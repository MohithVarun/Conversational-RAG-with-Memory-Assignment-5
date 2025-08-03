import json
import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import hashlib
import numpy as np
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedMemoryManager:
    """
    Advanced memory manager with multi-session conversation memory,
    long-term storage, context window management, and relevance scoring.
    """
    
    def __init__(self, memory_db_path: str = "./advanced_memory_db"):
        self.memory_db_path = memory_db_path
        os.makedirs(memory_db_path, exist_ok=True)
        
        # Memory storage
        self.session_memories = {}  # Current session memories
        self.long_term_memories = []  # Persistent long-term memories
        self.user_profiles = {}  # User personality profiles
        self.conversation_contexts = {}  # Context window management
        
        # Memory configuration
        self.max_context_window = 10  # Maximum messages in context window
        self.memory_retention_days = 30  # How long to keep memories
        self.relevance_threshold = 0.7  # Minimum relevance score
        
        # Load existing memories
        self._load_memories()
    
    def _load_memories(self):
        """Load existing memories from disk."""
        try:
            # Load long-term memories
            lt_memory_file = os.path.join(self.memory_db_path, "long_term_memories.pkl")
            if os.path.exists(lt_memory_file):
                with open(lt_memory_file, 'rb') as f:
                    self.long_term_memories = pickle.load(f)
            
            # Load user profiles
            profiles_file = os.path.join(self.memory_db_path, "user_profiles.pkl")
            if os.path.exists(profiles_file):
                with open(profiles_file, 'rb') as f:
                    self.user_profiles = pickle.load(f)
                    
            logger.info(f"Loaded {len(self.long_term_memories)} long-term memories and {len(self.user_profiles)} user profiles")
        except Exception as e:
            logger.error(f"Error loading memories: {e}")
    
    def _save_memories(self):
        """Save memories to disk with privacy considerations."""
        try:
            # Save long-term memories
            lt_memory_file = os.path.join(self.memory_db_path, "long_term_memories.pkl")
            with open(lt_memory_file, 'wb') as f:
                pickle.dump(self.long_term_memories, f)
            
            # Save user profiles
            profiles_file = os.path.join(self.memory_db_path, "user_profiles.pkl")
            with open(profiles_file, 'wb') as f:
                pickle.dump(self.user_profiles, f)
                
            logger.info("Memories saved successfully")
        except Exception as e:
            logger.error(f"Error saving memories: {e}")
    
    def add_session_memory(self, session_id: str, user_message: str, 
                          assistant_response: str, context: Dict = None,
                          user_id: str = None):
        """Add a conversation turn to session memory with context tracking."""
        timestamp = datetime.now()
        
        # Create memory entry
        memory_entry = {
            "session_id": session_id,
            "user_id": user_id or "anonymous",
            "user_message": user_message,
            "assistant_response": assistant_response,
            "timestamp": timestamp.isoformat(),
            "context": context or {},
            "memory_type": "session",
            "relevance_score": self._calculate_relevance_score(user_message),
            "keywords": self._extract_keywords(user_message),
            "sentiment": self._analyze_sentiment(user_message)
        }
        
        # Add to session memories
        if session_id not in self.session_memories:
            self.session_memories[session_id] = []
        self.session_memories[session_id].append(memory_entry)
        
        # Update conversation context
        self._update_conversation_context(session_id, memory_entry)
        
        # Update user profile
        if user_id:
            self._update_user_profile(user_id, memory_entry)
        
        # Check if memory should be promoted to long-term
        if self._should_promote_to_long_term(memory_entry):
            self._promote_to_long_term(memory_entry)
        
        # Clean up old memories
        self._cleanup_old_memories()
        
        logger.info(f"Added session memory for session {session_id}")
    
    def get_session_context(self, session_id: str, limit: int = None) -> List[Dict]:
        """Retrieve recent session context with relevance scoring."""
        if session_id not in self.session_memories:
            return []
        
        memories = self.session_memories[session_id]
        limit = limit or self.max_context_window
        
        # Sort by relevance and recency
        sorted_memories = sorted(
            memories,
            key=lambda x: (x.get('relevance_score', 0), x['timestamp']),
            reverse=True
        )
        
        return sorted_memories[:limit]
    
    def get_relevant_long_term_memories(self, query: str, user_id: str = None, 
                                      limit: int = 5) -> List[Dict]:
        """Retrieve relevant long-term memories using similarity scoring."""
        query_keywords = self._extract_keywords(query)
        query_relevance = self._calculate_relevance_score(query)
        
        relevant_memories = []
        
        for memory in self.long_term_memories:
            # Skip if user_id doesn't match (privacy consideration)
            if user_id and memory.get('user_id') != user_id:
                continue
            
            # Calculate similarity score
            keyword_overlap = len(set(query_keywords) & set(memory.get('keywords', [])))
            relevance_similarity = 1 - abs(query_relevance - memory.get('relevance_score', 0))
            
            # Combined similarity score
            similarity_score = (keyword_overlap * 0.6) + (relevance_similarity * 0.4)
            
            if similarity_score >= self.relevance_threshold:
                memory_copy = memory.copy()
                memory_copy['similarity_score'] = similarity_score
                relevant_memories.append(memory_copy)
        
        # Sort by similarity and return top results
        relevant_memories.sort(key=lambda x: x['similarity_score'], reverse=True)
        return relevant_memories[:limit]
    
    def get_user_profile(self, user_id: str) -> Dict:
        """Get user personality profile for personalized responses."""
        if user_id not in self.user_profiles:
            return self._create_default_profile()
        
        profile = self.user_profiles[user_id]
        
        # Calculate personality traits based on conversation history
        profile['personality_traits'] = self._analyze_personality(user_id)
        profile['conversation_style'] = self._analyze_conversation_style(user_id)
        profile['health_interests'] = self._analyze_health_interests(user_id)
        
        return profile
    
    def get_conversation_summary(self, session_id: str) -> Dict:
        """Generate conversation summary for context window management."""
        if session_id not in self.session_memories:
            return {}
        
        memories = self.session_memories[session_id]
        
        # Extract key topics and themes
        topics = defaultdict(int)
        sentiments = []
        keywords = set()
        
        for memory in memories:
            # Count topics
            for keyword in memory.get('keywords', []):
                topics[keyword] += 1
                keywords.add(keyword)
            
            # Collect sentiments
            sentiments.append(memory.get('sentiment', 'neutral'))
        
        # Calculate conversation metrics
        avg_sentiment = sum(1 if s == 'positive' else -1 if s == 'negative' else 0 
                           for s in sentiments) / len(sentiments) if sentiments else 0
        
        return {
            "session_id": session_id,
            "total_turns": len(memories),
            "main_topics": sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5],
            "average_sentiment": avg_sentiment,
            "unique_keywords": len(keywords),
            "conversation_duration": self._calculate_duration(memories),
            "last_updated": datetime.now().isoformat()
        }
    
    def _calculate_relevance_score(self, text: str) -> float:
        """Calculate relevance score based on content analysis."""
        # Simple relevance scoring based on content length and keyword density
        words = text.lower().split()
        health_keywords = ['health', 'medical', 'doctor', 'symptom', 'treatment', 
                          'medicine', 'pain', 'fever', 'cough', 'headache']
        
        keyword_count = sum(1 for word in words if word in health_keywords)
        relevance = min(1.0, (keyword_count / len(words)) * 2 + (len(words) / 50))
        
        return relevance
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for memory indexing."""
        # Simple keyword extraction
        words = text.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords[:10]  # Limit to top 10 keywords
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of user message."""
        positive_words = {'good', 'great', 'excellent', 'happy', 'better', 'improved', 'helpful'}
        negative_words = {'bad', 'terrible', 'pain', 'hurt', 'sick', 'worried', 'anxious', 'depressed'}
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _update_conversation_context(self, session_id: str, memory_entry: Dict):
        """Update conversation context for session continuity."""
        if session_id not in self.conversation_contexts:
            self.conversation_contexts[session_id] = {
                'current_topic': '',
                'conversation_flow': [],
                'user_preferences': set(),
                'assistant_responses': []
            }
        
        context = self.conversation_contexts[session_id]
        
        # Update current topic based on keywords
        keywords = memory_entry.get('keywords', [])
        if keywords:
            context['current_topic'] = keywords[0]
        
        # Track conversation flow
        context['conversation_flow'].append({
            'timestamp': memory_entry['timestamp'],
            'user_message': memory_entry['user_message'][:50] + '...',
            'sentiment': memory_entry.get('sentiment', 'neutral')
        })
        
        # Limit conversation flow history
        if len(context['conversation_flow']) > 20:
            context['conversation_flow'] = context['conversation_flow'][-20:]
    
    def _update_user_profile(self, user_id: str, memory_entry: Dict):
        """Update user profile for personalized responses."""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = self._create_default_profile()
        
        profile = self.user_profiles[user_id]
        
        # Update conversation statistics
        profile['total_conversations'] += 1
        profile['total_messages'] += 1
        
        # Update health interests
        health_keywords = memory_entry.get('keywords', [])
        for keyword in health_keywords:
            if keyword in profile['health_interests']:
                profile['health_interests'][keyword] += 1
            else:
                profile['health_interests'][keyword] = 1
        
        # Update conversation style
        sentiment = memory_entry.get('sentiment', 'neutral')
        profile['sentiment_distribution'][sentiment] += 1
        
        # Update last interaction
        profile['last_interaction'] = memory_entry['timestamp']
        
        self.user_profiles[user_id] = profile
    
    def _create_default_profile(self) -> Dict:
        """Create default user profile."""
        return {
            'user_id': 'anonymous',
            'total_conversations': 0,
            'total_messages': 0,
            'health_interests': {},
            'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
            'personality_traits': {},
            'conversation_style': 'formal',
            'last_interaction': datetime.now().isoformat(),
            'preferences': {
                'response_length': 'medium',
                'technical_level': 'general',
                'emotion_support': True
            }
        }
    
    def _analyze_personality(self, user_id: str) -> Dict:
        """Analyze user personality based on conversation history."""
        if user_id not in self.user_profiles:
            return {}
        
        profile = self.user_profiles[user_id]
        sentiment_dist = profile['sentiment_distribution']
        
        # Calculate personality traits
        total_messages = sum(sentiment_dist.values())
        if total_messages == 0:
            return {}
        
        positivity_ratio = sentiment_dist.get('positive', 0) / total_messages
        negativity_ratio = sentiment_dist.get('negative', 0) / total_messages
        
        personality = {
            'optimism_level': 'high' if positivity_ratio > 0.6 else 'low' if negativity_ratio > 0.6 else 'balanced',
            'engagement_level': 'high' if total_messages > 10 else 'medium' if total_messages > 5 else 'low',
            'health_consciousness': 'high' if len(profile['health_interests']) > 5 else 'medium' if len(profile['health_interests']) > 2 else 'low'
        }
        
        return personality
    
    def _analyze_conversation_style(self, user_id: str) -> str:
        """Analyze user's conversation style."""
        if user_id not in self.user_profiles:
            return 'formal'
        
        profile = self.user_profiles[user_id]
        total_messages = profile['total_messages']
        
        if total_messages < 3:
            return 'formal'
        elif total_messages > 10:
            return 'casual'
        else:
            return 'mixed'
    
    def _analyze_health_interests(self, user_id: str) -> Dict:
        """Analyze user's health interests."""
        if user_id not in self.user_profiles:
            return {}
        
        profile = self.user_profiles[user_id]
        interests = profile['health_interests']
        
        # Sort by frequency
        sorted_interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_interests[:5])
    
    def _should_promote_to_long_term(self, memory_entry: Dict) -> bool:
        """Determine if memory should be promoted to long-term storage."""
        # Promote based on relevance score and content importance
        relevance_score = memory_entry.get('relevance_score', 0)
        keywords = memory_entry.get('keywords', [])
        
        # High relevance or contains important health keywords
        important_keywords = ['emergency', 'symptom', 'treatment', 'medication', 'diagnosis']
        has_important_keywords = any(keyword in important_keywords for keyword in keywords)
        
        return relevance_score > 0.8 or has_important_keywords
    
    def _promote_to_long_term(self, memory_entry: Dict):
        """Promote session memory to long-term storage."""
        long_term_entry = memory_entry.copy()
        long_term_entry['memory_type'] = 'long_term'
        long_term_entry['promoted_at'] = datetime.now().isoformat()
        
        self.long_term_memories.append(long_term_entry)
        self._save_memories()
        
        logger.info(f"Promoted memory to long-term storage")
    
    def _cleanup_old_memories(self):
        """Clean up old memories for privacy and storage management."""
        cutoff_date = datetime.now() - timedelta(days=self.memory_retention_days)
        
        # Clean up session memories
        for session_id in list(self.session_memories.keys()):
            memories = self.session_memories[session_id]
            filtered_memories = [
                memory for memory in memories
                if datetime.fromisoformat(memory['timestamp']) > cutoff_date
            ]
            
            if filtered_memories:
                self.session_memories[session_id] = filtered_memories
            else:
                del self.session_memories[session_id]
        
        # Clean up long-term memories
        self.long_term_memories = [
            memory for memory in self.long_term_memories
            if datetime.fromisoformat(memory['timestamp']) > cutoff_date
        ]
        
        # Save cleaned memories
        self._save_memories()
    
    def _calculate_duration(self, memories: List[Dict]) -> str:
        """Calculate conversation duration."""
        if len(memories) < 2:
            return "0 minutes"
        
        first_time = datetime.fromisoformat(memories[0]['timestamp'])
        last_time = datetime.fromisoformat(memories[-1]['timestamp'])
        duration = last_time - first_time
        
        minutes = duration.total_seconds() / 60
        return f"{int(minutes)} minutes"
    
    def get_memory_stats(self) -> Dict:
        """Get comprehensive memory statistics."""
        total_session_memories = sum(len(memories) for memories in self.session_memories.values())
        total_long_term_memories = len(self.long_term_memories)
        
        return {
            "session_memories": total_session_memories,
            "long_term_memories": total_long_term_memories,
            "total_memories": total_session_memories + total_long_term_memories,
            "active_sessions": len(self.session_memories),
            "user_profiles": len(self.user_profiles),
            "memory_retention_days": self.memory_retention_days,
            "relevance_threshold": self.relevance_threshold,
            "last_cleanup": datetime.now().isoformat()
        }
    
    def export_memories(self, filepath: str):
        """Export memories for backup or analysis."""
        export_data = {
            "session_memories": self.session_memories,
            "long_term_memories": self.long_term_memories,
            "user_profiles": self.user_profiles,
            "export_timestamp": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"Memories exported to {filepath}")
    
    def import_memories(self, filepath: str):
        """Import memories from backup."""
        with open(filepath, 'r') as f:
            import_data = json.load(f)
        
        self.session_memories.update(import_data.get("session_memories", {}))
        self.long_term_memories.extend(import_data.get("long_term_memories", []))
        self.user_profiles.update(import_data.get("user_profiles", {}))
        
        self._save_memories()
        logger.info(f"Memories imported from {filepath}")
    
    def clear_user_data(self, user_id: str):
        """Clear user data for privacy compliance."""
        # Remove from user profiles
        if user_id in self.user_profiles:
            del self.user_profiles[user_id]
        
        # Remove from long-term memories
        self.long_term_memories = [
            memory for memory in self.long_term_memories
            if memory.get('user_id') != user_id
        ]
        
        # Remove from session memories
        for session_id in list(self.session_memories.keys()):
            memories = self.session_memories[session_id]
            filtered_memories = [
                memory for memory in memories
                if memory.get('user_id') != user_id
            ]
            
            if filtered_memories:
                self.session_memories[session_id] = filtered_memories
            else:
                del self.session_memories[session_id]
        
        self._save_memories()
        logger.info(f"Cleared all data for user {user_id}") 