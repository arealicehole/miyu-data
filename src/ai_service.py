import os
import requests
from .config import DEEPSEEK_API_KEY

class AIService:
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"
        self.max_tokens = 4096
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    async def get_closer_look(self, transcript: str, topic: str) -> str:
        system_prompt = "You are a highly detailed and thorough assistant analyzing meeting transcripts. Provide comprehensive, in-depth responses that cover all relevant aspects of the given topic. Include specific details, examples, and context from the transcript when applicable. Your goal is to give a complete and nuanced answer that leaves no stone unturned."
        user_content = f"Please go into more depth about '{topic}' and the conversation surrounding and related to '{topic}' from the transcript. Include relevant examples, context, and specific information from the transcript in your response.\n\nTranscript:\n{transcript}"
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "max_tokens": self.max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Error getting closer look: {str(e)}"

    async def generate_comprehensive_report(self, transcript: str) -> str:
        system_prompt = "You are a helpful assistant tasked with analyzing meeting transcripts and creating comprehensive reports."
        user_content = f"""Please analyze the following transcript and organize the information into these specific categories:

1. Main Conversation Topics: List and briefly summarize the main topics discussed in the meeting.
2. Content Ideas: Identify any content ideas or suggestions that were proposed during the meeting.
3. Action Items: List all action items or tasks that were assigned or mentioned, including who is responsible (if specified).
4. Notes for the AI: Highlight any specific instructions or notes that were intended for the AI system.
5. Decisions Made: Summarize any decisions that were reached during the meeting.
6. Critical Updates: List any important updates or changes that were announced.

For each category, provide detailed information and context from the transcript. If a category doesn't have any relevant information, indicate that it's not applicable.

Transcript:
{transcript}"""
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "max_tokens": self.max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Error generating comprehensive report: {str(e)}"

    async def get_response(self, transcript: str, query: str) -> str:
        system_prompt = "You are a highly detailed and thorough assistant analyzing meeting transcripts. Provide comprehensive, in-depth responses that cover all relevant aspects of the given task. Include specific details, examples, and context from the transcript when applicable. Your goal is to give a complete and nuanced answer that leaves no stone unturned. When asked to return a list, format it as a comma-separated list."
        user_content = f"Please provide a detailed and comprehensive response to the following task about the meeting transcript. Include relevant examples, context, and specific information from the transcript in your response.\n\nTranscript:\n{transcript}\n\nTask: {query}"
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "max_tokens": self.max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Error getting AI response: {str(e)}"
