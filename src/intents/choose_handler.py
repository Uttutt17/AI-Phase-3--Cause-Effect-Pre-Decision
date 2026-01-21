"""CHOOSE intent handler with pre-decision checks."""
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from src.intents.intent_handler import IntentHandler
from src.checks.attribute_completeness import AttributeCompletenessCheck
from src.checks.user_context import UserContextCheck
from src.checks.visualization_ready import VisualizationReadyCheck
from src.checks.decision_confidence import DecisionConfidenceCheck
from src.schemas.intent import IntentResponse
from src.schemas.visualization import VisualizationResponse


class ChooseHandler:
    """Handles CHOOSE intent with pre-decision checks."""
    
    def __init__(self):
        self.intent_handler = IntentHandler()
        self.attribute_check = AttributeCompletenessCheck()
        self.context_check = UserContextCheck()
        self.visualization_check = VisualizationReadyCheck()
        self.confidence_check = DecisionConfidenceCheck()
    
    def handle_choose_intent(
        self,
        db: Session,
        user_query: str,
        product_ids: List[str] = None
    ) -> tuple[IntentResponse, VisualizationResponse, Dict[str, Any]]:
        """
        Handle CHOOSE intent with pre-decision checks.
        
        Returns:
            Tuple of (IntentResponse, VisualizationResponse, ChecksResult)
        """
        # First, detect intent and get initial visualization
        intent_response, visualization_response = self.intent_handler.process_intent(
            db, user_query, product_ids
        )
        
        if not visualization_response.product_ids:
            return intent_response, visualization_response, {"checks": None, "message": "No products detected"}
        
        # Run pre-decision checks
        checks_result = self._run_pre_decision_checks(
            db,
            visualization_response.product_ids,
            visualization_response.selected_attributes,
            intent_response.extracted_context or {},
            user_query
        )
        
        # If checks fail, modify visualization response
        if not checks_result.get("passed", False):
            visualization_response.message = checks_result.get("message", "Pre-decision checks failed")
        
        return intent_response, visualization_response, checks_result
    
    def _run_pre_decision_checks(
        self,
        db: Session,
        product_ids: List[str],
        selected_attributes: List[str],
        user_context: Dict[str, Any],
        user_query: str
    ) -> Dict[str, Any]:
        """Run all pre-decision checks."""
        # 1. Attribute completeness check
        attribute_result = self.attribute_check.check(
            db, product_ids, selected_attributes
        )
        
        # 2. User context validation
        context_result = self.context_check.check(
            db, product_ids, user_context
        )
        
        # 3. Visualization readiness check
        visualization_result = self.visualization_check.check(
            db, product_ids, ["main_image"]
        )
        
        # 4. Decision confidence score
        # Estimate query clarity (simple heuristic)
        query_clarity = min(len(user_query.split()) / 10.0, 1.0)
        
        confidence_result = self.confidence_check.calculate(
            attribute_result,
            context_result,
            visualization_result,
            query_clarity
        )
        
        # Overall result
        all_checks_passed = (
            attribute_result.get("passed", False) and
            context_result.get("passed", False) and
            visualization_result.get("passed", False) and
            confidence_result.get("passed", False)
        )
        
        return {
            "passed": all_checks_passed,
            "checks": {
                "attribute_completeness": attribute_result,
                "user_context": context_result,
                "visualization_ready": visualization_result,
                "decision_confidence": confidence_result
            },
            "message": confidence_result.get("message", "Pre-decision checks completed")
        }

