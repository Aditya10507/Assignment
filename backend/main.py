# ============================================================
# PART 1 — IMPORTS AND SETUP
# ============================================================

import json
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.generate import router as generate_router

app = FastAPI(title="Udhi Science Diagram Maker")

# Allow the frontend to talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# PART 2 — API ROUTES
# ============================================================

# Hook up the /api/generate route we wrote in routes/generate.py
app.include_router(generate_router, prefix="/api")

@app.get("/api/results")
def get_saved_results():
    """
    Reads the results.json file and sends it to the frontend.
    This allows the table to load instantly with no API calls to Gemini.
    """
    filepath = "data/results.json"
    if not os.path.exists(filepath):
        return []
        
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# ============================================================
# PART 3 — SERVE THE FRONTEND
# ============================================================

# This MUST be at the bottom. It tells FastAPI to serve the HTML/CSS/JS 
# files from the 'frontend' folder at the root URL (e.g., localhost:8000/)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")