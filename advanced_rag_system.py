import json
import os
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging
import numpy as np
from collections import defaultdict

# Import advanced components
from advanced_memory_manager import AdvancedMemoryManager
from advanced_knowledge_base import AdvancedKnowledgeBase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedRAGSystem:
    """
    Advanced RAG system with multi-session memory, context-aware generation,
    and comprehensive evaluation metrics.
    """
    
    def __init__(self, memory_db_path: str = "./advanced_memory_db", 
                 knowledge_db_path: str = "./advanced_knowledge_db"):
        # Initialize components
        self.memory_manager = AdvancedMemoryManager(memory_db_path)
        self.knowledge_base = AdvancedKnowledgeBase(knowledge_db_path)
        
        # System configuration
        self.max_context_length = 2000  # Maximum context length for generation
        self.response_generation_timeout = 30  # Seconds
        self.evaluation_metrics = defaultdict(list)
        
        # Load environment variables
        self._load_environment()
        
        # Initialize knowledge base with data
        self._initialize_knowledge_base()
        
        logger.info("Advanced RAG System initialized successfully")
    
    def _load_environment(self):
        """Load environment variables."""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            self.openai_api_key = os.getenv('OPENAI_API_KEY')
            if not self.openai_api_key:
                logger.warning("OpenAI API key not found. Using fallback responses.")
        except Exception as e:
            logger.error(f"Error loading environment: {e}")
            self.openai_api_key = None
    
    def _initialize_knowledge_base(self):
        """Initialize knowledge base with comprehensive data."""
        try:
            # Check if knowledge base is empty
            if len(self.knowledge_base.chunks) == 0:
                logger.info("Initializing knowledge base with comprehensive healthcare data...")
                self.knowledge_base.add_comprehensive_healthcare_data()
            else:
                logger.info(f"Knowledge base already contains {len(self.knowledge_base.chunks)} chunks")
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {e}")
    
    def generate_response(self, user_message: str, session_id: str, 
                         user_id: str = None) -> Dict:
        """
        Generate context-aware response using advanced RAG pipeline.
        """
        start_time = time.time()
        
        try:
            # Step 1: Retrieve relevant knowledge
            knowledge_results = self._retrieve_knowledge(user_message)
            
            # Step 2: Retrieve relevant memories
            memory_results = self._retrieve_memories(user_message, session_id, user_id)
            
            # Step 3: Get user profile for personalization
            user_profile = self._get_user_profile(user_id)
            
            # Step 4: Build context for generation
            context = self._build_generation_context(
                user_message, knowledge_results, memory_results, user_profile
            )
            
            # Step 5: Generate response
            response = self._generate_contextual_response(context)
            
            # Step 6: Store in memory
            self._store_conversation_memory(
                session_id, user_message, response, user_id
            )
            
            # Step 7: Calculate metrics
            response_time = time.time() - start_time
            metrics = self._calculate_response_metrics(
                user_message, response, knowledge_results, memory_results, response_time
            )
            
            return {
                "response": response,
                "knowledge_sources": [r['title'] for r in knowledge_results],
                "memory_used": len(memory_results) > 0,
                "user_profile_used": user_profile is not None,
                "response_time": response_time,
                "metrics": metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "I apologize, but I'm having trouble processing your request right now. Please try again.",
                "knowledge_sources": [],
                "memory_used": False,
                "user_profile_used": False,
                "response_time": time.time() - start_time,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _retrieve_knowledge(self, query: str) -> List[Dict]:
        """Retrieve relevant knowledge using advanced search."""
        try:
            # Search with different strategies
            results = []
            
            # Direct search
            direct_results = self.knowledge_base.search_knowledge(query, limit=3)
            results.extend(direct_results)
            
            # Category-specific search
            categories = ['medical_condition', 'treatment', 'prevention', 'wellness']
            for category in categories:
                if any(term in query.lower() for term in self._get_category_terms(category)):
                    category_results = self.knowledge_base.search_knowledge(
                        query, limit=2, category_filter=category
                    )
                    results.extend(category_results)
            
            # Remove duplicates and sort by relevance
            unique_results = self._deduplicate_results(results)
            unique_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return unique_results[:5]
            
        except Exception as e:
            logger.error(f"Error retrieving knowledge: {e}")
            return []
    
    def _retrieve_memories(self, query: str, session_id: str, user_id: str = None) -> List[Dict]:
        """Retrieve relevant memories for context."""
        try:
            memories = []
            
            # Get session context
            session_memories = self.memory_manager.get_session_context(session_id, limit=5)
            memories.extend(session_memories)
            
            # Get relevant long-term memories
            if user_id:
                long_term_memories = self.memory_manager.get_relevant_long_term_memories(
                    query, user_id, limit=3
                )
                memories.extend(long_term_memories)
            
            return memories
            
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            return []
    
    def _get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile for personalization."""
        if not user_id:
            return None
        
        try:
            return self.memory_manager.get_user_profile(user_id)
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    def _build_generation_context(self, user_message: str, knowledge_results: List[Dict],
                                memory_results: List[Dict], user_profile: Optional[Dict]) -> Dict:
        """Build comprehensive context for response generation."""
        context = {
            "user_message": user_message,
            "knowledge_context": self._format_knowledge_context(knowledge_results),
            "memory_context": self._format_memory_context(memory_results),
            "user_profile": user_profile,
            "conversation_summary": self._get_conversation_summary(memory_results),
            "response_style": self._determine_response_style(user_profile, user_message)
        }
        
        return context
    
    def _format_knowledge_context(self, knowledge_results: List[Dict]) -> str:
        """Format knowledge results for context."""
        if not knowledge_results:
            return ""
        
        context_parts = []
        for i, result in enumerate(knowledge_results[:3]):
            context_parts.append(f"Source {i+1}: {result['title']}")
            context_parts.append(f"Content: {result['content'][:200]}...")
            context_parts.append(f"Relevance: {result['relevance_score']:.2f}")
        
        return "\n".join(context_parts)
    
    def _format_memory_context(self, memory_results: List[Dict]) -> str:
        """Format memory results for context."""
        if not memory_results:
            return ""
        
        context_parts = []
        for memory in memory_results[:2]:
            context_parts.append(f"Previous: {memory.get('user_message', '')[:100]}...")
            context_parts.append(f"Response: {memory.get('assistant_response', '')[:100]}...")
        
        return "\n".join(context_parts)
    
    def _get_conversation_summary(self, memory_results: List[Dict]) -> Dict:
        """Generate conversation summary for context."""
        if not memory_results:
            return {}
        
        # Analyze conversation patterns
        topics = defaultdict(int)
        sentiments = []
        
        for memory in memory_results:
            # Extract topics from keywords
            keywords = memory.get('keywords', [])
            for keyword in keywords:
                topics[keyword] += 1
            
            # Collect sentiments
            sentiment = memory.get('sentiment', 'neutral')
            sentiments.append(sentiment)
        
        return {
            "main_topics": sorted(topics.items(), key=lambda x: x[1], reverse=True)[:3],
            "average_sentiment": self._calculate_average_sentiment(sentiments),
            "conversation_length": len(memory_results)
        }
    
    def _determine_response_style(self, user_profile: Optional[Dict], user_message: str) -> str:
        """Determine appropriate response style based on user profile and message."""
        if not user_profile:
            return "professional"
        
        # Analyze user preferences
        conversation_style = user_profile.get('conversation_style', 'formal')
        personality_traits = user_profile.get('personality_traits', {})
        
        # Determine style based on profile and message content
        if conversation_style == 'casual' or personality_traits.get('optimism_level') == 'high':
            return "friendly"
        elif any(word in user_message.lower() for word in ['emergency', 'urgent', 'severe']):
            return "urgent"
        elif any(word in user_message.lower() for word in ['technical', 'detailed', 'explain']):
            return "detailed"
        else:
            return "professional"
    
    def _generate_contextual_response(self, context: Dict) -> str:
        """Generate contextual response using the built context."""
        user_message = context['user_message']
        knowledge_context = context['knowledge_context']
        memory_context = context['memory_context']
        user_profile = context['user_profile']
        response_style = context['response_style']
        
        # Generate response based on context and style
        if response_style == "urgent":
            return self._generate_urgent_response(user_message, knowledge_context)
        elif response_style == "friendly":
            return self._generate_friendly_response(user_message, knowledge_context, user_profile)
        elif response_style == "detailed":
            return self._generate_detailed_response(user_message, knowledge_context)
        else:
            return self._generate_professional_response(user_message, knowledge_context, memory_context)
    
    def _generate_urgent_response(self, user_message: str, knowledge_context: str) -> str:
        """Generate urgent response for emergency situations."""
        response = "⚠️ **IMPORTANT:** If you're experiencing a medical emergency, please:\n\n"
        response += "🚨 **Immediate Actions:**\n"
        response += "• Call emergency services (911) immediately\n"
        response += "• Go to the nearest emergency room\n"
        response += "• Don't wait for online advice\n\n"
        
        if knowledge_context:
            response += "📋 **Relevant Information:**\n"
            response += knowledge_context + "\n\n"
        
        response += "This assistant is for general health information only and cannot provide emergency medical guidance."
        return response
    
    def _generate_friendly_response(self, user_message: str, knowledge_context: str, 
                                 user_profile: Optional[Dict]) -> str:
        """Generate friendly, personalized response."""
        response = "Hi there! 👋 "
        
        if user_profile:
            name = user_profile.get('user_id', 'there')
            response += f"Thanks for reaching out, {name}! "
        
        response += "I'm here to help with your health questions.\n\n"
        
        if knowledge_context:
            response += "💡 **Here's what I found for you:**\n"
            response += knowledge_context + "\n\n"
            response += "✨ **Remember:** This information is for educational purposes. Always consult healthcare professionals for personalized advice!"
        else:
            response += "I understand your question! While I can provide general health information, it's always best to consult with healthcare professionals for personalized guidance.\n\n"
            response += "💚 **Health Tip:** Maintaining a healthy lifestyle with proper diet, exercise, and regular check-ups is key to overall wellness!"
        
        return response
    
    def _generate_detailed_response(self, user_message: str, knowledge_context: str) -> str:
        """Generate detailed, technical response."""
        response = "Here's a comprehensive analysis of your health question:\n\n"
        
        if knowledge_context:
            response += "📚 **Detailed Information:**\n"
            response += knowledge_context + "\n\n"
            response += "🔬 **Key Points:**\n"
            response += "• Evidence-based recommendations\n"
            response += "• Clinical guidelines and best practices\n"
            response += "• Risk factors and prevention strategies\n\n"
        else:
            response += "📋 **General Information:**\n"
            response += "Based on your question, here are some important considerations:\n\n"
            response += "• Regular health monitoring is essential\n"
            response += "• Lifestyle modifications can significantly impact outcomes\n"
            response += "• Professional medical evaluation is recommended\n\n"
        
        response += "📞 **Next Steps:** Consider scheduling an appointment with your healthcare provider for personalized guidance."
        return response
    
    def _generate_professional_response(self, user_message: str, knowledge_context: str, 
                                     memory_context: str) -> str:
        """Generate professional, balanced response."""
        response = "Thank you for your health-related question. Here's what I can share:\n\n"
        
        if knowledge_context:
            response += "📋 **Relevant Information:**\n"
            response += knowledge_context + "\n\n"
        
        if memory_context:
            response += "📝 **Context from our conversation:**\n"
            response += memory_context + "\n\n"
        
        response += "💡 **Recommendations:**\n"
        response += "• Monitor your symptoms closely\n"
        response += "• Maintain a healthy lifestyle\n"
        response += "• Consult healthcare professionals for personalized advice\n\n"
        
        response += "⚠️ **Important:** This information is for educational purposes only. Always consult healthcare professionals for medical advice."
        return response
    
    def _store_conversation_memory(self, session_id: str, user_message: str, 
                                 response: str, user_id: str = None):
        """Store conversation in memory for future reference."""
        try:
            self.memory_manager.add_session_memory(
                session_id=session_id,
                user_message=user_message,
                assistant_response=response,
                user_id=user_id
            )
        except Exception as e:
            logger.error(f"Error storing conversation memory: {e}")
    
    def _calculate_response_metrics(self, user_message: str, response: str,
                                 knowledge_results: List[Dict], memory_results: List[Dict],
                                 response_time: float) -> Dict:
        """Calculate comprehensive response metrics."""
        metrics = {
            "response_time": response_time,
            "knowledge_relevance": self._calculate_knowledge_relevance(knowledge_results),
            "memory_utilization": len(memory_results),
            "response_length": len(response),
            "user_message_length": len(user_message),
            "knowledge_sources_count": len(knowledge_results),
            "average_knowledge_score": self._calculate_average_knowledge_score(knowledge_results)
        }
        
        # Store metrics for evaluation
        self.evaluation_metrics['response_times'].append(response_time)
        self.evaluation_metrics['knowledge_relevance_scores'].append(metrics['knowledge_relevance'])
        
        return metrics
    
    def _calculate_knowledge_relevance(self, knowledge_results: List[Dict]) -> float:
        """Calculate overall knowledge relevance score."""
        if not knowledge_results:
            return 0.0
        
        scores = [result.get('relevance_score', 0) for result in knowledge_results]
        return sum(scores) / len(scores)
    
    def _calculate_average_knowledge_score(self, knowledge_results: List[Dict]) -> float:
        """Calculate average knowledge score."""
        if not knowledge_results:
            return 0.0
        
        scores = [result.get('relevance_score', 0) for result in knowledge_results]
        return sum(scores) / len(scores)
    
    def _calculate_average_sentiment(self, sentiments: List[str]) -> float:
        """Calculate average sentiment score."""
        if not sentiments:
            return 0.0
        
        sentiment_scores = []
        for sentiment in sentiments:
            if sentiment == 'positive':
                sentiment_scores.append(1)
            elif sentiment == 'negative':
                sentiment_scores.append(-1)
            else:
                sentiment_scores.append(0)
        
        return sum(sentiment_scores) / len(sentiment_scores)
    
    def _get_category_terms(self, category: str) -> List[str]:
        """Get relevant terms for a category."""
        category_terms = {
            'medical_condition': ['condition', 'disease', 'illness', 'symptom', 'diagnosis'],
            'treatment': ['treatment', 'therapy', 'medication', 'cure', 'remedy'],
            'prevention': ['prevention', 'prevent', 'avoid', 'protection', 'screening'],
            'wellness': ['wellness', 'health', 'fitness', 'lifestyle', 'nutrition']
        }
        return category_terms.get(category, [])
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on content."""
        seen_contents = set()
        unique_results = []
        
        for result in results:
            content_hash = hash(result.get('content', ''))
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                unique_results.append(result)
        
        return unique_results
    
    def get_system_stats(self) -> Dict:
        """Get comprehensive system statistics."""
        memory_stats = self.memory_manager.get_memory_stats()
        knowledge_stats = self.knowledge_base.get_knowledge_stats()
        
        # Calculate evaluation metrics
        avg_response_time = np.mean(self.evaluation_metrics['response_times']) if self.evaluation_metrics['response_times'] else 0
        avg_knowledge_relevance = np.mean(self.evaluation_metrics['knowledge_relevance_scores']) if self.evaluation_metrics['knowledge_relevance_scores'] else 0
        
        return {
            "memory_stats": memory_stats,
            "knowledge_stats": knowledge_stats,
            "evaluation_metrics": {
                "average_response_time": round(avg_response_time, 3),
                "average_knowledge_relevance": round(avg_knowledge_relevance, 3),
                "total_responses": len(self.evaluation_metrics['response_times']),
                "system_uptime": datetime.now().isoformat()
            },
            "system_configuration": {
                "max_context_length": self.max_context_length,
                "response_generation_timeout": self.response_generation_timeout,
                "embedding_model_available": self.knowledge_base.embedding_model is not None
            }
        }
    
    def evaluate_system_performance(self) -> Dict:
        """Evaluate system performance using RAGAS-like metrics."""
        if not self.evaluation_metrics['response_times']:
            return {"error": "No evaluation data available"}
        
        # Calculate metrics
        response_times = self.evaluation_metrics['response_times']
        knowledge_scores = self.evaluation_metrics['knowledge_relevance_scores']
        
        evaluation = {
            "latency": {
                "average_response_time": np.mean(response_times),
                "min_response_time": np.min(response_times),
                "max_response_time": np.max(response_times),
                "response_time_std": np.std(response_times)
            },
            "retrieval_accuracy": {
                "average_knowledge_relevance": np.mean(knowledge_scores),
                "knowledge_relevance_std": np.std(knowledge_scores),
                "high_relevance_responses": sum(1 for score in knowledge_scores if score > 0.7)
            },
            "system_utilization": {
                "total_responses": len(response_times),
                "memory_utilization_rate": self._calculate_memory_utilization_rate(),
                "knowledge_coverage": self._calculate_knowledge_coverage()
            }
        }
        
        return evaluation
    
    def _calculate_memory_utilization_rate(self) -> float:
        """Calculate memory utilization rate."""
        memory_stats = self.memory_manager.get_memory_stats()
        total_memories = memory_stats['total_memories']
        return min(1.0, total_memories / 1000)  # Normalize to 0-1
    
    def _calculate_knowledge_coverage(self) -> float:
        """Calculate knowledge coverage rate."""
        knowledge_stats = self.knowledge_base.get_knowledge_stats()
        total_chunks = knowledge_stats['total_chunks']
        return min(1.0, total_chunks / 100)  # Normalize to 0-1
    
    def export_system_data(self, filepath: str):
        """Export system data for analysis."""
        export_data = {
            "system_stats": self.get_system_stats(),
            "evaluation_metrics": dict(self.evaluation_metrics),
            "memory_export": self.memory_manager.export_memories,
            "knowledge_export": self.knowledge_base.export_knowledge,
            "export_timestamp": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"System data exported to {filepath}")
    
    def clear_system_data(self):
        """Clear all system data."""
        self.memory_manager.clear_user_data("all")
        self.knowledge_base.clear_knowledge()
        self.evaluation_metrics.clear()
        
        logger.info("System data cleared") 