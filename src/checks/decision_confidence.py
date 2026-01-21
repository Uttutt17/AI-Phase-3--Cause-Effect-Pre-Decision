"""Decision confidence scoring."""
from typing import Dict, Any, List


class DecisionConfidenceCheck:
    """Calculates confidence score for decision readiness."""
    
    def calculate(
        self,
        attribute_completeness: Dict[str, Any],
        user_context: Dict[str, Any],
        visualization_ready: Dict[str, Any],
        query_clarity: float = 0.5
    ) -> Dict[str, Any]:
        """
        Calculate overall decision confidence score.
        
        Args:
            attribute_completeness: Result from AttributeCompletenessCheck
            user_context: Result from UserContextCheck
            visualization_ready: Result from VisualizationReadyCheck
            query_clarity: Clarity score of user query (0-1)
        
        Returns:
            Dict with 'confidence' (float), 'passed' (bool), 'factors' (Dict)
        """
        # Weight factors
        attribute_weight = 0.4
        context_weight = 0.2
        visualization_weight = 0.2
        clarity_weight = 0.2
        
        # Get scores
        attribute_score = attribute_completeness.get("coverage", 0.0)
        context_score = 1.0 if user_context.get("passed", False) else 0.5
        visualization_score = 1.0 if visualization_ready.get("passed", False) else 0.5
        
        # Calculate weighted confidence
        confidence = (
            attribute_score * attribute_weight +
            context_score * context_weight +
            visualization_score * visualization_weight +
            query_clarity * clarity_weight
        )
        
        passed = confidence >= 0.7  # 70% confidence threshold
        
        factors = {
            "attribute_completeness": attribute_score,
            "user_context": context_score,
            "visualization_ready": visualization_score,
            "query_clarity": query_clarity
        }
        
        return {
            "confidence": confidence,
            "passed": passed,
            "factors": factors,
            "message": f"Decision confidence: {confidence:.1%}" + (" - Ready to proceed" if passed else " - Needs clarification")
        }

