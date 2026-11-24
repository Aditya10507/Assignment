
# Udhi Science Diagram Maker

A small web application that asks an AI model to generate 5 animated science diagrams, validates each diagram using code, and allows a reviewer to approve or reject them.

## 🚀 How to Run It on Your Computer

### 1. Clone the Repository

Clone the repository and open the project folder in your terminal.

### 2. Create and Activate a Virtual Environment

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
.\venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

Install the required dependencies:

```bash
uv pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory of the project and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual Gemini API key.

### 5. Generate the Diagrams (Part A)

Run the diagram generation script:

```bash
python scripts/generate_all.py
```

This will:

- Run the AI-powered diagram generation pipeline.
- Generate animated SVG diagrams.
- Validate the generated SVGs.
- Save the final results to `data/results.json`.

### 6. Run the Web Application (Part B)

Start the FastAPI application:

```bash
uvicorn backend.main:app --reload
```

Open the application in your browser:

[http://localhost:8000](http://localhost:8000)

---

## 📊 Results Table

The following table shows the results of the diagram generation and validation process.

| Concept | Pass/Fail | Estimated Cost (USD) | Retries |
|---|---|---:|---:|
| Pythagoras' theorem | PASS | $0.001095 | 0 |
| Parts of a circle | PASS | $0.001543 | 0 |
| Series circuit | PASS | $0.001058 | 0 |
| Photosynthesis | PASS | $0.002307 | 0 |
| States of matter | PASS | $0.002384 | 0 |

**Note:** Costs are calculated using Gemini Flash Lite input/output token pricing. The free tier was used, but the application logs the estimated cost as if it were a paid tier.

---

## 🛠️ What Failed and How I Fixed It

### 1. Heavy API Rate Limits and 503 Errors

**Problem:**

The free tier of the Gemini API frequently returned `503 Service Unavailable` errors when using heavier models due to server overloads.

Retrying the same request repeatedly did not solve the problem.

**Solution:**

I implemented a **Fallback Model Chain** in `llm.py`.

- The application strictly uses `gemini-3.5-flash-lite` and `gemini-3.1-flash-lite`.
- It automatically switches between these models if one fails.
- I also implemented exponential backoff, which increases the waiting time between retries to respect API limits and reduce repeated failures.

### 2. Strict SVG Validation False Positives

**Problem:**

The AI generated visually correct SVG diagrams, but my Python validator was rejecting them.

The custom "no external resources" check was incorrectly blocking standard SVG namespace declarations such as:

```xml
xmlns="http://www.w3.org/2000/svg"
```

The `viewBox` checker also struggled with percentages and `<path>` elements.

**Solution:**

I rewrote `validate_svg.py` using regular expressions that:

- Ignore the standard SVG namespace.
- Continue blocking actual malicious external images and scripts.
- Handle valid SVG structures more reliably.
- Relax the `viewBox` boundary checks to account for valid CSS transforms.

### 3. Persistent Review States

**Problem:**

The assignment required Approve/Reject decisions to remain saved after refreshing the page, without introducing a database.

**Solution:**

I used the browser's `localStorage` to persist the review states.

This approach was chosen because:

- It requires zero backend infrastructure.
- Review decisions are saved instantly.
- States survive page refreshes.
- It avoids the complexity of introducing a database for a simple review workflow.

---

## 🚀 What I Would Do with One More Day

### 1. Pixel-Perfect SVG Validation

Instead of relying on regular expressions and string-based validation, I would use a headless browser such as Playwright to render the SVGs and check whether any pixels are drawn outside the `viewBox`.

### 2. Real Database Integration

I would move the Approve/Reject states from `localStorage` to a real database such as PostgreSQL.

This would allow multiple reviewers to collaborate and share their decisions and notes in real time.

### 3. Better Prompting

I would introduce multi-shot prompting with examples of good and bad SVG diagrams.

This would help ensure that the AI consistently generates diagrams with the required GCSE-level educational labels.

### 4. UI Improvements

I would add a **Download SVG** button so teachers can easily export the generated diagrams and use them in their presentations and educational slide decks.

---

## 🧠 AI Tools Used and Their Purpose

### DeepSeek

DeepSeek was used for coding assistance.

It helped me:

- Structure the FastAPI backend.
- Debug Pydantic validation errors in the Gemini SDK.
- Write and improve the CSS for the hover-zoom effect.

### Gemini API

The Gemini API is used at runtime as the core AI engine of the application.

It generates the actual animated SVG science diagrams based on the provided concepts.

---

## 📝 Conclusion

Udhi Science Diagram Maker combines AI-powered SVG generation, automated code-based validation, and a simple human review workflow to create educational science diagrams.

The project demonstrates how AI models can be integrated into a practical web application while handling API failures, validating generated content, and maintaining persistent review states without requiring a database.
