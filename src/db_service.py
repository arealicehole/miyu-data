import os
from datetime import datetime
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict
from .ai_service import AIService

class DBService:
    # Constants
    VECTOR_DIMENSION = 3072  # Standard dimension for text embeddings
    CHUNK_SIZE = 30000  # Size for transcript chunks
    BATCH_SIZE = 100  # Size for Pinecone batch operations
    DEFAULT_TOP_K = 1000  # Default number of results to fetch
    
    def __init__(self):
        self.api_key = os.getenv('PINECONE_API_KEY')
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables.")
        
        self.pc = Pinecone(api_key=self.api_key)
        self.index_name = 'miyu-testa'
        
        # Create index if it doesn't exist
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=self.VECTOR_DIMENSION,
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
        
        self.index = self.pc.Index(self.index_name)
        # Pre-compute placeholder vector
        self.placeholder_vector = [0.1] * self.VECTOR_DIMENSION

    def parse_report_sections(self, report: str) -> dict:
        sections = {
            'conversation_topics': [],
            'content_ideas': [],
            'action_items': [],
            'notes_for_ai': [],
            'decisions_made': [],
            'critical_updates': []
        }
        
        current_section = None
        
        for line in report.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if "Main Conversation Topics:" in line:
                current_section = 'conversation_topics'
            elif "Content Ideas:" in line:
                current_section = 'content_ideas'
            elif "Action Items:" in line:
                current_section = 'action_items'
            elif "Notes for the AI:" in line:
                current_section = 'notes_for_ai'
            elif "Decisions Made:" in line:
                current_section = 'decisions_made'
            elif "Critical Updates:" in line:
                current_section = 'critical_updates'
            elif current_section and (line.startswith('-') or line.startswith('*') or line.startswith('•')):
                item = line.lstrip('-*• ').strip()
                if item:
                    sections[current_section].append(item)
        
        return sections

    async def save_transcript(self, channel_id: int, transcript: str, source: str = "channel", transcript_name: str = None):
        timestamp = datetime.now().isoformat()
        
        # Generate the report using AIService
        ai_service = AIService()
        report = await ai_service.generate_comprehensive_report(transcript)
        
        # Parse the report into sections
        sections = self.parse_report_sections(report)
        
        vectors = []
        
        # Split transcript into chunks
        chunks = [transcript[i:i+self.CHUNK_SIZE] for i in range(0, len(transcript), self.CHUNK_SIZE)]
        total_chunks = len(chunks)
        
        # Save chunks with all metadata
        for i, chunk in enumerate(chunks):
            vector_id = f"{channel_id}_{timestamp}_{i}"
            metadata = {
                'channel_id': str(channel_id),
                'timestamp': timestamp,
                'source': source,
                'type': 'transcript',
                'transcript_name': transcript_name or f"Transcript_{timestamp}",
                'chunk_index': i,
                'total_chunks': total_chunks,
                'text': chunk,
                'conversation_topics': sections['conversation_topics'],
                'content_ideas': sections['content_ideas'],
                'action_items': sections['action_items'],
                'notes_for_ai': sections['notes_for_ai'],
                'decisions_made': sections['decisions_made'],
                'critical_updates': sections['critical_updates']
            }
            vectors.append((vector_id, self.placeholder_vector, metadata))
        
        # Upsert to Pinecone in batches
        for i in range(0, len(vectors), self.BATCH_SIZE):
            batch = vectors[i:i+self.BATCH_SIZE]
            self.index.upsert(vectors=batch)
        
        return f"{channel_id}_{timestamp}"

    async def get_channel_transcript(self, channel_id: int, transcript_name: str = None) -> str:
        # Build filter dict
        filter_dict = {'channel_id': str(channel_id)}
        if transcript_name:
            filter_dict['transcript_name'] = transcript_name
            
        query_response = self.index.query(
            vector=self.placeholder_vector,
            filter=filter_dict,
            top_k=self.DEFAULT_TOP_K,
            include_metadata=True
        )
        
        if query_response.matches:
            # Sort chunks by their index
            sorted_chunks = sorted(query_response.matches, key=lambda x: x.metadata['chunk_index'])
            # Reconstruct the transcript
            return ''.join(chunk.metadata['text'] for chunk in sorted_chunks)
        return ''

    async def delete_transcript(self, channel_id: int):
        # Delete all vectors associated with this channel_id
        self.index.delete(filter={'channel_id': str(channel_id)})

    async def list_transcripts(self, channel_id: int = None) -> List[Dict[str, str]]:
        # Query for all transcripts, optionally filtered by channel_id
        filter_dict = {'channel_id': str(channel_id), 'type': 'transcript'} if channel_id else {'type': 'transcript'}
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
                    'transcript_name': metadata.get('transcript_name', f"Transcript_{metadata['timestamp']}")
                }
        
        return list(transcripts.values())

    async def get_section_items(self, channel_id: int, section_type: str) -> List[str]:
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
