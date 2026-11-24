# ============================================================
# PART 1 — IMPORTS
# ============================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.lib.concepts import CONCEPTS
from backend.lib.generate_diagram import generate_and_validate

# ============================================================
# PART 2 — SETUP
# ============================================================

router = APIRouter()

# This defines what data the frontend must send us. 
# It just needs the ID of the concept they want to generate.
class GenerateRequest(BaseModel):
    concept_id: int

# ============================================================
# PART 3 — THE ENDPOINT
# ============================================================

@router.post("/generate")
def generate_live(request: GenerateRequest):
    """
    Takes a concept ID from the frontend, runs the AI pipeline, and returns the result.
    """
    # Find the concept that matches the requested ID
    concept = next((c for c in CONCEPTS if c["id"] == request.concept_id), None)
    
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    # Run the pipeline (API call + validation + retries)
    result = generate_and_validate(concept)
    
    # If the API failed completely, send an error code so the frontend can show a message
    if "api_error" in result:
        raise HTTPException(status_code=500, detail=result["api_error"])
        
    return result