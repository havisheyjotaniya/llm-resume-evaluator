import os
import json
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

from utils import (
    LLMClient,
    extract_text_from_pdf,
    score_resume_against_jd,
    safe_json_loads,
)
from prompts import RUBRIC, SYSTEM_INSTRUCTIONS

load_dotenv()

st.set_page_config(page_title="LLM Resume Evaluator", page_icon="🧠", layout="wide")

st.title("🧠 Lightweight LLM Resume Evaluator")
st.caption("Evaluate a resume against a job description using OpenAI or Ollama. Lightweight, transparent, and fast.")

with st.sidebar:
    st.header("Settings")
    provider = st.selectbox("Provider", ["openai", "ollama"], index=0)
    model = st.text_input(
        "Model",
        value=("gpt-4o-mini" if provider == "openai" else "llama3.1:8b"),
        help=(
            "OpenAI examples: gpt-4o-mini, gpt-4o, o3-mini.\n"
            "Ollama examples: llama3.1:8b, qwen2.5:7b, mistral:7b"
        ),
    )
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.05)
    max_tokens = st.number_input("Max tokens", min_value=256, max_value=4000, value=1200, step=50)

    st.divider()
    st.subheader("API Keys & Hosts")
    if provider == "openai":
        st.text("Uses OPENAI_API_KEY from environment if set.")
    else:
        ollama_host = st.text_input("OLLAMA_HOST", value=os.getenv("OLLAMA_HOST", "http://localhost:11434"))

    st.divider()
    st.subheader("Output format")
    pretty = st.checkbox("Pretty JSON", value=True)

st.subheader("1) Paste Job Description")
jd_text = st.text_area("Job Description", value="", height=220, placeholder="Paste the JD here…")

st.subheader("2) Provide Resume")
resume_input_mode = st.radio("Resume input", ["Paste text", "Upload PDF"], horizontal=True)
resume_text: Optional[str] = None

if resume_input_mode == "Paste text":
    resume_text = st.text_area("Resume (plain text)", value="", height=360, placeholder="Paste your resume text…")
else:
    uploaded = st.file_uploader("Upload resume PDF", type=["pdf"])
    if uploaded is not None:
        with st.spinner("Extracting text from PDF…"):
            try:
                resume_text = extract_text_from_pdf(uploaded.read())
                st.success("Text extracted from PDF.")
            except Exception as e:
                st.error(f"PDF extraction failed: {e}")

col1, col2 = st.columns([1,1])
with col1:
    run = st.button("Evaluate ✅", use_container_width=True, type="primary")
with col2:
    show_prompt = st.toggle("Show full prompt")

if run:
    if not jd_text or not resume_text:
        st.warning("Please provide both the job description and the resume text/PDF.")
        st.stop()

    client = LLMClient(provider=provider, model=model, temperature=temperature, max_tokens=max_tokens)
    with st.spinner("Scoring resume against the JD…"):
        response_text, raw_prompt = score_resume_against_jd(
            client=client,
            job_description=jd_text,
            resume_text=resume_text,
            rubric=RUBRIC,
            system_instructions=SYSTEM_INSTRUCTIONS,
        )

    data = safe_json_loads(response_text)
    if data is None:
        st.error("Model returned invalid JSON. Try lowering temperature or another model.")
    else:
        st.success("Evaluation complete.")
        overall = data.get("overall", {})
        st.metric("Overall Match (0-100)", value=overall.get("score", "-"))
        st.write("")
        st.subheader("Detailed Scores")
        st.json(data if not pretty else json.loads(json.dumps(data, indent=2)))

    if show_prompt and raw_prompt:
        st.divider()
        st.subheader("Prompt sent to the model")
        st.code(raw_prompt, language="markdown")

st.divider()
st.markdown("""
**How it works**
1. Your JD + resume are formatted into a transparent rubric-based prompt.
2. The model must return strict JSON with dimension-wise scores and feedback.
3. We parse & display the JSON. If the JSON fails, tweak temperature or model.
""") 
