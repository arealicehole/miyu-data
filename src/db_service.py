import os
import asyncio
from datetime import datetime
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Optional, Tuple
from src.models.transcript import TranscriptMetadata, TranscriptSections
from src.ai_service import AIService
from src.providers.embeddings import get_embedding_provider
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def retry(max_retries=3, delay=1):
    """Decorator to retry a function with exponential backoff"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        raise
                    wait = delay * (2 ** (retries - 1))
                    logger.warning(f"Retry {retries}/{max_retries} after {wait}s: {str(e)}")
                    await asyncio.sleep(wait)
        return wrapper
    return decorator

class DBService:
    # Constants
    VECTOR_DIMENSION = 3072  # Standard dimension for text embeddings
    CHUNK_SIZE = 1500  # Optimal size for RAG (roughly 300-400 tokens)
    CHUNK_OVERLAP = 200  # 13% overlap for context preservation
    BATCH_SIZE = 50  # Reduced batch size for better reliability
    DEFAULT_TOP_K = 1000  # Default number of results to fetch
    
    def __init__(self):
        self.api_key = os.getenv('PINECONE_API_KEY')
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables.")
        
        # Configure Pinecone
        self.pc = Pinecone(api_key=self.api_key)
        self.index_name = 'miyu-testa'
        
        # Connect to index
        try:
            # Check if index exists
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            if self.index_name not in existing_indexes:
                logger.info(f"Index {self.index_name} not found, creating...")
                self._create_index()
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to connect to Pinecone: {e}")
            raise
        # Pre-compute placeholder vector
        self.placeholder_vector = [0.1] * self.VECTOR_DIMENSION
        
        # Initialize embedding provider
        try:
            self.embedding_provider = get_embedding_provider()
            logger.info("Initialized embedding provider")
        except Exception as e:
            logger.warning(f"Failed to initialize embedding provider: {e}")
            logger.warning("Falling back to placeholder vectors")
            self.embedding_provider = None
    
    def _create_index(self) -> None:
        """Create Pinecone index with configured settings"""
        self.pc.create_index(
            name=self.index_name,
            dimension=self.VECTOR_DIMENSION,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
    
    def _parse_section_line(self, line: str) -> Optional[str]:
        """Parse a single line for section items"""
        line = line.strip()
        if not line:
            return None
        if line.startswith(('-', '*', '•')):
            item = line.lstrip('-*• ').strip()
            return item if item else None
        return None
    
    def parse_report_sections(self, report: str) -> TranscriptSections:
        """Parse report text into structured sections"""
        sections = TranscriptSections()
        current_section = None
        
        section_mapping = {
            "Main Conversation Topics:": 'conversation_topics',
            "Content Ideas:": 'content_ideas',
            "Action Items:": 'action_items',
            "Notes for the AI:": 'notes_for_ai',
            "Decisions Made:": 'decisions_made',
            "Critical Updates:": 'critical_updates'
        }
        
        for line in report.split('\n'):
            line_stripped = line.strip()
            
            # Check if line is a section header
            for header, section_name in section_mapping.items():
                if header in line:
                    current_section = section_name
                    break
            
            # Parse section items
            if current_section:
                item = self._parse_section_line(line)
                if item:
                    getattr(sections, current_section).append(item)
        
        return sections
    
    def _chunk_transcript(self, transcript: str) -> List[str]:
        """Split transcript into semantically meaningful chunks with overlap"""
        if not transcript:
            return []
        
        chunks = []
        start = 0
        
        while start < len(transcript):
            # Calculate end position
            end = min(start + self.CHUNK_SIZE, len(transcript))
            
            # If not at the beginning and not the last chunk, try to break at a sentence
            if start > 0 and end < len(transcript):
                # Look for sentence boundaries near the end
                for delimiter in ['. ', '! ', '? ', '\n\n', '\n']:
                    last_delimiter = transcript.rfind(delimiter, start + self.CHUNK_SIZE - 100, end)
                    if last_delimiter != -1:
                        end = last_delimiter + len(delimiter)
                        break
            
            # Add the chunk
            chunk = transcript[start:end].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
            
            # Move start position with overlap
            if end >= len(transcript):
                break
            start = end - self.CHUNK_OVERLAP
        
        return chunks
    
    async def _prepare_metadata(
        self, 
        channel_id: int, 
        transcript: str, 
        source: str, 
        transcript_name: Optional[str]
    ) -> Tuple[TranscriptMetadata, TranscriptSections]:
        """Prepare metadata and generate report sections"""
        timestamp = datetime.now()
        
        # Generate the report using AIService
        ai_service = AIService()
        report = await ai_service.generate_comprehensive_report(transcript)
        
        # Parse the report into sections
        sections = self.parse_report_sections(report)
        
        # Create base metadata (will be customized per chunk)
        base_metadata = TranscriptMetadata(
            channel_id=str(channel_id),
            timestamp=timestamp,
            source=source,
            transcript_name=transcript_name or f"Transcript_{timestamp.isoformat()}",
            chunk_index=0,  # Will be updated per chunk
            total_chunks=0,  # Will be updated
            text="",  # Will be updated per chunk
            sections=sections
        )
        
        return base_metadata, sections
    
    async def _create_vectors(
        self, 
        chunks: List[str], 
        base_metadata: TranscriptMetadata,
        sections: TranscriptSections
    ) -> List[Tuple[str, List[float], Dict]]:
        """Create vector representations for transcript chunks using real embeddings"""
        vectors = []
        total_chunks = len(chunks)
        
        # Generate embeddings for all chunks
        if self.embedding_provider:
            try:
                logger.info(f"Generating embeddings for {total_chunks} chunks...")
                embeddings = await self.embedding_provider.create_embeddings(chunks)
                logger.info(f"Successfully generated {len(embeddings)} embeddings")
            except Exception as e:
                logger.error(f"Failed to generate embeddings: {e}")
                logger.warning("Falling back to placeholder vectors")
                embeddings = [self.placeholder_vector] * total_chunks
        else:
            embeddings = [self.placeholder_vector] * total_chunks
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector_id = f"{base_metadata.channel_id}_{base_metadata.timestamp.isoformat()}_{i}"
            
            # Create metadata dict for this chunk
            metadata = {
                'channel_id': base_metadata.channel_id,
                'timestamp': base_metadata.timestamp.isoformat(),
                'source': base_metadata.source,
                'type': base_metadata.type,
                'transcript_name': base_metadata.transcript_name,
                'chunk_index': i,
                'total_chunks': total_chunks,
                'text': chunk,
                'conversation_topics': sections.conversation_topics,
                'content_ideas': sections.content_ideas,
                'action_items': sections.action_items,
                'notes_for_ai': sections.notes_for_ai,
                'decisions_made': sections.decisions_made,
                'critical_updates': sections.critical_updates
            }
            
            vectors.append((vector_id, embedding, metadata))
        
        return vectors
    
    @retry(max_retries=3, delay=1)
    async def _async_upsert(self, batch: List) -> None:
        """Async wrapper for Pinecone upsert operation"""
        await asyncio.to_thread(self.index.upsert, vectors=batch)
    
    async def _upsert_vectors(self, vectors: List) -> None:
        """Batch upsert vectors to Pinecone"""
        try:
            for i in range(0, len(vectors), self.BATCH_SIZE):
                batch = vectors[i:i + self.BATCH_SIZE]
                await self._async_upsert(batch)
        except Exception as e:
            logger.error(f"Failed to upsert vectors: {str(e)}")
            raise RuntimeError(f"Failed to save transcript: {str(e)}")
    
    async def save_transcript(
        self, 
        channel_id: int, 
        transcript: str, 
        source: str = "channel", 
        transcript_name: Optional[str] = None
    ) -> str:
        """Save transcript to vector database with metadata"""
        # Prepare metadata and sections
        base_metadata, sections = await self._prepare_metadata(
            channel_id, transcript, source, transcript_name
        )
        
        # Chunk the transcript
        chunks = self._chunk_transcript(transcript)
        
        # Create vectors with real embeddings
        vectors = await self._create_vectors(chunks, base_metadata, sections)
        
        # Upsert to Pinecone
        await self._upsert_vectors(vectors)
        
        return f"{channel_id}_{base_metadata.timestamp.isoformat()}"
    
    def _build_channel_filter(
        self, 
        channel_id: int, 
        transcript_name: Optional[str] = None
    ) -> Dict:
        """Build filter dict for channel queries"""
        filter_dict = {'channel_id': str(channel_id)}
        if transcript_name:
            filter_dict['transcript_name'] = transcript_name
        return filter_dict
    
    async def _get_query_vector(self, query: Optional[str] = None) -> List[float]:
        """Generate query vector for semantic search"""
        if query and self.embedding_provider:
            try:
                return await self.embedding_provider.create_embedding(query)
            except Exception as e:
                logger.warning(f"Failed to generate query embedding: {e}")
                logger.warning("Using placeholder vector for query")
        
        return self.placeholder_vector
    
    async def get_channel_transcript(
        self, 
        channel_id: int, 
        transcript_name: Optional[str] = None
    ) -> str:
        """Retrieve and reconstruct transcript from database"""
        filter_dict = self._build_channel_filter(channel_id, transcript_name)
        
        query_response = self.index.query(
            vector=self.placeholder_vector,
            filter=filter_dict,
            top_k=self.DEFAULT_TOP_K,
            include_metadata=True
        )
        
        if not query_response.matches:
            return ''
        
        # Sort chunks by their index and reconstruct
        sorted_chunks = sorted(
            query_response.matches, 
            key=lambda x: x.metadata['chunk_index']
        )
        return ''.join(chunk.metadata['text'] for chunk in sorted_chunks)
    
    async def search_transcripts(
        self, 
        query: str, 
        channel_id: int, 
        top_k: int = 5,
        min_score: float = 0.7
    ) -> List[Dict]:
        """Semantic search for relevant transcript chunks"""
        filter_dict = self._build_channel_filter(channel_id)
        query_vector = await self._get_query_vector(query)
        
        query_response = self.index.query(
            vector=query_vector,
            filter=filter_dict,
            top_k=top_k,
            include_metadata=True
        )
        
        results = []
        for match in query_response.matches:
            if match.score >= min_score:
                results.append({
                    'text': match.metadata['text'],
                    'score': match.score,
                    'chunk_index': match.metadata['chunk_index'],
                    'timestamp': match.metadata['timestamp'],
                    'transcript_name': match.metadata.get('transcript_name', 'Unknown')
                })
        
        return results
    
    async def delete_transcript(self, channel_id: int) -> None:
        """Delete all vectors associated with a channel"""
        self.index.delete(filter={'channel_id': str(channel_id)})
    
    async def list_transcripts(
        self, 
        channel_id: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """List all transcripts, optionally filtered by channel"""
        filter_dict = (
            {'channel_id': str(channel_id), 'type': 'transcript'} 
            if channel_id 
            else {'type': 'transcript'}
        )
        
        query_response = self.index.query(
            vector=self.placeholder_vector,
            filter=filter_dict,
            top_k=self.DEFAULT_TOP_K,
            include_metadata=True
        )
        
        transcripts = {}
        for match in query_response.matches:
            metadata = match.metadata
            transcript_id = f"{metadata['channel_id']}_{metadata['timestamp']}"
            
            if transcript_id not in transcripts:
                transcripts[transcript_id] = {
                    'channel_id': metadata['channel_id'],
                    'timestamp': metadata['timestamp'],
                    'source': metadata['source'],
                    'total_chunks': metadata['total_chunks'],
                    'transcript_name': metadata.get(
                        'transcript_name', 
                        f"Transcript_{metadata['timestamp']}"
                    )
                }
        
        return list(transcripts.values())
    
    async def get_section_items(
        self, 
        channel_id: int, 
        section_type: str
    ) -> List[str]:
        """
        Retrieve all items of a specific section type for a channel.
        section_type can be: conversation_topics, content_ideas, action_items, 
        notes_for_ai, decisions_made, or critical_updates
        """
        query_response = self.index.query(
            vector=self.placeholder_vector,
            filter={
                'channel_id': str(channel_id),
                'type': 'transcript',
                'chunk_index': 0  # Only need first chunk since all chunks have same sections
            },
            top_k=1,
            include_metadata=True
        )
        
        if query_response.matches:
            return query_response.matches[0].metadata.get(section_type, [])
        return []
    
    async def get_all_sections(self, channel_id: int) -> Dict[str, List[str]]:
        """
        Retrieve all section items for a channel, organized by section type
        """
        query_response = self.index.query(
            vector=self.placeholder_vector,
            filter={
                'channel_id': str(channel_id),
                'type': 'transcript',
                'chunk_index': 0  # Only need first chunk since all chunks have same sections
            },
            top_k=1,
            include_metadata=True
        )
        
        if query_response.matches:
            metadata = query_response.matches[0].metadata
            return {
                'conversation_topics': metadata.get('conversation_topics', []),
                'content_ideas': metadata.get('content_ideas', []),
                'action_items': metadata.get('action_items', []),
                'notes_for_ai': metadata.get('notes_for_ai', []),
                'decisions_made': metadata.get('decisions_made', []),
                'critical_updates': metadata.get('critical_updates', [])
            }
        
        return {
            'conversation_topics': [],
            'content_ideas': [],
            'action_items': [],
            'notes_for_ai': [],
            'decisions_made': [],
            'critical_updates': []
        }