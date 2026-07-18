"""
ai_engine.py
LLM-powered insights and Q&A chatbot, grounded strictly in the uploaded dataset's
statistical summary. Supports Anthropic (Claude), OpenAI, and Google Gemini.
Falls back to a rule-based, purely statistical insight generator if no API key
is configured, so the app is always fully functional out of the box.
"""

import pandas as pd
import numpy as np

SYSTEM_INSTRUCTIONS = (
    "You are a senior data analyst. You will be given a statistical summary of a "
    "user's dataset (aggregates, not raw rows). Answer ONLY using the information "
    "in that summary. Do not invent numbers, trends, or facts that are not "
    "supported by the summary. If something cannot be determined from the summary, "
    "say so clearly instead of guessing. Be concise, specific, and business-focused. "
    "Use bullet points where helpful."
)


def get_available_provider(secrets: dict):
    """Return ('anthropic'|'openai'|'gemini'|None, api_key|None) based on configured secrets."""
    if secrets.get("ANTHROPIC_API_KEY"):
        return "anthropic", secrets["ANTHROPIC_API_KEY"]
    if secrets.get("OPENAI_API_KEY"):
        return "openai", secrets["OPENAI_API_KEY"]
    if secrets.get("GEMINI_API_KEY"):
        return "gemini", secrets["GEMINI_API_KEY"]
    return None, None


def _call_anthropic(api_key: str, context: str, question: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=SYSTEM_INSTRUCTIONS,
        messages=[{"role": "user", "content": f"Dataset summary:\n{context}\n\nQuestion: {question}"}],
    )
    return "".join(block.text for block in resp.content if hasattr(block, "text"))


def _call_openai(api_key: str, context: str, question: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=800,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": f"Dataset summary:\n{context}\n\nQuestion: {question}"},
        ],
    )
    return resp.choices[0].message.content


def _call_gemini(api_key: str, context: str, question: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_INSTRUCTIONS)
    resp = model.generate_content(f"Dataset summary:\n{context}\n\nQuestion: {question}")
    return resp.text


def ask_ai(secrets: dict, context: str, question: str) -> str:
    """
    Route a question + dataset context to whichever LLM provider is configured.
    Raises a clear exception on failure so the UI can show a friendly error.
    """
    provider, api_key = get_available_provider(secrets)
    if provider is None:
        return generate_offline_answer(context, question)

    try:
        if provider == "anthropic":
            return _call_anthropic(api_key, context, question)
        elif provider == "openai":
            return _call_openai(api_key, context, question)
        elif provider == "gemini":
            return _call_gemini(api_key, context, question)
    except Exception as e:
        return (
            f"⚠️ AI provider request failed ({provider}): {e}\n\n"
            "Falling back to offline statistical summary:\n\n"
            + generate_offline_answer(context, question)
        )


def generate_offline_answer(context: str, question: str) -> str:
    """A safe, no-API-key fallback that just surfaces the statistical context relevantly."""
    return (
        "🔌 No AI API key is configured, so here is a direct statistical summary "
        "instead of a generated narrative. Add ANTHROPIC_API_KEY, OPENAI_API_KEY, "
        "or GEMINI_API_KEY to `.streamlit/secrets.toml` to enable full AI answers.\n\n"
        f"Your question: \"{question}\"\n\n"
        f"Relevant dataset summary:\n{context}"
    )


def generate_ai_insights(secrets: dict, context: str) -> str:
    """Generate a structured business-insights narrative from the dataset summary."""
    prompt = (
        "Based strictly on the dataset summary, generate:\n"
        "1) 3-5 key patterns or trends\n"
        "2) Any notable anomalies or data quality concerns\n"
        "3) 3 concrete, actionable business recommendations\n"
        "Only state what is directly supported by the summary statistics provided."
    )
    return ask_ai(secrets, context, prompt)


def generate_rule_based_insights(df: pd.DataFrame, profile: dict, corr_pairs: list) -> list:
    """
    Always-available, deterministic insights derived purely from computed statistics
    (used both as offline fallback and as a fast pre-AI summary shown in the UI).
    """
    insights = []

    if profile["duplicate_rows"] > 0:
        pct = round(profile["duplicate_rows"] / profile["n_rows"] * 100, 1)
        insights.append(f"🔁 Found {profile['duplicate_rows']} duplicate rows ({pct}% of data) — consider removing them.")

    total_missing = sum(profile["missing_values"].values())
    if total_missing > 0:
        worst_col = max(profile["missing_values"], key=profile["missing_values"].get)
        insights.append(
            f"⚠️ {total_missing} missing values detected. '{worst_col}' has the most "
            f"({profile['missing_values'][worst_col]} missing)."
        )

    for a, b, v in corr_pairs[:3]:
        direction = "positive" if v > 0 else "negative"
        strength = "strong" if abs(v) > 0.7 else "moderate"
        insights.append(f"📈 {strength.capitalize()} {direction} correlation ({v}) between '{a}' and '{b}'.")

    numeric_cols = profile["numeric_columns"]
    for col in numeric_cols[:3]:
        skew = df[col].skew()
        if abs(skew) > 1:
            direction = "right" if skew > 0 else "left"
            insights.append(f"📊 '{col}' is heavily skewed to the {direction} (skewness={round(skew,2)}).")

    if not insights:
        insights.append("✅ No major data quality issues detected. Dataset looks clean and well-distributed.")

    return insights
