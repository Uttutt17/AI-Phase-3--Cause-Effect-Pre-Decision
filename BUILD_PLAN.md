# Akari Phase 3 - Build Plan

## Executive Summary

This document outlines the build plan for Akari Phase 3, based on the clarification document. The system is designed to help users make informed product decisions through intent-based visualization and explanation, with ChatGPT serving purely as an explanation layer.

---

## 1. System Architecture Overview

### Core Components:
1. **Intent Detection Engine** - Detects user intent (compare/explain/clarify/choose)
2. **Product Data Layer** - Structured product database with attributes
3. **Cause-Effect Logic Engine** - Maps intents to attributes and visual triggers
4. **Pre-Decision Check System** - Validates user readiness before decision
5. **Visualization Engine** - Renders visual triggers (highlight/zoom/split/label)
6. **ChatGPT Explanation Layer** - Provides natural language explanations (read-only)

---

## 2. Product Data + Cause-Effect Logic Structure

### 2.1 Product Data Schema

```json
{
  "product_id": "string",
  "name": "string",
  "attributes": {
    "price": "number",
    "weight": "number",
    "battery_life": "number",
    "noise_cancellation": "number",
    "material": "string",
    "build_quality": "string",
    "driver_type": "string",
    "noise_cancellation_level": "string",
    "clamp_force": "number",
    "padding_material": "string",
    "foldability": "boolean",
    "case_size": "string",
    "usage_context": ["string"]
  },
  "visual_assets": {
    "main_image": "url",
    "detail_images": ["url"],
    "spec_callouts": ["url"]
  }
}
```

### 2.2 Cause-Effect Logic Structure

The cause-effect logic is structured as **Intent → Attribute Mapping → Visual Effect**:

#### Intent Types:
1. **COMPARE** - Compare two or more products
2. **EXPLAIN** - Explain why a product has certain characteristics
3. **CLARIFY** - Clarify fit/size/comfort concerns
4. **CHOOSE** - Pre-decision support for purchase decisions

#### Mapping Structure:

```javascript
const intentMappings = {
  "compare": {
    attributes: ["price", "weight", "battery_life", "noise_cancellation", "usage_context"],
    visual_effects: ["split_screen", "highlight_differences"]
  },
  "explain_price": {
    attributes: ["material", "build_quality", "driver_type", "noise_cancellation_level"],
    visual_effects: ["highlight_materials", "zoom_earcup_frame", "show_spec_callouts"]
  },
  "clarify_comfort": {
    attributes: ["weight", "clamp_force", "padding_material"],
    visual_effects: ["weight_label", "comfort_indicator", "comparison_vs_lighter"]
  },
  "usage_context": {
    attributes: ["weight", "foldability", "battery_life", "case_size"],
    visual_effects: ["highlight_travel_specs", "dim_irrelevant_specs"]
  }
}
```

### 2.3 Implementation Approach

**Data Layer:**
- Store product data in structured database (PostgreSQL/JSON)
- Maintain attribute catalog with metadata (type, unit, display_name)
- Version control for product data updates

**Logic Engine:**
- Rule-based mapping system (intent → attributes → effects)
- Extensible configuration file for new intents
- Validation layer to ensure attributes exist before mapping

**Key Principle:** 
> AI does NOT invent data. AI only selects + visualizes existing attributes based on user intention.

---

## 3. Pre-Decision Checks Location

### 3.1 System Location

Pre-decision checks are integrated into the **CHOOSE intent flow**, which is triggered when:
- User indicates purchase intent (e.g., "Which one is better for travel?")
- System detects decision-making context

### 3.2 Pre-Decision Check Components

#### 3.2.1 Check Points:

1. **Attribute Completeness Check**
   - Location: `src/checks/attribute_completeness.py`
   - Validates all required attributes are available for comparison
   - Returns missing attributes list if incomplete

2. **User Context Validation**
   - Location: `src/checks/user_context.py`
   - Validates user's stated use case matches available product attributes
   - Checks if usage_context attributes exist

3. **Visualization Readiness Check**
   - Location: `src/checks/visualization_ready.py`
   - Ensures all required visual assets exist
   - Validates product images and spec callouts are available

