# ============================================================
# PART 1 — IMPORTS AND ENVIRONMENT
# ============================================================

import os
import time
from google import genai
from google.genai import errors
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY must be set in .env")

# ============================================================
# PART 2 — CLIENT SETUP
# ============================================================

# Initialize the standard Gemini client (removed HttpOptions)
client = genai.Client(api_key=GEMINI_API_KEY)

# ============================================================
# PART 3 — MODEL FALLBACK CHAIN
# ============================================================

FALLBACK_MODELS = [
    "gemini-3.5-flash-lite",     
    "gemini-3.1-flash-lite",     
]


# ============================================================
# PART 3 — STRICT SYSTEM PROMPT
# ============================================================

STRICT_SYSTEM_PROMPT = """
You are a specialized SVG code generator for educational science diagrams.
Your ONLY job is to output raw, valid, animated SVG code.
Do not overthink. Do not write long explanations. Output the code immediately.

RULES:
1. Output ONLY the <svg> tag and its contents. No markdown formatting (no ```xml), no HTML, no explanations.
2. The SVG must have a valid viewBox attribute (e.g., viewBox="0 0 800 600").
3. The SVG must contain a <title> element.
4. The SVG must contain at least 3 <text> elements for labels.
5. The SVG must contain at least one animation. Use CSS inside a <style> tag (e.g., @keyframes) or SMIL (e.g., <animate>).
6. Do not use external images or URLs. Everything must be self-contained.
7. Use a solid WHITE background (<rect width="100%" height="100%" fill="white" />) for the diagram. Use high-contrast colors so it is easily readable for students.
"""

# ============================================================
# PART 4 — THE API CALL WITH FALLBACK
# ============================================================

def ask_llm_for_svg(prompt_text, previous_error=None):
    user_prompt = f"Create an animated SVG diagram for this concept: {prompt_text}"
    
    if previous_error:
        user_prompt += f"\n\nYOUR PREVIOUS ATTEMPT FAILED VALIDATION: {previous_error}. You MUST fix this in your new SVG."

    for model_name in FALLBACK_MODELS:
        for attempt in range(2):
            try:
                print(f"  -> Asking {model_name} (Attempt {attempt + 1})...")
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config={'system_instruction': STRICT_SYSTEM_PROMPT}
                )
                
                return {
                    "success": True,
                    "svg_text": response.text,
                    "input_tokens": response.usage_metadata.prompt_token_count,
                    "output_tokens": response.usage_metadata.candidates_token_count,
                    "model_used": model_name
                }
                
            except errors.APIError as e:
                if e.code in [429, 503, 500, 404]:
                    print(f"  ⚠️ {model_name} failed ({e.code}).")
                    if attempt == 0:
                        time.sleep(2)
                    else:
                        break 
                else:
                    return {"success": False, "error": f"Fatal API Error: {e}"}
                    
            except Exception as e:
                return {"success": False, "error": f"Unknown error: {str(e)}"}

    return {"success": False, "error": "All fallback models failed."}