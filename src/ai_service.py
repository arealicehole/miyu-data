import os
import asyncio
from functools import wraps
from typing import Optional
from src.providers import get_ai_provider, AIProvider
from src.models.ai_models import AIRequest, AIResponse
import logging

logger = logging.getLogger(__name__)

def retry(max_retries=3, delay=1):
    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await f(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        raise
                    await asyncio.sleep(delay * (2 ** retries))
        return wrapper
    return decorator

class AIService:
    # Prompt constants
    CLOSER_LOOK_PROMPT = (
        "You are a highly detailed and thorough assistant analyzing meeting transcripts. "
        "Provide comprehensive, in-depth responses that cover all relevant aspects of the given topic. "
        "Include specific details, examples, and context from the transcript when applicable. "
        "Your goal is to give a complete and nuanced answer that leaves no stone unturned."
    )

    REPORT_PROMPT = (
        "You are a helpful assistant tasked with analyzing meeting transcripts and creating comprehensive reports."
    )

    GENERAL_PROMPT = (
        "You are a highly detailed and thorough assistant analyzing meeting transcripts. "
        "Provide comprehensive, in-depth responses that cover all relevant aspects of the given task. "
        "Include specific details, examples, and context from the transcript when applicable. "
        "Your goal is to give a complete and nuanced answer that leaves no stone unturned. "
        "When asked to return a list, format it as a comma-separated list."
    )

    def __init__(self, provider: Optional[AIProvider] = None):
        self.provider = provider or get_ai_provider()
        self.max_tokens = 4096
        # Get model override, strip whitespace and comments
        model_env = os.getenv('AI_MODEL', '').strip()
        # Remove inline comments if present
        if '#' in model_env:
            model_env = model_env.split('#')[0].strip()
        self.model = model_env if model_env else None
        # YOLO mode - no limits!
        self.yolo_mode = os.getenv('YOLO_MODE', 'false').lower() == 'true'
        if self.yolo_mode:
            logger.info("YOLO_MODE enabled - AI processing limits removed!")

    def _truncate_transcript(self, transcript: str, thinking: bool = False) -> str:
        """Truncate transcript to fit within token limits"""
        if self.yolo_mode:
            return transcript  # No truncation in YOLO mode
        # Use larger limit for thinking mode
        max_tokens = 32768 if thinking else self.max_tokens
        max_length = max_tokens * 4  # Approximate character count
        return transcript[:max_length] if len(transcript) > max_length else transcript

    def _format_closer_look_query(self, transcript: str, topic: str) -> str:
        """Format the query for closer look analysis"""
        return (
            f"Please go into more depth about '{topic}' and the conversation surrounding "
            f"and related to '{topic}' from the transcript. Include relevant examples, "
            f"context, and specific information from the transcript in your response.\n\n"
            f"Transcript:\n{transcript}"
        )

    def _format_report_query(self, transcript: str) -> str:
        """Format the query for comprehensive report generation"""
        return f"""Please analyze the following transcript and organize the information into these specific categories:

1. Main Conversation Topics: List and briefly summarize the main topics discussed in the meeting.
2. Content Ideas: Identify any content ideas or suggestions that were proposed during the meeting.
3. Action Items: List all action items or tasks that were assigned or mentioned, including who is responsible (if specified).
4. Notes for the AI: Highlight any specific instructions or notes that were intended for the AI system.
5. Decisions Made: Summarize any decisions that were reached during the meeting.
6. Critical Updates: List any important updates or changes that were announced.

For each category, provide detailed information and context from the transcript. If a category doesn't have any relevant information, indicate that it's not applicable.

Transcript:
{transcript}"""

    def _format_general_query(self, transcript: str, query: str) -> str:
        """Format a general query for AI response"""
        return (
            f"Please provide a detailed and comprehensive response to the following task "
            f"about the meeting transcript. Include relevant examples, context, and specific "
            f"information from the transcript in your response.\n\n"
            f"Transcript:\n{transcript}\n\nTask: {query}"
        )

    def _build_request(self, system_prompt: str, user_content: str, thinking: bool = False) -> AIRequest:
        """Build an AI request with the given prompts"""
        return AIRequest(
            model=self.model or "",  # Will use provider's default if empty
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            max_tokens=self.max_tokens,
            stream=False,
            thinking=thinking
        )

    async def _execute_request(self, request: AIRequest) -> str:
        """Execute an AI request and return the content"""
        try:
            response = await self.provider.chat_completion(request)
            return response.content
        except Exception as e:
            logger.error(f"AI request failed: {str(e)}")
            return f"Error processing AI request: {str(e)}"

    @retry(max_retries=3)
    async def get_closer_look(self, transcript: str, topic: str, thinking: bool = True) -> str:
        """Get a detailed analysis of a specific topic from the transcript.
        Defaults to thinking mode for deeper reasoning."""
        transcript = self._truncate_transcript(transcript, thinking)
        user_content = self._format_closer_look_query(transcript, topic)
        request = self._build_request(self.CLOSER_LOOK_PROMPT, user_content, thinking)
        return await self._execute_request(request)

    @retry(max_retries=3)
    async def generate_comprehensive_report(self, transcript: str, thinking: bool = False) -> str:
        """Generate a comprehensive report from the transcript.
        Defaults to non-thinking mode for faster structured extraction."""
        transcript = self._truncate_transcript(transcript, thinking)
        user_content = self._format_report_query(transcript)
        request = self._build_request(self.REPORT_PROMPT, user_content, thinking)
        return await self._execute_request(request)

    @retry(max_retries=3)
    async def get_response(self, transcript: str, query: str, thinking: bool = False) -> str:
        """Get a general AI response for a query about the transcript.
        Defaults to non-thinking mode for faster responses."""
        transcript = self._truncate_transcript(transcript, thinking)
        user_content = self._format_general_query(transcript, query)
        request = self._build_request(self.GENERAL_PROMPT, user_content, thinking)
        return await self._execute_request(request)