4. **Decision Confidence Score**
   - Location: `src/checks/decision_confidence.py`
   - Calculates confidence based on:
     - Attribute coverage percentage
     - User question clarity
     - Available comparison data

#### 3.2.2 Flow Integration:

```
User Query → Intent Detection (CHOOSE) → Pre-Decision Checks → 
  ├─ If checks pass → Attribute Selection → Visualization
  └─ If checks fail → Request clarification or show available options
```

### 3.3 Implementation Structure

```
src/
├── checks/
│   ├── __init__.py
│   ├── attribute_completeness.py
│   ├── user_context.py
│   ├── visualization_ready.py
│   └── decision_confidence.py
├── intents/
│   ├── choose_handler.py  # Contains pre-decision logic
│   └── ...
```

---

## 4. ChatGPT as Pure Explanation Layer

### 4.1 Architecture Principle

**ChatGPT is read-only and explanation-only.** It does NOT:
- Generate product data
- Create attributes
- Make decisions
- Modify visualizations

### 4.2 Implementation Structure

#### 4.2.1 Data Flow:

```
Product Data (Structured) → Intent Engine → Attribute Selection → 
Visualization → [Structured Output] → ChatGPT Explanation Layer → 
Natural Language Response
```

#### 4.2.2 ChatGPT Integration Points:

1. **Post-Visualization Explanation**
   - Location: `src/explanation/chatgpt_explainer.py`
   - Input: Selected attributes + visual effects applied
   - Output: Natural language explanation of why these attributes were shown
   - Example: "I'm highlighting the weight and foldability because you mentioned travel..."

2. **Attribute Context Explanation**
   - Location: `src/explanation/attribute_explainer.py`
   - Input: Specific attribute values + user question
   - Output: Explanation of what the attribute means in context
   - Example: "The 384g weight means..."

3. **Comparison Summary**
   - Location: `src/explanation/comparison_summary.py`
   - Input: Two products + selected attributes + differences
   - Output: Natural language comparison summary
   - Example: "AirPods Max is heavier but offers better noise cancellation..."

#### 4.2.3 Prompt Engineering:

```python
def generate_explanation_prompt(selected_attributes, visual_effects, user_intent):
    return f"""
    You are explaining product attributes to a user. 
    
    DO NOT:
    - Invent or guess product data
    - Make recommendations
    - Create new attributes
    
    DO:
    - Explain why these specific attributes were selected
    - Describe what the visual effects show
    - Use the exact attribute values provided
    
    User Intent: {user_intent}
    Selected Attributes: {selected_attributes}
    Visual Effects Applied: {visual_effects}
    
    Provide a clear, helpful explanation.
    """
```

#### 4.2.4 Data Isolation:

- ChatGPT receives **only**:
  - Selected attribute names and values (from database)
  - Applied visual effects
  - User intent type
  
- ChatGPT receives **never**:
  - Raw product database access
  - Ability to query new attributes
  - Decision-making authority

### 4.3 Implementation Files:

```
src/
├── explanation/
│   ├── __init__.py
│   ├── chatgpt_explainer.py
│   ├── attribute_explainer.py
│   ├── comparison_summary.py
│   └── prompt_templates.py
├── api/
│   └── chatgpt_client.py  # Wrapper for OpenAI API
```

---

## 5. Detailed Build Plan

### Phase 1: Foundation (Weeks 1-2)

#### 1.1 Product Data Layer
- [ ] Design product data schema
- [ ] Set up database (PostgreSQL or JSON file system)
- [ ] Create product data ingestion pipeline
- [ ] Implement attribute catalog with metadata
- [ ] Add data validation layer

#### 1.2 Intent Detection Engine
- [ ] Implement NLP-based intent classifier
- [ ] Create intent types: compare, explain, clarify, choose
- [ ] Build intent → attribute mapping configuration
- [ ] Add intent confidence scoring

### Phase 2: Core Logic (Weeks 3-4)

