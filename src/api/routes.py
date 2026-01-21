"""FastAPI route handlers."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from src.database import get_db
from src.schemas.intent import IntentRequest, IntentResponse
from src.schemas.visualization import VisualizationResponse
from src.schemas.explanation import ExplanationRequest, ExplanationResponse
from src.schemas.product import ProductCreate, ProductFullResponse
from src.intents.intent_handler import IntentHandler
from src.intents.choose_handler import ChooseHandler
from src.explanation.chatgpt_explainer import ChatGPTExplainer
from src.visualization.visualization_engine import VisualizationEngine
from src.data.product_service import ProductService

router = APIRouter()


@router.post("/intent/detect", response_model=IntentResponse)
async def detect_intent(
    request: IntentRequest,
    db: Session = Depends(get_db)
):
    """Detect user intent from query."""
    handler = IntentHandler()
    intent_response, _ = handler.process_intent(db, request.user_query, request.product_ids)
    return intent_response


@router.post("/intent/process", response_model=dict)
async def process_intent(
    request: IntentRequest,
    db: Session = Depends(get_db)
):
    """Process intent and return visualization."""
    handler = IntentHandler()
    intent_response, visualization_response = handler.process_intent(
        db, request.user_query, request.product_ids
    )
    
    # Apply visual effects
    viz_engine = VisualizationEngine()
    enhanced_data = viz_engine.apply_visual_effects(visualization_response)
    
    return {
        "intent": intent_response,
        "visualization": {
            **visualization_response.model_dump(),
            "visualization_data": enhanced_data
        }
    }


@router.post("/intent/choose", response_model=dict)
async def handle_choose_intent(
    request: IntentRequest,
    db: Session = Depends(get_db)
):
    """Handle CHOOSE intent with pre-decision checks."""
    handler = ChooseHandler()
    intent_response, visualization_response, checks_result = handler.handle_choose_intent(
        db, request.user_query, request.product_ids
    )
    
    # Apply visual effects
    viz_engine = VisualizationEngine()
    enhanced_data = viz_engine.apply_visual_effects(visualization_response)
    
    return {
        "intent": intent_response,
        "visualization": {
            **visualization_response.model_dump(),
            "visualization_data": enhanced_data
        },
        "pre_decision_checks": checks_result
    }


@router.post("/explanation/generate", response_model=ExplanationResponse)
async def generate_explanation(
    request: ExplanationRequest
):
    """Generate explanation using GPT-4."""
    explainer = ChatGPTExplainer()
    return explainer.generate_explanation(request)


@router.post("/explanation/full", response_model=dict)
async def full_flow_with_explanation(
    request: IntentRequest,
    db: Session = Depends(get_db)
):
    """Complete flow: intent → visualization → explanation."""
    # Process intent
    handler = IntentHandler()
    intent_response, visualization_response = handler.process_intent(
        db, request.user_query, request.product_ids
    )
    
    # Apply visual effects
    viz_engine = VisualizationEngine()
    enhanced_data = viz_engine.apply_visual_effects(visualization_response)
    
    # Generate explanation
    if visualization_response.product_ids and visualization_response.selected_attributes:
        # Format attributes for explanation
        product_service = ProductService()
        products_attrs = product_service.get_products_attributes(
            db, visualization_response.product_ids
        )
        
        # Filter to selected attributes only
        formatted_attrs = {}
        for product_id, attrs in products_attrs.items():
            formatted_attrs[product_id] = {
                attr: attrs.get(attr) for attr in visualization_response.selected_attributes
                if attr in attrs
            }
        
        explanation_request = ExplanationRequest(
            user_intent=intent_response.intent_type.value,
            selected_attributes=formatted_attrs,
            visual_effects_applied=[effect.value for effect in visualization_response.visual_effects],
            products=visualization_response.product_ids,
            user_query=request.user_query
        )
        
        explainer = ChatGPTExplainer()
        explanation_response = explainer.generate_explanation(explanation_request)
    else:
        explanation_response = ExplanationResponse(
            explanation="Unable to generate explanation: no products or attributes selected.",
            source_data_verified=False
        )
    
    return {
        "intent": intent_response,
        "visualization": {
            **visualization_response.model_dump(),
            "visualization_data": enhanced_data
        },
        "explanation": explanation_response
    }


@router.post("/products", response_model=ProductFullResponse)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """Create a new product."""
    service = ProductService()
    created_product = service.create_product(db, product)
    
    # Return full product data
    return ProductFullResponse(
        id=created_product.id,
        product_id=created_product.product_id,
        name=created_product.name,
        category=created_product.category,
        attributes=[
            {
                "attribute_name": attr.attribute_name,
                "attribute_type": attr.attribute_type,
                "attribute_value": attr.attribute_value,
                "unit": attr.unit,
                "display_name": attr.display_name
            }
            for attr in created_product.attributes
        ],
        visual_assets=[
            {
                "asset_type": asset.asset_type,
                "asset_url": asset.asset_url,
                "metadata": asset.metadata
            }
            for asset in created_product.visual_assets
        ]
    )


@router.get("/products", response_model=List[ProductFullResponse])
async def get_all_products(db: Session = Depends(get_db)):
    """Get all products."""
    service = ProductService()
    products = service.get_all_products(db)
    
    result = []
    for product in products:
        result.append(ProductFullResponse(
            id=product.id,
            product_id=product.product_id,
            name=product.name,
            category=product.category,
            attributes=[
                {
                    "attribute_name": attr.attribute_name,
                    "attribute_type": attr.attribute_type,
                    "attribute_value": attr.attribute_value,
                    "unit": attr.unit,
                    "display_name": attr.display_name
                }
                for attr in product.attributes
            ],
            visual_assets=[
                {
                    "asset_type": asset.asset_type,
                    "asset_url": asset.asset_url,
                    "metadata": asset.metadata
                }
                for asset in product.visual_assets
            ]
        ))
    
    return result


@router.get("/products/{product_id}", response_model=ProductFullResponse)
async def get_product(product_id: str, db: Session = Depends(get_db)):
    """Get product by ID."""
    service = ProductService()
    product = service.get_product_by_id(db, product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ProductFullResponse(
        id=product.id,
        product_id=product.product_id,
        name=product.name,
        category=product.category,
        attributes=[
            {
                "attribute_name": attr.attribute_name,
                "attribute_type": attr.attribute_type,
                "attribute_value": attr.attribute_value,
                "unit": attr.unit,
                "display_name": attr.display_name
            }
            for attr in product.attributes
        ],
        visual_assets=[
            {
                "asset_type": asset.asset_type,
                "asset_url": asset.asset_url,
                "metadata": asset.metadata
            }
            for asset in product.visual_assets
        ]
    )

