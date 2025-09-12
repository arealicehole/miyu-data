#!/usr/bin/env python3
"""
Test OpenRouter integration without Pinecone
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_openrouter():
    from src.ai_service import AIService
    
    # Create AI service
    ai_service = AIService()
    print(f"AI Provider: {type(ai_service.provider).__name__}")
    
    # Test transcript analysis
    test_transcript = """
    John: Hey team, let's discuss the new feature rollout.
    Sarah: I think we should prioritize the mobile app first.
    John: Good idea. Let's set a deadline for next Friday.
    Sarah: Sounds good. I'll handle the UI updates.
    John: Perfect. AI, please note that Sarah is handling UI updates for the mobile app.
    """
    
    print("\nTesting OpenRouter with transcript analysis...")
    print("-" * 50)
    
    # Test closer look
    response = await ai_service.get_closer_look(test_transcript, "mobile app")
    print("Closer Look Response:", response[:200] + "...")
    
    print("\n✅ OpenRouter integration working!")

if __name__ == "__main__":
    asyncio.run(test_openrouter())