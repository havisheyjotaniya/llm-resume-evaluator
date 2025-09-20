# Lightweight LLM Resume Evaluator

A tiny, transparent resume evaluator that compares a candidate resume to a job description against a clear rubric, returning structured JSON + actionable feedback.

## Features
- OpenAI or Local (Ollama) — choose your provider.
- Strict JSON outputs for easy logging or dashboards.
- PDF extraction built-in (pypdf).
- Transparent prompts — view the exact prompt sent.

## Quickstart
1. **Clone** and create a venv
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Configure**
   - For OpenAI: set `OPENAI_API_KEY` in `.env` (copy from `.env.example`).
   - For Ollama: install [Ollama](https://ollama.com), pull a model (e.g., `ollama pull llama3.1:8b`).
3. **Run**
   ```bash
   streamlit run app.py
   ```
4. **Use**
   - Paste a JD, provide resume text or upload a PDF, select provider/model, click **Evaluate**.

## Output Contract
The app expects the model to return JSON like:
```json
{
  "dimensions": [
    {"name": "Alignment", "score": 4, "evidence": "…"},
    {"name": "Skills Match", "score": 5, "evidence": "…"},
    {"name": "Experience Level", "score": 3, "evidence": "…"},
    {"name": "Keywords", "score": 4, "evidence": "…"},
    {"name": "Clarity", "score": 4, "evidence": "…"}
  ],
  "overall": {
    "score": 82,
    "recommended_action": "consider",
    "summary": "…"
  },
  "suggested_improvements": [
    "Add metrics to project X",
    "Surface Python + SQL in top skills",
    "Match phrasing of JD keywords"
  ]
}
```

## Notes
- If JSON parsing fails, lower temperature or try a different model.
- You can tweak `prompts.py` to change the rubric or dimensions.

## License
MIT
