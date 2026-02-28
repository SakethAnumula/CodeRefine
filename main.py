import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import AsyncClient

# --- CONFIGURATION ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("CRITICAL: GROQ_API_KEY is not set in the .env file.")

client = AsyncClient(api_key=GROQ_API_KEY)
app = FastAPI(title="CodeRefine AI Engine")

# --- CORS SETUP ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class CodeRequest(BaseModel):
    code: str

class CodeResponse(BaseModel):
    original_score: int
    refined_score: int
    bugs: str
    performance: str
    improvements: list[str]
    optimized_code: str
    explanation: str
    original_time_complexity: str
    original_space_complexity: str
    time_complexity: str
    space_complexity: str

class TranslateRequest(BaseModel):
    code: str
    target_language: str

# --- SYSTEM PROMPT ---
REVIEW_SYSTEM_PROMPT = """
You are a Senior Algorithm Theorist and Big-O specialist.
Your task is to STRICTLY and MATHEMATICALLY derive complexity and calculate scores.

-------------------------
SCORING ALGORITHM (100 PTS TOTAL)
-------------------------
You must start the user's code at 100 points and deduct based on these strict rules:

1. Logic & Correctness (30 pts):
   - Deduct 10 pts for every logical bug or edge-case failure.
   - Deduct 30 pts if the code does not solve the primary problem.

2. Time/Space Efficiency (25 pts):
   - Deduct 15 pts if the complexity is sub-optimal (e.g., O(n^2) when O(n) exists).
   - Deduct 10 pts for unnecessary object allocations or redundant passes.

3. Security & Safety (15 pts):
   - Deduct 15 pts for vulnerabilities (SQL injection, lack of bounds checking, etc.).
   - Deduct 5 pts for lack of input validation.

4. Readability & Standards (15 pts):
   - Deduct 5 pts for poor variable naming (e.g., a, b, temp).
   - Deduct 5 pts for "God Functions" (functions too long/doing too much).

5. Maintainability (15 pts):
   - Deduct 10 pts for hardcoded values or lack of modularity.

-------------------------
TIME & SPACE COMPLEXITY RULES
-------------------------
1. Identify all loops, recursion, and data structure costs.
2. Use strict Big-O notation (O(n), O(log n), etc.).
3. NEVER use O(?), Unknown, or N/A.
4. return original_time_complexity and original_space_complexity for the user's code.
5. return time_complexity and space_complexity for YOUR optimized version.

-------------------------
CRITICAL OUTPUT RULES
-------------------------
- 'original_score' must be an integer based on the deductions above.
- 'refined_score' must be your optimized version's score (usually 95-100).
- Return ONLY valid JSON. Escape newlines in optimized_code with \\n.

JSON Schema:
{
    "original_score": int,
    "refined_score": int,
    "bugs": "string",
    "performance": "string",
    "improvements": ["string"],
    "optimized_code": "string",
    "explanation": "string",
    "original_time_complexity": "string",
    "original_space_complexity": "string",
    "time_complexity": "string",
    "space_complexity": "string"
}
"""

@app.post("/review", response_model=CodeResponse)
async def review_code(request: CodeRequest):
    try:
        response = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this code and provide full Big O metrics and score:\n\n{request.code}"},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        ai_data = json.loads(response.choices[0].message.content)
        ai_data["original_score"] = int(ai_data.get("original_score", 0))
        ai_data["refined_score"] = int(ai_data.get("refined_score", 0))
        return ai_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate")
async def translate_code(request: TranslateRequest):
    system_prompt = f"Translate to {request.target_language}. Return JSON: {{\"translated_code\": \"string\"}}. Escape quotes/newlines."
    try:
        response = await client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": request.code}],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"translated_code": f"// Translation error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)