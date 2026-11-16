"""
narrative.py - turn the structured prescription into a short engineer-ready summary.

Default: a deterministic template (no API key needed, fully reproducible).
Optional: if ANTHROPIC_API_KEY or OPENAI_API_KEY is set (and PRA_USE_LLM=1), an LLM
rewrites the summary. The LLM only sees the agent's structured findings and is told
not to add facts - the engineering decisions stay in the deterministic core.
"""
from __future__ import annotations

import json
import os


def template_summary(p) -> str:
    d = p.diagnosis
    tag = p.asset["tag"]
    lines = [
        f"{tag} {p.asset['name']}: suspected **{d['name']}** "
        f"(match {d['match_score']:.0%}, likelihood {d['likelihood']:.0%} among {len(p.hypotheses)} failure modes).",
    ]
    sup = [e for e in d["evidence"] if e["verdict"] == "supports"]
    if sup:
        lines.append("Evidence: " + "; ".join(f"{e['label']} {e['expected']} ({e['z']:+.0f} sigma)" for e in sup) + ".")
    if p.ambiguous:
        alt = p.hypotheses[1]
        lines.append(f"Diagnosis not yet conclusive - {alt['name']} is close behind. Run the discriminating checks first.")
    if p.days_to_trip is not None:
        lines.append(f"At the current trend the machine reaches a trip limit in about {p.days_to_trip:.0f} days.")
    else:
        lines.append("No trip limit is predicted within 90 days at the current trend.")
    if p.history.get("bad_actor"):
        lines.append(f"This is a repeat failure on {tag} ({p.history['count']} events in 36 months) - a formal RCA is recommended.")
    lines.append(f"Priority **P{p.priority['level']} {p.priority['label']}** ({p.priority['window']}). "
                 f"Planned intervention avoids roughly USD {p.economics['value_of_acting_now_usd']:,.0f} versus run-to-failure (illustrative).")
    lines.append(f"First action: {p.actions['confirm'][0] if p.ambiguous else p.actions['immediate'][0]}.")
    return " ".join(lines)


def _llm_summary(p) -> str | None:
    if os.getenv("PRA_USE_LLM") != "1":
        return None
    facts = {k: getattr(p, k) for k in ("asset", "diagnosis", "ambiguous", "discriminating_checks",
                                         "history", "forecast", "days_to_trip", "priority",
                                         "economics", "actions")}
    prompt = ("You are a senior rotating-equipment reliability engineer. Write a 120-word summary "
              "for the plant maintenance meeting from these findings. Use ONLY these facts; do not "
              "invent numbers. Lead with the diagnosis and the decision needed.\n\n"
              + json.dumps(facts, default=str)[:12000])
    try:
        if os.getenv("ANTHROPIC_API_KEY"):
            import anthropic
            msg = anthropic.Anthropic().messages.create(
                model=os.getenv("PRA_LLM_MODEL", "claude-sonnet-4-5"), max_tokens=400,
                messages=[{"role": "user", "content": prompt}])
            return msg.content[0].text
        if os.getenv("OPENAI_API_KEY"):
            from openai import OpenAI
            r = OpenAI().chat.completions.create(
                model=os.getenv("PRA_LLM_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}])
            return r.choices[0].message.content
    except Exception as exc:                     # never let the narrative break the agent
        return f"(LLM summary unavailable: {exc})\n\n" + template_summary(p)
    return None


def summarise(p) -> str:
    return _llm_summary(p) or template_summary(p)
