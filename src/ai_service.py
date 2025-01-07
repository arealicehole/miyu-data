import anthropic
from .config import ANTHROPIC_API_KEY

class AIService:
    def __init__(self):
        self.client = anthropic.Client(api_key=ANTHROPIC_API_KEY)
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 8192

    async def get_closer_look(self, transcript: str, topic: str) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system="You are a highly detailed and thorough assistant analyzing meeting transcripts. Provide comprehensive, in-depth responses that cover all relevant aspects of the given topic. Include specific details, examples, and context from the transcript when applicable. Your goal is to give a complete and nuanced answer that leaves no stone unturned.",
                messages=[{
                    "role": "user",
                    "content": f"Please go into more depth about '{topic}' and the conversation surrounding and related to '{topic}' from the transcript. Include relevant examples, context, and specific information from the transcript in your response.\n\nTranscript:\n{transcript}"
                }]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error getting closer look: {str(e)}"

    async def generate_comprehensive_report(self, transcript: str) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system="You are a helpful assistant tasked with analyzing meeting transcripts and creating comprehensive reports.",
                messages=[{
                    "role": "user",
                    "content": f"""Please analyze the following transcript and organize the information into these specific categories:

1. Main Conversation Topics: List and briefly summarize the main topics discussed in the meeting.
2. Content Ideas: Identify any content ideas or suggestions that were proposed during the meeting.
3. Action Items: List all action items or tasks that were assigned or mentioned, including who is responsible (if specified).
4. Notes for the AI: Highlight any specific instructions or notes that were intended for the AI system.
5. Decisions Made: Summarize any decisions that were reached during the meeting.
6. Critical Updates: List any important updates or changes that were announced.

For each category, provide detailed information and context from the transcript. If a category doesn't have any relevant information, indicate that it's not applicable.

Transcript:
{transcript}"""
                }]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error generating comprehensive report: {str(e)}"

    async def get_response(self, transcript: str, query: str) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system="You are a highly detailed and thorough assistant analyzing meeting transcripts. Provide comprehensive, in-depth responses that cover all relevant aspects of the given task. Include specific details, examples, and context from the transcript when applicable. Your goal is to give a complete and nuanced answer that leaves no stone unturned. When asked to return a list, format it as a comma-separated list.",
                messages=[{
                    "role": "user",
                    "content": f"Please provide a detailed and comprehensive response to the following task about the meeting transcript. Include relevant examples, context, and specific information from the transcript in your response.\n\nTranscript:\n{transcript}\n\nTask: {query}"
                }]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error getting AI response: {str(e)}"
