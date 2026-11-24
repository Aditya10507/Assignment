# ============================================================
# PART 1 — IMPORTS AND SETUP
# ============================================================

import json
import os
import sys

# Add the parent directory to sys.path so we can import from 'backend'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.lib.concepts import CONCEPTS
from backend.lib.generate_diagram import generate_and_validate

# ============================================================
# PART 2 — BATCH GENERATION
# ============================================================

def run_all_concepts():
    all_results = []
    
    for concept in CONCEPTS:
        print(f"\nGenerating: {concept['name']}...")
        
        # Run the pipeline
        result = generate_and_validate(concept)
        all_results.append(result)
        
        if result.get("all_passed"):
            print(f"✅ Success! (Cost: ${result['cost_usd']}, Retries: {result['retries']})")
        else:
            print(f"❌ Failed validation or API error.")

    # ============================================================
    # PART 3 — SAVE TO RESULTS.JSON
    # ============================================================
    
    # Make sure the data folder exists
    os.makedirs("data", exist_ok=True)
    
    with open("data/results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4)
        
    print("\n🎉 Done! All results saved to data/results.json")

if __name__ == "__main__":
    run_all_concepts()