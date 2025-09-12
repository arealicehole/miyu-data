import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
import asyncio

logger = logging.getLogger(__name__)

class ConversationManager:
    """Manages conversation history and context for natural chat interactions"""
    
    def __init__(self, max_history_messages: int = 10, context_timeout_minutes: int = 30):
        """
        Initialize conversation manager
        
        Args:
            max_history_messages: Maximum number of messages to keep in history per channel
            context_timeout_minutes: Minutes before conversation context resets
        """
        self.max_history = max_history_messages
        self.context_timeout = timedelta(minutes=context_timeout_minutes)
        
        # Store conversation history per channel
        self.conversations = defaultdict(lambda: {
            'messages': deque(maxlen=max_history_messages),
            'last_activity': datetime.now(),
            'context_mode': 'chat',  # 'chat' or 'search'
            'active_topics': []
        })
        
    def add_message(self, channel_id: int, role: str, content: str, message_id: Optional[int] = None):
        """Add a message to conversation history"""
        conv = self.conversations[channel_id]
        
        # Check if conversation has timed out
        if datetime.now() - conv['last_activity'] > self.context_timeout:
            # Reset conversation
            conv['messages'].clear()
            conv['context_mode'] = 'chat'
            conv['active_topics'] = []
            logger.info(f"Conversation reset for channel {channel_id} due to timeout")
        
        # Add message
        conv['messages'].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now(),
            'message_id': message_id
        })
        conv['last_activity'] = datetime.now()
        
    def get_conversation_history(self, channel_id: int) -> List[Dict]:
        """Get recent conversation history for a channel"""
        conv = self.conversations[channel_id]
        
        # Check timeout
        if datetime.now() - conv['last_activity'] > self.context_timeout:
            return []
        
        return list(conv['messages'])
    
    def should_search_transcripts(self, message_content: str, channel_id: int) -> Tuple[bool, Optional[str]]:
        """
        Determine if the message requires searching transcripts
        
        Returns:
            (should_search, search_query) - whether to search and what query to use
        """
        content_lower = message_content.lower()
        
        # Keywords that indicate need for transcript search
        search_triggers = {
            'explicit': [
                'search for', 'find', 'look up', 'look for', 'locate',
                'what did we discuss about', 'when did we talk about',
                'remember when', 'recall', 'from the meeting', 'in the transcript'
            ],
            'implicit': [
                'what was decided', 'what were the action items',
                'who said', 'did anyone mention', 'was there discussion about',
                'what was the conclusion', 'what did we agree on'
            ],
            'temporal': [
                'yesterday', 'last week', 'last meeting', 'previously',
                'earlier', 'before', 'in the past'
            ]
        }
        
        # Check for explicit search requests
        for trigger in search_triggers['explicit']:
            if trigger in content_lower:
                # Extract the search topic after the trigger phrase
                query = self._extract_search_query(message_content, trigger)
                return True, query
        
        # Check for implicit search needs
        for trigger in search_triggers['implicit']:
            if trigger in content_lower:
                return True, message_content
        
        # Check for temporal references (might need transcript context)
        for trigger in search_triggers['temporal']:
            if trigger in content_lower:
                return True, message_content
        
        # Check conversation context
        conv = self.conversations[channel_id]
        
        # If recent messages referenced searching or specific topics from transcripts
        recent_messages = list(conv['messages'])[-3:]  # Last 3 messages
        for msg in recent_messages:
            if 'search' in msg.get('content', '').lower() or 'transcript' in msg.get('content', '').lower():
                # Continue in search context
                return True, message_content
        
        # Check if the message is asking for clarification about active topics
        if any(topic in content_lower for topic in conv['active_topics']):
            return True, message_content
        
        # Default to conversational response without search
        return False, None
    
    def _extract_search_query(self, message: str, trigger: str) -> str:
        """Extract the search query from a message after a trigger phrase"""
        message_lower = message.lower()
        trigger_pos = message_lower.find(trigger)
        
        if trigger_pos != -1:
            # Get everything after the trigger
            query_part = message[trigger_pos + len(trigger):].strip()
            
            # Remove common filler words at the start
            filler_words = ['the', 'a', 'an', 'about', 'for', 'regarding']
            words = query_part.split()
            
            if words and words[0].lower() in filler_words:
                query_part = ' '.join(words[1:])
            
            # Remove trailing punctuation
            query_part = query_part.rstrip('?.,!')
            
            return query_part if query_part else message
        
        return message
    
    def format_conversation_context(self, channel_id: int) -> str:
        """Format conversation history for AI context"""
        history = self.get_conversation_history(channel_id)
        
        if not history:
            return ""
        
        formatted = []
        for msg in history:
            role = msg['role']
            content = msg['content']
            
            # Truncate very long messages
            if len(content) > 500:
                content = content[:500] + "..."
            
            formatted.append(f"{role}: {content}")
        
        return "\n".join(formatted)
    
    def update_active_topics(self, channel_id: int, topics: List[str]):
        """Update the active topics being discussed in a channel"""
        conv = self.conversations[channel_id]
        conv['active_topics'] = topics[-5:]  # Keep last 5 topics
    
    def get_context_summary(self, channel_id: int) -> Dict:
        """Get a summary of the current conversation context"""
        conv = self.conversations[channel_id]
        history = self.get_conversation_history(channel_id)
        
        return {
            'message_count': len(history),
            'context_mode': conv['context_mode'],
            'active_topics': conv['active_topics'],
            'time_since_last': (datetime.now() - conv['last_activity']).seconds if conv['last_activity'] else None,
            'has_context': len(history) > 0
        }

