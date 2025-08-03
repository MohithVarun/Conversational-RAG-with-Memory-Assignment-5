import json
import time
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging
from collections import defaultdict
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGEvaluationSystem:
    """
    Comprehensive evaluation system for RAG performance using RAGAS-like metrics.
    Evaluates retrieval accuracy, latency, relevance scoring, and system performance.
    """
    
    def __init__(self):
        self.evaluation_results = defaultdict(list)
        self.test_queries = []
        self.ground_truth = {}
        self.performance_metrics = {}
        
        # Initialize test data
        self._initialize_test_data()
    
    def _initialize_test_data(self):
        """Initialize test queries and ground truth for evaluation."""
        self.test_queries = [
            {
                "query": "What are the symptoms of hypertension?",
                "expected_category": "medical_condition",
                "expected_keywords": ["hypertension", "blood pressure", "symptoms"],
                "difficulty": "easy"
            },
            {
                "query": "How to manage diabetes?",
                "expected_category": "medical_condition",
                "expected_keywords": ["diabetes", "management", "blood sugar"],
                "difficulty": "medium"
            },
            {
                "query": "Treatment for respiratory infections",
                "expected_category": "treatment",
                "expected_keywords": ["respiratory", "infection", "treatment"],
                "difficulty": "medium"
            },
            {
                "query": "Mental health wellness tips",
                "expected_category": "wellness",
                "expected_keywords": ["mental health", "wellness", "tips"],
                "difficulty": "easy"
            },
            {
                "query": "Preventive care nutrition guidelines",
                "expected_category": "prevention",
                "expected_keywords": ["prevention", "nutrition", "guidelines"],
                "difficulty": "hard"
            }
        ]
        
        # Ground truth for evaluation
        self.ground_truth = {
            "hypertension": {
                "relevant_chunks": ["Hypertension Management", "blood pressure", "cardiovascular"],
                "irrelevant_chunks": ["diabetes", "respiratory", "mental health"]
            },
            "diabetes": {
                "relevant_chunks": ["Diabetes Prevention", "blood sugar", "metabolic"],
                "irrelevant_chunks": ["hypertension", "respiratory", "mental health"]
            },
            "respiratory": {
                "relevant_chunks": ["Respiratory Infection", "treatment", "infection"],
                "irrelevant_chunks": ["hypertension", "diabetes", "mental health"]
            }
        }
    
    def evaluate_retrieval_accuracy(self, knowledge_base, test_queries: List[str] = None) -> Dict:
        """Evaluate retrieval accuracy using precision, recall, and F1-score."""
        if test_queries is None:
            test_queries = [q["query"] for q in self.test_queries]
        
        accuracy_metrics = {
            "precision": [],
            "recall": [],
            "f1_score": [],
            "mean_reciprocal_rank": [],
            "normalized_discounted_cumulative_gain": []
        }
        
        for query in test_queries:
            try:
                # Get search results
                results = knowledge_base.search_knowledge(query, limit=5)
                
                # Calculate metrics for this query
                query_metrics = self._calculate_retrieval_metrics(query, results)
                
                for metric in accuracy_metrics:
                    if metric in query_metrics:
                        accuracy_metrics[metric].append(query_metrics[metric])
                
            except Exception as e:
                logger.error(f"Error evaluating query '{query}': {e}")
        
        # Calculate averages
        final_metrics = {}
        for metric, values in accuracy_metrics.items():
            if values:
                final_metrics[metric] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values)
                }
        
        return final_metrics
    
    def _calculate_retrieval_metrics(self, query: str, results: List[Dict]) -> Dict:
        """Calculate precision, recall, and F1-score for a single query."""
        # Determine relevant results based on ground truth
        relevant_results = []
        retrieved_results = []
        
        # Simple relevance determination based on query keywords
        query_lower = query.lower()
        relevant_keywords = []
        
        # Extract relevant keywords from ground truth
        for topic, truth in self.ground_truth.items():
            if topic in query_lower:
                relevant_keywords = truth["relevant_chunks"]
                break
        
        # If no specific ground truth, use general relevance
        if not relevant_keywords:
            relevant_keywords = ["management", "treatment", "symptoms", "prevention"]
        
        # Evaluate each result
        for i, result in enumerate(results):
            result_content = result.get('content', '').lower()
            result_title = result.get('title', '').lower()
            
            # Check if result is relevant
            is_relevant = any(keyword in result_content or keyword in result_title 
                            for keyword in relevant_keywords)
            
            retrieved_results.append(is_relevant)
            if is_relevant:
                relevant_results.append(i)
        
        # Calculate metrics
        retrieved_count = len(retrieved_results)
        relevant_count = len(relevant_results)
        true_positives = sum(retrieved_results)
        
        # Precision = TP / (TP + FP)
        precision = true_positives / retrieved_count if retrieved_count > 0 else 0
        
        # Recall = TP / (TP + FN)
        recall = true_positives / len(relevant_keywords) if relevant_keywords else 0
        
        # F1-score = 2 * (precision * recall) / (precision + recall)
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Mean Reciprocal Rank (MRR)
        mrr = 0
        if relevant_results:
            mrr = 1 / (relevant_results[0] + 1)  # +1 because rank is 1-indexed
        
        # Normalized Discounted Cumulative Gain (NDCG)
        ndcg = self._calculate_ndcg(retrieved_results, len(relevant_keywords))
        
        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "mean_reciprocal_rank": mrr,
            "normalized_discounted_cumulative_gain": ndcg
        }
    
    def _calculate_ndcg(self, retrieved_results: List[bool], total_relevant: int) -> float:
        """Calculate Normalized Discounted Cumulative Gain."""
        if total_relevant == 0:
            return 0
        
        dcg = 0
        idcg = 0
        
        # Calculate DCG
        for i, is_relevant in enumerate(retrieved_results):
            if is_relevant:
                dcg += 1 / np.log2(i + 2)  # +2 because log2(1) = 0
        
        # Calculate IDCG (ideal case where all relevant items are at the top)
        for i in range(min(total_relevant, len(retrieved_results))):
            idcg += 1 / np.log2(i + 2)
        
        return dcg / idcg if idcg > 0 else 0
    
    def evaluate_latency(self, knowledge_base, test_queries: List[str] = None) -> Dict:
        """Evaluate system latency and response times."""
        if test_queries is None:
            test_queries = [q["query"] for q in self.test_queries]
        
        latency_metrics = {
            "response_times": [],
            "search_times": [],
            "embedding_times": []
        }
        
        for query in test_queries:
            try:
                # Measure total response time
                start_time = time.time()
                results = knowledge_base.search_knowledge(query, limit=5)
                total_time = time.time() - start_time
                
                latency_metrics["response_times"].append(total_time)
                
                # Estimate search and embedding times (in a real system, these would be measured separately)
                search_time = total_time * 0.7  # Assume 70% is search time
                embedding_time = total_time * 0.3  # Assume 30% is embedding time
                
                latency_metrics["search_times"].append(search_time)
                latency_metrics["embedding_times"].append(embedding_time)
                
            except Exception as e:
                logger.error(f"Error measuring latency for query '{query}': {e}")
        
        # Calculate latency statistics
        latency_stats = {}
        for metric, times in latency_metrics.items():
            if times:
                latency_stats[metric] = {
                    "mean": np.mean(times),
                    "median": np.median(times),
                    "std": np.std(times),
                    "min": np.min(times),
                    "max": np.max(times),
                    "p95": np.percentile(times, 95),
                    "p99": np.percentile(times, 99)
                }
        
        return latency_stats
    
    def evaluate_relevance_scoring(self, knowledge_base, test_queries: List[str] = None) -> Dict:
        """Evaluate relevance scoring accuracy and consistency."""
        if test_queries is None:
            test_queries = [q["query"] for q in self.test_queries]
        
        relevance_metrics = {
            "relevance_scores": [],
            "score_distribution": defaultdict(int),
            "threshold_analysis": {},
            "consistency_metrics": {}
        }
        
        for query in test_queries:
            try:
                results = knowledge_base.search_knowledge(query, limit=5)
                
                for result in results:
                    score = result.get('relevance_score', 0)
                    relevance_metrics["relevance_scores"].append(score)
                    
                    # Score distribution
                    score_bucket = int(score * 10) / 10  # Round to nearest 0.1
                    relevance_metrics["score_distribution"][score_bucket] += 1
                
            except Exception as e:
                logger.error(f"Error evaluating relevance for query '{query}': {e}")
        
        # Calculate relevance statistics
        scores = relevance_metrics["relevance_scores"]
        if scores:
            relevance_metrics["consistency_metrics"] = {
                "mean_score": np.mean(scores),
                "std_score": np.std(scores),
                "min_score": np.min(scores),
                "max_score": np.max(scores),
                "score_range": np.max(scores) - np.min(scores)
            }
            
            # Threshold analysis
            thresholds = [0.1, 0.3, 0.5, 0.7, 0.9]
            threshold_analysis = {}
            for threshold in thresholds:
                above_threshold = sum(1 for score in scores if score >= threshold)
                threshold_analysis[f"above_{threshold}"] = above_threshold
                threshold_analysis[f"percentage_above_{threshold}"] = above_threshold / len(scores) * 100
            
            relevance_metrics["threshold_analysis"] = threshold_analysis
        
        return relevance_metrics
    
    def evaluate_context_awareness(self, knowledge_base, test_queries: List[str] = None) -> Dict:
        """Evaluate context-aware generation capabilities."""
        if test_queries is None:
            test_queries = [q["query"] for q in self.test_queries]
        
        context_metrics = {
            "context_utilization": [],
            "response_relevance": [],
            "context_coherence": []
        }
        
        for query in test_queries:
            try:
                results = knowledge_base.search_knowledge(query, limit=3)
                
                # Analyze context utilization
                context_utilization = len(results) / 3  # How much of available context is used
                context_metrics["context_utilization"].append(context_utilization)
                
                # Analyze response relevance
                if results:
                    avg_relevance = np.mean([r.get('relevance_score', 0) for r in results])
                    context_metrics["response_relevance"].append(avg_relevance)
                
                # Analyze context coherence (how well results relate to each other)
                coherence_score = self._calculate_context_coherence(results)
                context_metrics["context_coherence"].append(coherence_score)
                
            except Exception as e:
                logger.error(f"Error evaluating context awareness for query '{query}': {e}")
        
        # Calculate context awareness statistics
        context_stats = {}
        for metric, values in context_metrics.items():
            if values:
                context_stats[metric] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values)
                }
        
        return context_stats
    
    def _calculate_context_coherence(self, results: List[Dict]) -> float:
        """Calculate how coherent the retrieved context is."""
        if len(results) < 2:
            return 1.0  # Single result is perfectly coherent
        
        # Simple coherence based on category consistency
        categories = [r.get('category', 'unknown') for r in results]
        unique_categories = len(set(categories))
        
        # Coherence is higher when fewer unique categories (more focused)
        coherence = 1.0 - (unique_categories - 1) / len(results)
        return max(0.0, coherence)
    
    def evaluate_memory_effectiveness(self, memory_manager) -> Dict:
        """Evaluate memory management effectiveness."""
        try:
            memory_stats = memory_manager.get_memory_stats()
            
            memory_metrics = {
                "memory_utilization": memory_stats.get("total_memories", 0) / 1000,  # Normalize
                "session_memory_ratio": memory_stats.get("session_memories", 0) / max(memory_stats.get("total_memories", 1), 1),
                "long_term_memory_ratio": memory_stats.get("long_term_memories", 0) / max(memory_stats.get("total_memories", 1), 1),
                "active_sessions": memory_stats.get("active_sessions", 0),
                "user_profiles": memory_stats.get("user_profiles", 0),
                "memory_retention_days": memory_stats.get("memory_retention_days", 30)
            }
            
            return memory_metrics
            
        except Exception as e:
            logger.error(f"Error evaluating memory effectiveness: {e}")
            return {}
    
    def run_comprehensive_evaluation(self, knowledge_base, memory_manager) -> Dict:
        """Run comprehensive evaluation with all metrics."""
        logger.info("Starting comprehensive RAG evaluation...")
        
        evaluation_results = {
            "timestamp": datetime.now().isoformat(),
            "retrieval_accuracy": self.evaluate_retrieval_accuracy(knowledge_base),
            "latency": self.evaluate_latency(knowledge_base),
            "relevance_scoring": self.evaluate_relevance_scoring(knowledge_base),
            "context_awareness": self.evaluate_context_awareness(knowledge_base),
            "memory_effectiveness": self.evaluate_memory_effectiveness(memory_manager)
        }
        
        # Calculate overall system score
        overall_score = self._calculate_overall_score(evaluation_results)
        evaluation_results["overall_score"] = overall_score
        
        # Store results
        self.evaluation_results[datetime.now().isoformat()] = evaluation_results
        
        logger.info(f"Comprehensive evaluation completed. Overall score: {overall_score:.3f}")
        
        return evaluation_results
    
    def _calculate_overall_score(self, evaluation_results: Dict) -> float:
        """Calculate overall system performance score."""
        scores = []
        
        # Retrieval accuracy score (F1-score)
        if "retrieval_accuracy" in evaluation_results:
            f1_scores = evaluation_results["retrieval_accuracy"].get("f1_score", {})
            if "mean" in f1_scores:
                scores.append(f1_scores["mean"])
        
        # Latency score (inverse of response time)
        if "latency" in evaluation_results:
            response_times = evaluation_results["latency"].get("response_times", {})
            if "mean" in response_times:
                # Normalize latency (lower is better)
                latency_score = max(0, 1 - response_times["mean"] / 5.0)  # Assume 5s is max acceptable
                scores.append(latency_score)
        
        # Relevance scoring score
        if "relevance_scoring" in evaluation_results:
            consistency = evaluation_results["relevance_scoring"].get("consistency_metrics", {})
            if "mean_score" in consistency:
                scores.append(consistency["mean_score"])
        
        # Context awareness score
        if "context_awareness" in evaluation_results:
            coherence = evaluation_results["context_awareness"].get("context_coherence", {})
            if "mean" in coherence:
                scores.append(coherence["mean"])
        
        # Memory effectiveness score
        if "memory_effectiveness" in evaluation_results:
            memory_util = evaluation_results["memory_effectiveness"].get("memory_utilization", 0)
            scores.append(min(1.0, memory_util))
        
        # Calculate overall score as average of all component scores
        return np.mean(scores) if scores else 0.0
    
    def generate_evaluation_report(self, evaluation_results: Dict) -> str:
        """Generate a comprehensive evaluation report."""
        report = []
        report.append("=" * 80)
        report.append("RAG SYSTEM COMPREHENSIVE EVALUATION REPORT")
        report.append("=" * 80)
        report.append(f"Evaluation Date: {evaluation_results.get('timestamp', 'Unknown')}")
        report.append(f"Overall Score: {evaluation_results.get('overall_score', 0):.3f}")
        report.append("")
        
        # Retrieval Accuracy Section
        report.append("RETRIEVAL ACCURACY METRICS")
        report.append("-" * 40)
        accuracy = evaluation_results.get("retrieval_accuracy", {})
        for metric, stats in accuracy.items():
            if isinstance(stats, dict) and "mean" in stats:
                report.append(f"{metric.replace('_', ' ').title()}: {stats['mean']:.3f} (±{stats['std']:.3f})")
        report.append("")
        
        # Latency Section
        report.append("LATENCY METRICS")
        report.append("-" * 40)
        latency = evaluation_results.get("latency", {})
        response_times = latency.get("response_times", {})
        if "mean" in response_times:
            report.append(f"Mean Response Time: {response_times['mean']:.3f}s")
            report.append(f"95th Percentile: {response_times.get('p95', 0):.3f}s")
            report.append(f"99th Percentile: {response_times.get('p99', 0):.3f}s")
        report.append("")
        
        # Relevance Scoring Section
        report.append("RELEVANCE SCORING METRICS")
        report.append("-" * 40)
        relevance = evaluation_results.get("relevance_scoring", {})
        consistency = relevance.get("consistency_metrics", {})
        if "mean_score" in consistency:
            report.append(f"Mean Relevance Score: {consistency['mean_score']:.3f}")
            report.append(f"Score Range: {consistency.get('score_range', 0):.3f}")
        report.append("")
        
        # Context Awareness Section
        report.append("CONTEXT AWARENESS METRICS")
        report.append("-" * 40)
        context = evaluation_results.get("context_awareness", {})
        for metric, stats in context.items():
            if isinstance(stats, dict) and "mean" in stats:
                report.append(f"{metric.replace('_', ' ').title()}: {stats['mean']:.3f}")
        report.append("")
        
        # Memory Effectiveness Section
        report.append("MEMORY EFFECTIVENESS METRICS")
        report.append("-" * 40)
        memory = evaluation_results.get("memory_effectiveness", {})
        for metric, value in memory.items():
            if isinstance(value, (int, float)):
                report.append(f"{metric.replace('_', ' ').title()}: {value:.3f}")
        report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 40)
        overall_score = evaluation_results.get("overall_score", 0)
        if overall_score >= 0.8:
            report.append("✅ Excellent performance! System is ready for production.")
        elif overall_score >= 0.6:
            report.append("⚠️ Good performance with room for improvement.")
        else:
            report.append("❌ Performance needs significant improvement.")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def export_evaluation_data(self, filepath: str, evaluation_results: Dict):
        """Export evaluation data for analysis."""
        export_data = {
            "evaluation_results": evaluation_results,
            "test_queries": self.test_queries,
            "ground_truth": self.ground_truth,
            "export_timestamp": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"Evaluation data exported to {filepath}")
    
    def get_evaluation_history(self) -> List[Dict]:
        """Get evaluation history."""
        return list(self.evaluation_results.values())
    
    def clear_evaluation_history(self):
        """Clear evaluation history."""
        self.evaluation_results.clear()
        logger.info("Evaluation history cleared") 