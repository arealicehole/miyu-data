import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Types of queries for different optimization strategies"""
    FACTUAL = "factual"           # Direct factual questions
    CONCEPTUAL = "conceptual"     # Broader conceptual queries
    TEMPORAL = "temporal"         # Time-based queries
    DECISION = "decision"         # Decision-related queries
    ACTION = "action"             # Action items or tasks
    TECHNICAL = "technical"       # Technical discussions

@dataclass
class OptimizedQuery:
    """Optimized query with multiple search strategies"""
    original: str
    expanded: List[str]
    keywords: List[str]
    query_type: QueryType
    search_params: Dict
    
class QueryOptimizer:
    """Optimizes user queries for better RAG retrieval"""
    
    def __init__(self):
        # Keywords for query type detection
        self.type_keywords = {
            QueryType.FACTUAL: ['what', 'who', 'where', 'when', 'which', 'how many'],
            QueryType.CONCEPTUAL: ['why', 'how', 'explain', 'concept', 'understand'],
            QueryType.TEMPORAL: ['yesterday', 'today', 'tomorrow', 'last week', 'recently', 'ago'],
            QueryType.DECISION: ['decide', 'choice', 'option', 'should', 'better', 'recommend'],
            QueryType.ACTION: ['action', 'task', 'todo', 'need to', 'must', 'should do'],
            QueryType.TECHNICAL: ['code', 'implementation', 'technical', 'algorithm', 'architecture']
        }
        
        # Common stopwords to remove for keyword extraction
        self.stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
        
        # Domain-specific expansions for common terms
        self.expansion_map = {
            'app': ['application', 'software', 'program'],
            'mobile': ['ios', 'android', 'smartphone'],
            'db': ['database', 'storage', 'data'],
            'api': ['endpoint', 'interface', 'service'],
            'ui': ['interface', 'frontend', 'design'],
            'bug': ['error', 'issue', 'problem'],
            'feature': ['functionality', 'capability', 'enhancement']
        }
    
    def optimize_query(self, query: str) -> OptimizedQuery:
        """Main optimization method"""
        # Clean and normalize query
        cleaned_query = self._clean_query(query)
        
        # Detect query type
        query_type = self._detect_query_type(cleaned_query)
        
        # Extract keywords
        keywords = self._extract_keywords(cleaned_query)
        
        # Generate query expansions
        expanded_queries = self._expand_query(cleaned_query, keywords)
        
        # Determine search parameters based on query type
        search_params = self._get_search_params(query_type, len(keywords))
        
        return OptimizedQuery(
            original=query,
            expanded=expanded_queries,
            keywords=keywords,
            query_type=query_type,
            search_params=search_params
        )
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize the input query"""
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query.strip())
        
        # Convert to lowercase for processing
        query_lower = query.lower()
        
        # Remove common question patterns that don't add semantic value
        query_lower = re.sub(r'^(can you |please |help me |tell me )', '', query_lower)
        query_lower = re.sub(r'(please|thanks?|thank you)$', '', query_lower)
        
        return query_lower.strip()
    
    def _detect_query_type(self, query: str) -> QueryType:
        """Detect the type of query for optimization strategy"""
        query_lower = query.lower()
        
        # Score each query type based on keyword matches
        type_scores = {}
        for query_type, keywords in self.type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                type_scores[query_type] = score
        
        # Return the highest scoring type, or CONCEPTUAL as default
        if type_scores:
            return max(type_scores.items(), key=lambda x: x[1])[0]
        return QueryType.CONCEPTUAL
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from the query"""
        # Split into words and filter
        words = re.findall(r'\b\w+\b', query.lower())
        
        # Remove stopwords and short words
        keywords = [
            word for word in words 
            if word not in self.stopwords and len(word) > 2
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords[:10]  # Limit to top 10 keywords
    
    def _expand_query(self, query: str, keywords: List[str]) -> List[str]:
        """Generate expanded versions of the query"""
        expanded = [query]  # Always include original
        
        # Add keyword-focused version
        if keywords:
            keyword_query = ' '.join(keywords)
            if keyword_query != query:
                expanded.append(keyword_query)
        
        # Add expanded versions with synonyms
        expanded_terms = []
        for keyword in keywords:
            if keyword in self.expansion_map:
                expanded_terms.extend(self.expansion_map[keyword])
        
        if expanded_terms:
            # Create a version with some expanded terms
            expanded_query = query
            for original, expansions in self.expansion_map.items():
                if original in query:
                    # Replace with first expansion
                    expanded_query = expanded_query.replace(original, expansions[0])
            
            if expanded_query != query:
                expanded.append(expanded_query)
        
        # Add a broader conceptual version for complex queries
        if len(keywords) > 3:
            # Use only the most important keywords (first 3)
            broad_query = ' '.join(keywords[:3])
            if broad_query not in expanded:
                expanded.append(broad_query)
        
        return expanded[:4]  # Limit to 4 variations max
    
    def _get_search_params(self, query_type: QueryType, keyword_count: int) -> Dict:
        """Get optimized search parameters based on query characteristics"""
        base_params = {
            'top_k': 5,
            'min_score': 0.3,
            'include_metadata': True
        }
        
        # Adjust parameters based on query type
        if query_type == QueryType.FACTUAL:
            # Factual queries need higher precision
            base_params.update({
                'top_k': 3,
                'min_score': 0.4
            })
        elif query_type == QueryType.CONCEPTUAL:
            # Conceptual queries benefit from more results
            base_params.update({
                'top_k': 8,
                'min_score': 0.25
            })
        elif query_type == QueryType.TEMPORAL:
            # Temporal queries should prioritize recent content
            base_params.update({
                'top_k': 6,
                'min_score': 0.3,
                'prefer_recent': True
            })
        elif query_type in [QueryType.DECISION, QueryType.ACTION]:
            # Decision/action queries need comprehensive coverage
            base_params.update({
                'top_k': 10,
                'min_score': 0.2
            })
        elif query_type == QueryType.TECHNICAL:
            # Technical queries need precise matches
            base_params.update({
                'top_k': 5,
                'min_score': 0.35
            })
        
        # Adjust based on query complexity (keyword count)
        if keyword_count <= 2:
            # Simple queries - increase results to catch variations
            base_params['top_k'] = min(base_params['top_k'] + 2, 10)
            base_params['min_score'] = max(base_params['min_score'] - 0.05, 0.2)
        elif keyword_count >= 6:
            # Complex queries - higher precision needed
            base_params['min_score'] = min(base_params['min_score'] + 0.05, 0.5)
        
        return base_params

class MultiQueryProcessor:
    """Processes multiple query variations and combines results"""
    
    def __init__(self, db_service):
        self.db_service = db_service
        self.query_optimizer = QueryOptimizer()
    
    async def search_optimized(
        self, 
        query: str, 
        channel_id: int, 
        max_results: int = 10
    ) -> List[Dict]:
        """
        Perform optimized multi-query search
        
        Args:
            query: Original user query
            channel_id: Discord channel ID to search in
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with relevance scores
        """
        # Optimize the query
        optimized = self.query_optimizer.optimize_query(query)
        
        logger.info(f"Query optimization: type={optimized.query_type.value}, "
                   f"keywords={optimized.keywords}, expansions={len(optimized.expanded)}")
        
        # Search with multiple query variations
        all_results = []
        seen_chunks = set()
        
        for i, expanded_query in enumerate(optimized.expanded):
            try:
                # Use optimized search parameters
                results = await self.db_service.search_transcripts(
                    query=expanded_query,
                    channel_id=channel_id,
                    top_k=optimized.search_params['top_k'],
                    min_score=optimized.search_params['min_score']
                )
                
                # Add query source and boost original query results
                for result in results:
                    chunk_id = f"{result.get('timestamp', '')}_{result.get('chunk_index', 0)}"
                    
                    if chunk_id not in seen_chunks:
                        seen_chunks.add(chunk_id)
                        
                        # Boost score for original query matches
                        if i == 0:  # Original query
                            result['score'] *= 1.1
                        
                        result['query_source'] = 'original' if i == 0 else 'expanded'
                        result['query_variation'] = expanded_query
                        all_results.append(result)
                
                logger.debug(f"Query '{expanded_query}' returned {len(results)} results")
                
            except Exception as e:
                logger.error(f"Error searching with query '{expanded_query}': {e}")
                continue
        
        # Sort by score and return top results
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Apply final filtering and ranking
        final_results = self._post_process_results(all_results, optimized, max_results)
        
        logger.info(f"Multi-query search returned {len(final_results)} results "
                   f"from {len(optimized.expanded)} query variations")
        
        return final_results
    
    def _post_process_results(
        self, 
        results: List[Dict], 
        optimized_query: OptimizedQuery, 
        max_results: int
    ) -> List[Dict]:
        """Post-process and rank final results"""
        
        if not results:
            return []
        
        # Additional scoring based on keyword matches
        for result in results:
            text_lower = result.get('text', '').lower()
            keyword_matches = sum(1 for keyword in optimized_query.keywords 
                                if keyword in text_lower)
            
            # Boost score based on keyword density
            if optimized_query.keywords:
                keyword_ratio = keyword_matches / len(optimized_query.keywords)
                result['score'] *= (1 + keyword_ratio * 0.1)
        
        # Re-sort after keyword boosting
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Remove very low scores that might have slipped through
        filtered_results = [r for r in results if r['score'] >= 0.2]
        
        return filtered_results[:max_results]