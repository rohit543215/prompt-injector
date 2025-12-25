from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simple_pii_model import SimplePIIProcessor
from prompt_protector import PromptProtector
import uvicorn

app = FastAPI(
    title="PII Detection and Masking API",
    description="Neural Network-based PII detection and masking system",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global PII processor instance
pii_processor = None
prompt_protector = None

# Pydantic models
class TextInput(BaseModel):
    text: str

class MaskRequest(BaseModel):
    text: str

class UnmaskRequest(BaseModel):
    masked_text: str
    session_data: Dict

class ChatbotRequest(BaseModel):
    user_message: str

class ChatbotResponse(BaseModel):
    masked_message: str
    session_data: Dict
    detected_pii: List[Dict]

class AnalysisResponse(BaseModel):
    original_text: str
    masked_text: str
    detected_entities: List[Dict]
    pii_count: int
    pii_types: List[str]
    mask_info: List[Dict]

class PromptProtectionRequest(BaseModel):
    prompt: str
    num_alternatives: Optional[int] = 3

class PromptProtectionResponse(BaseModel):
    original_prompt: str
    protected_prompt: str
    protection_applied: bool
    detected_pii: List[Dict]
    replacements_made: List[Dict]
    suggestions: List[str]
    context: str
    risk_level: str
    pii_count: int
    pii_types: List[str]
    alternatives: Optional[List[str]] = None

def get_pii_processor():
    global pii_processor
    if pii_processor is None:
        pii_processor = SimplePIIProcessor()
    return pii_processor

def get_prompt_protector():
    global prompt_protector
    if prompt_protector is None:
        prompt_protector = PromptProtector()
    return prompt_protector

@app.on_event("startup")
async def startup_event():
    """Initialize the PII processor on startup"""
    global pii_processor, prompt_protector
    pii_processor = SimplePIIProcessor()
    prompt_protector = PromptProtector()
    print("PII Detection API started with simple rule-based model!")
    print("Prompt Protection system initialized!")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "PII Detection and Masking API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": True,
        "model_type": "Rule-based + spaCy",
        "supported_pii_types": [
            "PERSON", "EMAIL", "PHONE", "SSN", "CREDIT_CARD",
            "ADDRESS", "DATE", "ORGANIZATION", "LOCATION", 
            "IP_ADDRESS", "URL", "BANK_ACCOUNT"
        ]
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(request: TextInput):
    """Analyze text for PII entities"""
    try:
        processor = get_pii_processor()
        analysis = processor.analyze_text(request.text)
        return AnalysisResponse(**analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/mask")
async def mask_text(request: MaskRequest):
    """Mask PII in text"""
    try:
        processor = get_pii_processor()
        masked_text, session_data = processor.process_for_chatbot(request.text)
        return {
            "masked_text": masked_text,
            "session_data": session_data,
            "detected_entities": session_data["detected_entities"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Masking failed: {str(e)}")

@app.post("/unmask")
async def unmask_text(request: UnmaskRequest):
    """Unmask PII in text"""
    try:
        processor = get_pii_processor()
        unmasked_text = processor.process_chatbot_response(
            request.masked_text, 
            request.session_data
        )
        return {"unmasked_text": unmasked_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unmasking failed: {str(e)}")

@app.post("/chatbot/process", response_model=ChatbotResponse)
async def process_for_chatbot(request: ChatbotRequest):
    """Process user message before sending to chatbot"""
    try:
        processor = get_pii_processor()
        masked_text, session_data = processor.process_for_chatbot(request.user_message)
        
        return ChatbotResponse(
            masked_message=masked_text,
            session_data=session_data,
            detected_pii=[
                {
                    "text": entity[0],
                    "type": entity[1],
                    "confidence": entity[2]
                } for entity in session_data["detected_entities"]
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/chatbot/response")
async def process_chatbot_response(request: dict):
    """Process chatbot response to restore PII"""
    try:
        processor = get_pii_processor()
        chatbot_response = request.get("chatbot_response", "")
        session_data = request.get("session_data", {})
        
        final_response = processor.process_chatbot_response(chatbot_response, session_data)
        
        return {"final_response": final_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response processing failed: {str(e)}")

@app.get("/demo/sample-texts")
async def get_sample_texts():
    """Get sample texts for demo purposes"""
    return {
        "samples": [
            {
                "title": "Email Sample",
                "text": "Hi John Smith, please contact me at john.doe@email.com or call 555-123-4567. My address is 123 Main St, New York, NY."
            },
            {
                "title": "Business Card",
                "text": "Jane Wilson, CEO of TechCorp Inc. Email: jane.wilson@techcorp.com, Phone: (555) 987-6543, Located in San Francisco, CA."
            },
            {
                "title": "Financial Info",
                "text": "Please process payment using card 4532-1234-5678-9012 or transfer to account GB82-WEST-1234-5698-7654-32 by 2024-12-31."
            },
            {
                "title": "Personal Details",
                "text": "Patient: Mary Johnson, DOB: 1985-03-15, SSN: 123-45-6789, Address: 456 Oak Avenue, Chicago, IL 60601."
            }
        ]
    }

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    processor = get_pii_processor()
    return {
        "total_masks_stored": len(processor.masker.mask_store),
        "supported_pii_types": 12,
        "model_name": "Simple Rule-based + spaCy",
        "mask_templates": processor.masker.mask_templates
    }

@app.post("/protect-prompt", response_model=PromptProtectionResponse)
async def protect_prompt(request: PromptProtectionRequest):
    """Generate a privacy-protected version of a prompt"""
    try:
        protector = get_prompt_protector()
        result = protector.generate_protected_prompt(request.prompt)
        
        # Add alternatives if requested
        if request.num_alternatives and request.num_alternatives > 0:
            alternatives = protector.generate_alternative_prompts(
                request.prompt, 
                request.num_alternatives
            )
            result['alternatives'] = alternatives
        
        return PromptProtectionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prompt protection failed: {str(e)}")

@app.post("/analyze-prompt-risk")
async def analyze_prompt_risk(request: TextInput):
    """Analyze privacy risk level of a prompt"""
    try:
        protector = get_prompt_protector()
        result = protector.generate_protected_prompt(request.text)
        
        return {
            "risk_level": result['risk_level'],
            "pii_count": result['pii_count'],
            "pii_types": result['pii_types'],
            "context": result['context'],
            "suggestions": result['suggestions'][:3],  # Top 3 suggestions
            "protection_needed": result['protection_applied']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")

@app.get("/prompt-examples")
async def get_prompt_examples():
    """Get example prompts showing before/after protection"""
    return {
        "examples": [
            {
                "category": "Email Writing",
                "original": "Write an email to John Smith at john.smith@company.com about the quarterly report. His phone is 555-123-4567.",
                "protected": "Write an email to Alex Johnson at user@example.com about the quarterly report. His phone is 555-0123.",
                "risk_level": "MEDIUM"
            },
            {
                "category": "Data Analysis",
                "original": "Analyze customer data for Sarah Wilson, account #123456789, living at 456 Oak St, Chicago.",
                "protected": "Analyze customer data for Customer A, account #XXXX-XXXX-1234, living at 123 Main Street, Anytown, ST 12345.",
                "risk_level": "HIGH"
            },
            {
                "category": "Customer Service",
                "original": "Help resolve complaint from Mike Johnson (mike.j@email.com) about his order #ORD-789.",
                "protected": "Help resolve complaint from Customer B (contact@example.com) about his order #ORD-789.",
                "risk_level": "LOW"
            },
            {
                "category": "Safe Prompt",
                "original": "Explain how to write effective marketing copy for a tech product.",
                "protected": "Explain how to write effective marketing copy for a tech product.",
                "risk_level": "LOW"
            }
        ]
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )