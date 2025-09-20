import os
import io
import json
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from dotenv import load_dotenv

load_dotenv()

try:
    from pypdf import PdfReader  # lightweight PDF text extractor
except Exception:  # pragma: no cover
    PdfReader = None

try:
    import openai  # OpenAI official SDK v1+
except Exception:  # pragma: no cover
    openai = None

import requests

JSON_SCHEMA_NOTE = (
    "Return ONLY a valid JSON object. Do not include markdown fences, backticks, or prose."
)


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    if PdfReader is None:
        raise RuntimeError("pypdf not installed. Add it to requirements.txt and reinstall.")
    reader = PdfReader(io.BytesIO(pdf_bytes))
    texts = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return "\n".join(texts).strip()


@dataclass
class LLMClient:
    provider: str
    model: str
    temperature: float = 0.2
    max_tokens: int = 1200

    def _openai_chat(self, messages):
        if openai is None:
            raise RuntimeError("openai package not installed.")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set.")
        client = openai.OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
        )
        return resp.choices[0].message.content

    def _ollama_chat(self, messages):
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        url = f"{host}/api/chat"
        payload = {
            "model": self.model,
            "messages": [{"role": m["role"], "content": m["content"]} for m in messages],
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data.get("message", {}).get("content", "")

    def chat(self, messages):
        if self.provider == "openai":
            return self._openai_chat(messages)
        elif self.provider == "ollama":
            return self._ollama_chat(messages)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")


def build_prompt(job_description: str, resume_text: str, rubric: Dict) -> str:
    return f"""
You are an expert technical recruiter and hiring manager. Follow the rubric strictly.

# Job Description
{job_description}

# Candidate Resume
{resume_text}

# Rubric (immutable)
{json.dumps(rubric, indent=2)}

# Output JSON Schema (immutable)
{{
  "dimensions": [
    {{"name": "Alignment", "score": 0, "evidence": ""}},
    {{"name": "Skills Match", "score": 0, "evidence": ""}},
    {{"name": "Experience Level", "score": 0, "evidence": ""}},
    {{"name": "Keywords", "score": 0, "evidence": ""}},
    {{"name": "Clarity", "score": 0, "evidence": ""}}
  ],
  "overall": {{
    "score": 0,   
    "recommended_action": "reject | consider | strong_consider",
    "summary": ""
  }},
  "suggested_improvements": ["short actionable bullets…"]
}}

{JSON_SCHEMA_NOTE}
""".strip()


def safe_json_loads(text: str) -> Optional[Dict]:
    try:
        return json.loads(text)
    except Exception:
        # try to salvage by trimming codefences or stray backticks
        cleaned = (
            text.strip()
            .removeprefix("```json").removesuffix("```")
            .removeprefix("```").removesuffix("```")
            .strip()
        )
        try:
            return json.loads(cleaned)
        except Exception:
            return None


def score_resume_against_jd(
    client: LLMClient,
    job_description: str,
    resume_text: str,
    rubric: Dict,
    system_instructions: str,
) -> Tuple[str, str]:
    user_prompt = build_prompt(job_description, resume_text, rubric)
    messages = [
        {"role": "system", "content": system_instructions},
        {"role": "user", "content": user_prompt},
    ]
    content = client.chat(messages)
    return content, user_prompt
