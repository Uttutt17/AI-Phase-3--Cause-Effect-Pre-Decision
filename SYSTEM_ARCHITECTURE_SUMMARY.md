# System Architecture Summary - Key Questions Answered

## Question 1: How are Product Data + Cause-Effect Logic Structured?

### Product Data Structure

**Hierarchical Structure:**
```
Product
├── Basic Info (id, name, category)
├── Attributes (price, weight, battery_life, material, etc.)
└── Visual Assets (images, spec callouts)
```

**Key Points:**
- Attributes are **pre-defined** in a structured database
- Each attribute has metadata: type, unit, display_name
- Attributes are **never invented** by AI - they exist in the database
- Product data is version-controlled and validated

### Cause-Effect Logic Structure

**Three-Layer Mapping:**

```
Layer 1: Intent Detection
  ↓
Layer 2: Intent → Attribute Mapping (Rule-Based)
  ↓
Layer 3: Attributes → Visual Effects
```

**Example Flow:**
```
User: "Compare AirPods Max vs AirPods Pro"
  ↓
Intent: COMPARE
  ↓
Mapping: compare → [price, weight, battery_life, noise_cancellation, usage_context]
  ↓
Visual Effects: [split_screen, highlight_differences]
```

**Implementation:**
- **Configuration-Based**: Intent mappings stored in config files (JSON/YAML)
- **Rule Engine**: Simple if-then rules, not ML-based
- **Validation**: System checks attributes exist before applying effects
- **Extensible**: New intents can be added by updating configuration

**Key Principle:**
> The cause-effect logic is **deterministic** and **rule-based**, not AI-generated. The AI only selects which existing rules to apply based on user intent.

---

## Question 2: Where Do Pre-Decision Checks Live in the System?

### System Location

**Primary Location:** Integrated into the **CHOOSE intent handler**

**File Structure:**
```
src/
├── intents/
│   └── choose_handler.py  ← Main entry point
│
├── checks/  ← Pre-decision check modules
│   ├── attribute_completeness.py
│   ├── user_context.py
│   ├── visualization_ready.py
│   └── decision_confidence.py
```

### When Pre-Decision Checks Execute

**Trigger Point:**
```
User Query → Intent Detection (CHOOSE) → [PRE-DECISION CHECKS] → Attribute Selection
```

**Check Sequence:**
1. **Attribute Completeness Check** - First
   - Validates required attributes exist in database
   - Returns missing attributes if incomplete
   
2. **User Context Validation** - Second
   - Validates user's use case matches available attributes
   - Checks if usage_context attributes exist
   
3. **Visualization Readiness Check** - Third
   - Ensures visual assets (images, callouts) are available
   - Validates product images exist
   
4. **Decision Confidence Score** - Final
   - Calculates overall readiness score
   - Determines if system can proceed or needs clarification

### Check Flow Logic

```python
def handle_choose_intent(user_query, products):
    # Step 1: Pre-decision checks
    checks_result = run_pre_decision_checks(user_query, products)
    
    if not checks_result.passed:
        # Return clarification request
        return request_clarification(checks_result.missing_items)
    
    # Step 2: Proceed with attribute selection and visualization
    attributes = select_attributes(checks_result.validated_intent)
    visualization = apply_visual_effects(attributes)
    
    return visualization
```

### Integration Points

1. **Before Attribute Selection**: Checks run BEFORE any attributes are selected
2. **Before Visualization**: Checks ensure visualization is possible
3. **In CHOOSE Intent Only**: Pre-decision checks are specific to purchase decision context
4. **Error Handling**: Failed checks trigger clarification requests, not errors

**Key Point:**
> Pre-decision checks are **gatekeepers** that ensure the system has everything needed before proceeding with visualization and explanation.

---

## Question 3: How is ChatGPT Used Purely as an Explanation Layer?

### Architecture: Read-Only Explanation Layer

**ChatGPT's Role:**
- ✅ **DOES**: Explain why attributes were selected
- ✅ **DOES**: Describe what visual effects show
- ✅ **DOES**: Provide natural language context
- ❌ **DOES NOT**: Generate product data
- ❌ **DOES NOT**: Create new attributes
- ❌ **DOES NOT**: Make decisions
- ❌ **DOES NOT**: Query the database

