# ============================================================
# PART 1 — IMPORTS
# ============================================================

from backend.lib.llm import ask_llm_for_svg
from backend.lib.validate_svg import validate_svg

# ============================================================
# PART 2 — PRICING CONSTANTS
# ============================================================

# Standard pricing for Gemini Flash models (per 1,000,000 tokens)
# Note: If you fall back to Gemma, the actual cost is $0, but this gives a safe estimate.
INPUT_COST_PER_MILLION = 0.10 
OUTPUT_COST_PER_MILLION = 0.40

# ============================================================
# PART 3 — THE PIPELINE
# ============================================================

def generate_and_validate(concept):
    """
    Takes a concept dictionary, asks Gemini for an SVG, validates it, retries once if invalid.
    Returns a fully formatted result dictionary with estimated cost.
    """
    retries = 0
    total_input_tokens = 0
    total_output_tokens = 0
    previous_error = None
    
    # We try a maximum of 2 times (1 initial + 1 retry if validation fails)
    for attempt in range(2):
        
        # 1. Ask the AI (This now automatically handles model fallback)
        api_result = ask_llm_for_svg(concept["prompt_text"], previous_error)
        
        if not api_result["success"]:
            return {
                "concept": concept,
                "api_error": api_result["error"],
                "all_passed": False,
                "retries": retries
            }
            
        total_input_tokens += api_result["input_tokens"]
        total_output_tokens += api_result["output_tokens"]
        
        # 2. Validate the SVG
        validation_result = validate_svg(api_result["svg_text"])
        
        # 3. Calculate estimated cost in USD
        cost = (
            (total_input_tokens / 1_000_000) * INPUT_COST_PER_MILLION
            + (total_output_tokens / 1_000_000) * OUTPUT_COST_PER_MILLION
        )
        
        # 4. If it passed, we are done!
        if validation_result["all_passed"]:
            return {
                "concept": concept,
                "svg": api_result["svg_text"],
                "checks": validation_result["checks_passed"],
                "all_passed": True,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "cost_usd": round(cost, 6), # Save the calculated cost
                "retries": retries,
                "model": api_result["model_used"]
            }
            
        # 5. If it failed validation, prepare error for retry
        else:
            retries += 1
            failed_checks = [name for name, passed in validation_result["checks_passed"].items() if not passed]
            previous_error = f"The following checks failed: {', '.join(failed_checks)}."

    # If we exit the loop, it failed validation twice
    return {
        "concept": concept,
        "svg": api_result["svg_text"],
        "checks": validation_result["checks_passed"],
        "all_passed": False,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "cost_usd": round(cost, 6),
        "retries": retries,
        "model": api_result["model_used"]
    }