#### 2.1 Cause-Effect Logic Engine
- [ ] Implement intent → attribute mapping system
- [ ] Create visual effect selection logic
- [ ] Build attribute validation (ensure attributes exist)
- [ ] Add extensible configuration system for new intents

#### 2.2 Pre-Decision Check System
- [ ] Implement attribute completeness check
- [ ] Build user context validation
- [ ] Create visualization readiness check
- [ ] Add decision confidence scoring
- [ ] Integrate checks into CHOOSE intent flow

### Phase 3: Visualization (Weeks 5-6)

#### 3.1 Visualization Engine
- [ ] Implement split screen view (for compare)
- [ ] Build highlight system
- [ ] Create zoom functionality
- [ ] Add label overlay system
- [ ] Implement dimming for irrelevant specs

#### 3.2 Visual Asset Management
- [ ] Set up image storage/retrieval
- [ ] Create spec callout system
- [ ] Build asset validation

### Phase 4: Explanation Layer (Weeks 7-8)

#### 4.1 ChatGPT Integration
- [ ] Set up OpenAI API client
- [ ] Create prompt templates
- [ ] Implement explanation generators:
  - Post-visualization explanation
  - Attribute context explanation
  - Comparison summary
- [ ] Add response validation (ensure no data invention)

#### 4.2 Data Isolation
- [ ] Implement strict input/output boundaries
- [ ] Add logging for all ChatGPT inputs
- [ ] Create validation layer to prevent data generation

### Phase 5: Integration & Testing (Weeks 9-10)

#### 5.1 System Integration
- [ ] Integrate all components
- [ ] Build API endpoints
- [ ] Create frontend interface
- [ ] Add error handling

#### 5.2 Testing
- [ ] Unit tests for each component
- [ ] Integration tests for full flow
- [ ] Test pre-decision checks
- [ ] Validate ChatGPT explanation layer (no data invention)
- [ ] User acceptance testing

---

## 6. Technical Stack Recommendations

### Backend:
- **Language**: Python 3.9+
- **Framework**: FastAPI or Flask
- **Database**: PostgreSQL (for structured data) or JSON files (for MVP)
- **NLP**: spaCy or Transformers for intent detection
- **API Client**: OpenAI Python SDK

### Frontend:
- **Framework**: React or Vue.js
- **Visualization**: D3.js or Three.js for interactive visuals
- **UI Components**: Material-UI or Tailwind CSS

### Infrastructure:
- **Deployment**: Docker containers
- **API Gateway**: nginx or AWS API Gateway
- **Storage**: AWS S3 or local file system for images

---

## 7. Key Design Principles

1. **Data Integrity**: AI never invents data, only selects and visualizes existing attributes
2. **Separation of Concerns**: 
   - Data layer (product database)
   - Logic layer (intent → attribute mapping)
   - Visualization layer (visual effects)
   - Explanation layer (ChatGPT - read-only)
3. **Extensibility**: Easy to add new intents, attributes, and visual effects
4. **Validation**: Multiple checkpoints to ensure data completeness and system readiness
5. **User-Centric**: All decisions based on user intent and context

---

## 8. Success Metrics

- Intent detection accuracy: >90%
- Pre-decision check pass rate: >85%
- ChatGPT explanation relevance: >90% (no hallucinated data)
- User decision confidence improvement: Measured via surveys
- System response time: <2 seconds for intent → visualization

---

## 9. Risk Mitigation

1. **ChatGPT Hallucination**: 
   - Strict prompt engineering
   - Input validation
   - Output validation against source data
   - Logging and monitoring

2. **Missing Product Data**:
   - Pre-decision checks catch missing attributes
   - Graceful degradation (show available attributes)
   - Clear user communication about limitations

3. **Intent Misclassification**:
   - Confidence scoring
   - User confirmation for low-confidence intents
   - Fallback to clarification

---

## 10. Next Steps

1. Review and approve this build plan
2. Set up development environment
3. Create project repository structure
4. Begin Phase 1 implementation
5. Schedule weekly progress reviews

---

**Document Version**: 1.0  
**Last Updated**: Based on "Akari- Phase 3 Clarification 2" PDF  
**Status**: Ready for Implementation