class ConversationalRAGHandler:
    """Handles conversational interactions with optional RAG search"""
    
    def __init__(self, ai_service, db_service, query_processor):
        self.ai_service = ai_service
        self.db_service = db_service
        self.query_processor = query_processor
        self.conversation_manager = ConversationManager()
        
    async def handle_mention(self, message, channel_id: int) -> str:
        """
        Handle an @ mention with conversational context and optional RAG
        
        Args:
            message: Discord message object
            channel_id: Channel ID
            
        Returns:
            Response text to send
        """
        user_input = message.content
        author_name = message.author.name
        
        # Add user message to conversation history
        self.conversation_manager.add_message(
            channel_id, 
            f"User ({author_name})",
            user_input,
            message.id
        )
        
        # Determine if we need to search transcripts
        should_search, search_query = self.conversation_manager.should_search_transcripts(
            user_input, 
            channel_id
        )
        
        # Get conversation history
        conv_history = self.conversation_manager.format_conversation_context(channel_id)
        
        # Build context for AI
        context_parts = []
        
        if conv_history:
            context_parts.append("=== Recent Conversation ===")
            context_parts.append(conv_history)
            context_parts.append("")
        
        # Perform RAG search if needed
        search_results = []
        if should_search and search_query:
            logger.info(f"Performing RAG search for: {search_query}")
            
            try:
                # Use the query processor for optimized search
                search_results = await self.query_processor.search_optimized(
                    query=search_query,
                    channel_id=channel_id,
                    max_results=5
                )
                
                if search_results:
                    context_parts.append("=== Relevant Transcript Context ===")
                    for i, result in enumerate(search_results[:3], 1):  # Top 3 results
                        context_parts.append(f"[Match {i} - Relevance: {result['score']:.2f}]")
                        context_parts.append(result['text'])
                        context_parts.append("")
                    
                    # Update active topics based on search
                    topics = [search_query] + [r.get('transcript_name', '') for r in search_results[:2]]
                    self.conversation_manager.update_active_topics(channel_id, topics)
                    
            except Exception as e:
                logger.error(f"RAG search failed: {e}")
                # Continue without search results
        
        # Combine all context
        full_context = "\n".join(context_parts) if context_parts else ""
        
        # Generate response
        if should_search and search_results:
            # Response with transcript context
            prompt = f"""You are a helpful Discord bot assistant. You have access to both the recent conversation history and relevant transcript excerpts.

{full_context}

Current User ({author_name}): {user_input}

Please provide a helpful response that:
1. Answers the user's question using the transcript context when relevant
2. Maintains conversational flow from the chat history
3. Is concise and friendly
4. Cites specific information from transcripts when used

Response:"""
        else:
            # Pure conversational response
            prompt = f"""You are a helpful Discord bot assistant engaged in a conversation.

{full_context}

Current User ({author_name}): {user_input}

Please provide a helpful, friendly, and conversational response. Be concise but informative.

Response:"""
        
        # Get AI response
        response = await self.ai_service.get_response("", prompt)  # Empty transcript since we provide context
        
        # Add assistant response to conversation history
        self.conversation_manager.add_message(
            channel_id,
            "Assistant",
            response
        )
        
        # Log context summary for debugging
        context_summary = self.conversation_manager.get_context_summary(channel_id)
        logger.info(f"Conversation context: {context_summary}")
        
        return response