"""
AI Service — HuggingFace Inference API integration.

Uses huggingface_hub InferenceClient with chat completions format.
Model: meta-llama/Llama-3.1-8B-Instruct (confirmed active on free tier)

Design rules (see claude.md):
  - AI output is NEVER written to DB here — callers decide what to save
  - Every function returns a schema object with degraded=True on any failure
  - No function raises exceptions — failures are soft and observable
"""

import json
import logging
from flask import current_app
from groq import Groq

from ..schemas.ai import HypothesisSuggestion, VerdictSuggestion, SummarySuggestion

logger = logging.getLogger(__name__)


def _get_client() -> Groq:
    token = current_app.config["GROQ_API_KEY"]
    return Groq(api_key=token)

def _call(prompt: str) -> str:
    from groq import Groq
    client = Groq(api_key=current_app.config.get("GROQ_API_KEY", ""))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.3,
    )
    return response.choices[0].message.content


def _extract_json(raw: str) -> dict:
    """
    Extract first valid JSON object from raw string.
    Handles preamble text before the JSON.
    """
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON found in response: {raw!r}")
    return json.loads(raw[start:end + 1])


def _safe_reason(exc: Exception) -> str:
    msg = str(exc)
    if "429" in msg:
        return "AI rate limit reached. Please try again in a moment."
    if "401" in msg or "403" in msg:
        return "AI authentication failed. Check your GROQ_API_KEY."
    if "timeout" in msg.lower():
        return "AI request timed out. Please try again."
    return "AI suggestion unavailable. You can write this manually."


# ── Public Functions ───────────────────────────────────────────────────────────

def suggest_hypothesis(rough_idea: str) -> HypothesisSuggestion:
    prompt = f"""You are a growth experiment assistant.
Rewrite this rough idea as a formal experiment hypothesis.
Use this exact format: "We believe that [change] will [metric impact] because [reason]."

Rough idea: {rough_idea}

Respond with valid JSON only, no explanation, no markdown.
Format: {{"hypothesis": "...", "confidence": "low|medium|high"}}"""

    try:
        raw = _call_hf(prompt)
        parsed = _extract_json(raw)
        return HypothesisSuggestion(
            hypothesis=parsed.get("hypothesis"),
            confidence=parsed.get("confidence", "medium"),
        )
    except Exception as exc:
        logger.warning("suggest_hypothesis failed: %s", exc)
        return HypothesisSuggestion(degraded=True, reason=_safe_reason(exc))


def suggest_verdict(
    metric_name: str,
    control_value: float,
    variant_value: float,
    sample_size_control: int,
    sample_size_variant: int,
    duration_days: int,
) -> VerdictSuggestion:
    relative_lift = (
        ((variant_value - control_value) / control_value * 100)
        if control_value != 0 else 0
    )

    prompt = f"""You are a growth experiment analyst.
Given these experiment results, suggest a verdict.

Metric: {metric_name}
Control: {control_value} (n={sample_size_control})
Variant: {variant_value} (n={sample_size_variant})
Duration: {duration_days} days
Relative lift: {relative_lift:.1f}%

Respond with valid JSON only, no explanation, no markdown.
Format: {{"verdict": "ship|rollback|iterate", "interpretation": "...", "suggested_reason": "..."}}"""

    try:
        raw = _call_hf(prompt)
        parsed = _extract_json(raw)
        verdict = parsed.get("verdict", "").lower()
        if verdict not in ("ship", "rollback", "iterate"):
            verdict = None
        return VerdictSuggestion(
            verdict=verdict,
            interpretation=parsed.get("interpretation"),
            suggested_reason=parsed.get("suggested_reason"),
        )
    except Exception as exc:
        logger.warning("suggest_verdict failed: %s", exc)
        return VerdictSuggestion(degraded=True, reason=_safe_reason(exc))


def summarize_experiment(experiment_dict: dict) -> SummarySuggestion:
    result = (experiment_dict.get("results") or [{}])[0]

    prompt = f"""You are a product growth analyst.
Write a 2-3 sentence stakeholder summary of this completed experiment.
Be specific about the numbers and the decision made.

Title: {experiment_dict.get("title")}
Hypothesis: {experiment_dict.get("hypothesis")}
Metric: {experiment_dict.get("metric_name")}
Control: {result.get("control_value")} | Variant: {result.get("variant_value")}
Verdict: {experiment_dict.get("verdict")}

Respond with valid JSON only, no explanation, no markdown.
Format: {{"summary": "..."}}"""

    try:
        raw = _call_hf(prompt)
        parsed = _extract_json(raw)
        return SummarySuggestion(summary=parsed.get("summary"))
    except Exception as exc:
        logger.warning("summarize_experiment failed: %s", exc)
        return SummarySuggestion(degraded=True, reason=_safe_reason(exc))