### Data Flow

```
[Product Database] → [Intent Engine] → [Attribute Selection] → 
[Visualization Applied] → [Structured Output] → 
[ChatGPT Explanation Layer] → [Natural Language Response]
```

**Critical Boundary:**
```
┌─────────────────────────────────────┐
│  Product Data & Logic Layer         │
│  (Source of Truth)                  │
└─────────────────────────────────────┘
              ↓ (Read-Only)
┌─────────────────────────────────────┐
│  ChatGPT Explanation Layer          │
│  (Reads structured output only)     │
└─────────────────────────────────────┘
```

### What ChatGPT Receives

**Input (Structured Data Only):**
```json
{
  "user_intent": "compare",
  "selected_attributes": {
    "price": 549,
    "weight": 384,
    "battery_life": 20
  },
  "visual_effects_applied": ["split_screen", "highlight_differences"],
  "products": ["AirPods Max", "AirPods Pro"]
}
```

**Output (Explanation Only):**
```
"I'm showing you a side-by-side comparison of AirPods Max and AirPods Pro. 
I've highlighted the key differences: price ($549 vs $249), weight (384g vs 56g), 
and battery life (20 hours vs 6 hours). The split screen view makes it easy 
to compare these attributes side by side."
```

### Implementation Structure

**File Organization:**
```
src/
├── explanation/
│   ├── chatgpt_explainer.py      ← Main explanation generator
│   ├── attribute_explainer.py     ← Attribute-specific explanations
│   ├── comparison_summary.py     ← Comparison explanations
│   └── prompt_templates.py       ← Prompt templates
│
├── api/
│   └── chatgpt_client.py         ← OpenAI API wrapper
```

### Prompt Engineering Strategy

**Template Structure:**
```
You are explaining product attributes to a user.

DO NOT:
- Invent or guess product data
- Make recommendations
- Create new attributes
- Access product database

DO:
- Explain why these specific attributes were selected
- Describe what the visual effects show
- Use ONLY the exact attribute values provided below

[Structured Data Inserted Here]

Provide a clear, helpful explanation.
```

### Validation & Safety

1. **Input Validation**: Only structured data passed to ChatGPT
2. **Output Validation**: Responses checked against source data
3. **Logging**: All ChatGPT inputs/outputs logged for audit
4. **Error Handling**: If ChatGPT response contains invented data, fallback to template-based explanation

### Key Principles

1. **No Database Access**: ChatGPT never queries product database
2. **No Data Generation**: ChatGPT never creates new attributes or values
3. **Read-Only**: ChatGPT only reads structured output from logic layer
4. **Explanation Only**: ChatGPT's sole purpose is natural language explanation
5. **Structured Input**: All data passed to ChatGPT is pre-structured and validated

**Critical Rule:**
> ChatGPT is a **translator** that converts structured system output into natural language. It does NOT participate in data selection, logic, or decision-making.

---

## Summary: System Boundaries

```
┌─────────────────────────────────────────────────────────┐
│  PRODUCT DATA LAYER                                     │
│  - Structured database                                  │
│  - Pre-defined attributes                               │
│  - Visual assets                                        │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│  CAUSE-EFFECT LOGIC LAYER                               │
│  - Intent detection                                     │
│  - Intent → Attribute mapping (rule-based)             │
│  - Attribute → Visual effect mapping                     │
│  - Pre-decision checks (in CHOOSE intent)              │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│  VISUALIZATION LAYER                                    │
│  - Split screen, highlight, zoom, labels                │
│  - Visual effects applied                               │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│  CHATGPT EXPLANATION LAYER (READ-ONLY)                  │
│  - Receives structured output                           │
│  - Generates natural language explanation               │
│  - NO database access                                   │
│  - NO data generation                                    │
└─────────────────────────────────────────────────────────┘
```

---

**Document Version**: 1.0  
**Based on**: Akari Phase 3 Clarification 2 PDF

