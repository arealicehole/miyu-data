from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class TranscriptChunk(BaseModel):
    channel_id: str
    timestamp: datetime
    source: Literal["channel", "file"]
    transcript_name: str
    chunk_index: int
    total_chunks: int
    text: str

class TranscriptSections(BaseModel):
    conversation_topics: List[str] = Field(default_factory=list)
    content_ideas: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    notes_for_ai: List[str] = Field(default_factory=list)
    decisions_made: List[str] = Field(default_factory=list)
    critical_updates: List[str] = Field(default_factory=list)

class TranscriptMetadata(BaseModel):
    channel_id: str
    timestamp: datetime
    source: Literal["channel", "file"]
    type: Literal["transcript"] = "transcript"
    transcript_name: str
    chunk_index: int
    total_chunks: int
    text: str
    sections: TranscriptSections