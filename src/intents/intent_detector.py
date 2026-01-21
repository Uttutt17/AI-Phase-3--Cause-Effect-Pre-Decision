"""Intent detection engine using NLP."""
import spacy
from typing import List, Dict, Any, Optional
from src.schemas.intent import IntentType, IntentResponse
import re


class IntentDetector:
    """Detects user intent from natural language queries."""
    
    def __init__(self):
        """Initialize the intent detector with spaCy model."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback to basic pattern matching if spaCy model not available
            self.nlp = None
    
    def detect_intent(self, user_query: str, product_ids: Optional[List[str]] = None) -> IntentResponse:
        """
        Detect intent from user query.
        
        Args:
            user_query: User's natural language query
            product_ids: Optional list of product IDs mentioned
            
        Returns:
            IntentResponse with detected intent and confidence
        """
        query_lower = user_query.lower()
        
        # Extract product IDs from query if not provided
        if product_ids is None:
            product_ids = self._extract_product_ids(user_query)
        
        # Pattern-based intent detection (more reliable than pure NLP for this use case)
        intent_scores = {
            IntentType.COMPARE: self._score_compare_intent(query_lower),
            IntentType.EXPLAIN: self._score_explain_intent(query_lower),
            IntentType.CLARIFY: self._score_clarify_intent(query_lower),
            IntentType.CHOOSE: self._score_choose_intent(query_lower)
        }
        
        # Get highest scoring intent
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent_type, confidence = best_intent
        
        # Extract context
        extracted_context = self._extract_context(user_query)
        
        return IntentResponse(
            intent_type=intent_type if confidence > 0.3 else IntentType.UNKNOWN,
            confidence=confidence,
            detected_products=product_ids,
            extracted_context=extracted_context
        )
    
    def _score_compare_intent(self, query: str) -> float:
        """Score how likely the query is a compare intent."""
        compare_keywords = [
            "compare", "comparison", "difference", "differences", "vs", "versus",
            "better", "which is", "which one", "side by side"
        ]
        score = 0.0
        for keyword in compare_keywords:
            if keyword in query:
                score += 0.3
        return min(score, 1.0)
    
    def _score_explain_intent(self, query: str) -> float:
        """Score how likely the query is an explain intent."""
        explain_keywords = [
            "explain", "why", "how", "what does", "what is", "tell me about",
            "reason", "because", "due to"
        ]
        score = 0.0
        for keyword in explain_keywords:
            if keyword in query:
                score += 0.25
        return min(score, 1.0)
    
    def _score_clarify_intent(self, query: str) -> float:
        """Score how likely the query is a clarify intent."""
        clarify_keywords = [
            "fit", "size", "comfort", "comfortable", "wear", "heavy", "light",
            "weight", "clamp", "padding", "suitable", "right for", "good for"
        ]
        score = 0.0
        for keyword in clarify_keywords:
            if keyword in query:
                score += 0.2
        return min(score, 1.0)
    
    def _score_choose_intent(self, query: str) -> float:
        """Score how likely the query is a choose intent."""
        choose_keywords = [
            "which", "choose", "should i", "recommend", "best", "better for",
            "good for", "purchase", "buy", "decide", "decision"
        ]
        score = 0.0
        for keyword in choose_keywords:
            if keyword in query:
                score += 0.25
        return min(score, 1.0)
    
    def _extract_product_ids(self, query: str) -> List[str]:
        """Extract product IDs or names from query."""
        # Simple extraction - can be enhanced with NLP
        # For now, look for common product name patterns
        product_patterns = [
            r"airpods\s+(max|pro|mini)",
            r"product\s+(\w+)",
            r"(\w+)\s+headphones"
        ]
        
        product_ids = []
        for pattern in product_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            product_ids.extend(matches)
        
        return list(set(product_ids))
    
    def _extract_context(self, query: str) -> Dict[str, Any]:
        """Extract context from query."""
        context = {}
        
        # Extract usage context
        usage_keywords = ["travel", "gym", "work", "home", "office", "commute"]
        for keyword in usage_keywords:
            if keyword in query.lower():
                context["usage_context"] = keyword
        
        # Extract attribute mentions
        attribute_keywords = ["price", "weight", "battery", "noise", "comfort", "material"]
        mentioned_attributes = [kw for kw in attribute_keywords if kw in query.lower()]
        if mentioned_attributes:
            context["mentioned_attributes"] = mentioned_attributes
        
        return context

