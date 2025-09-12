"""
Mock DBService for testing without Pinecone
Stores transcripts in memory temporarily
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
from src.models.transcript import TranscriptSections
from src.ai_service import AIService

logger = logging.getLogger(__name__)

class DBService:
    """Mock database service that stores data in memory"""
    
    def __init__(self):
        logger.info("Using MOCK DBService - data stored in memory only!")
        self.transcripts = {}
        self.sections = {}
        
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
            
            for header, section_name in section_mapping.items():
                if header in line:
                    current_section = section_name
                    break
            
            if current_section and line_stripped.startswith(('-', '*', '•')):
                item = line_stripped.lstrip('-*• ').strip()
                if item:
                    getattr(sections, current_section).append(item)
        
        return sections
    
    async def save_transcript(self, channel_id: int, transcript: str, 
                            source: str = "channel", transcript_name: Optional[str] = None) -> str:
        """Save transcript to memory"""
        timestamp = datetime.now().isoformat()
        
        # Generate report
        ai_service = AIService()
        report = await ai_service.generate_comprehensive_report(transcript)
        sections = self.parse_report_sections(report)
        
        # Store in memory
        self.transcripts[channel_id] = transcript
        self.sections[channel_id] = {
            'conversation_topics': sections.conversation_topics,
            'content_ideas': sections.content_ideas,
            'action_items': sections.action_items,
            'notes_for_ai': sections.notes_for_ai,
            'decisions_made': sections.decisions_made,
            'critical_updates': sections.critical_updates
        }
        
        logger.info(f"Transcript saved for channel {channel_id}")
        return f"{channel_id}_{timestamp}"
    
    async def get_channel_transcript(self, channel_id: int, 
                                    transcript_name: Optional[str] = None) -> str:
        """Get transcript from memory"""
        return self.transcripts.get(channel_id, '')
    
    async def get_section_items(self, channel_id: int, section_type: str) -> List[str]:
        """Get section items from memory"""
        if channel_id in self.sections:
            return self.sections[channel_id].get(section_type, [])
        return []
    
    async def get_all_sections(self, channel_id: int) -> Dict[str, List[str]]:
        """Get all sections from memory"""
        return self.sections.get(channel_id, {
            'conversation_topics': [],
            'content_ideas': [],
            'action_items': [],
            'notes_for_ai': [],
            'decisions_made': [],
            'critical_updates': []
        })
    
    async def delete_transcript(self, channel_id: int) -> None:
        """Delete transcript from memory"""
        self.transcripts.pop(channel_id, None)
        self.sections.pop(channel_id, None)
    
    async def list_transcripts(self, channel_id: Optional[int] = None) -> List[Dict[str, str]]:
        """List transcripts in memory"""
        if channel_id:
            if channel_id in self.transcripts:
                return [{'channel_id': str(channel_id), 'source': 'memory'}]
            return []
        return [{'channel_id': str(cid), 'source': 'memory'} 
                for cid in self.transcripts.keys()]