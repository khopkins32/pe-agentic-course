"""
module2/agent.py
Entry point for Module 2 exercise: Five-step agentic loop — diagnose a deployment failure

MOCK MODE
---------
Run without an API key to see the expected output format:
    python module2/agent.py --mock
    MOCK_MODE=1 python module2/agent.py
"""

import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.claude_client import ask
from shared.output import save_json, to_step_summary, to_github_issue

# ── Mock mode flag ─────────────────────────────────────────────────────────────
MOCK_MODE = "--mock" in sys.argv or os.environ.get("MOCK_MODE") == "1"

MOCK_RESPONSE = {
    "diagnosis": "The deployment failed due to a missing environment variable PAYMENT_API_KEY in the production environment. The application starts successfully but crashes at the first payment request.",
    "confidence": "HIGH",
    "recommended_action": "Add PAYMENT_API_KEY to GitHub Actions secrets and reference it in the workflow env block. Re-trigger the deployment after confirming the secret is present.",
    "escalate": False,
}

# ── Prompt & config ────────────────────────────────────────────────────────────
# TODO: Write the system prompt for the triage agent.
#
# Your prompt should tell Claude:
# 1. Its role (e.g. "You are a CI/CD diagnostic agent")
# 2. To return ONLY valid JSON (no prose, no markdown)
# 3. The required JSON keys:
#      - diagnosis (string): root cause of the failure
#      - confidence (HIGH|MEDIUM|LOW): HIGH only when the root cause is confirmed in logs
#      - recommended_action (string): concrete next step
#      - escalate (boolean): true if a human must review before taking action
#
# Hint: look at MOCK_RESPONSE above for the expected output shape.
SYSTEM_PROMPT = (
    "You are a CI/CD diagnostic agent. Analyse the build log and return ONLY valid JSON "
    "with keys: diagnosis (string), confidence (HIGH|MEDIUM|LOW), "
    "recommended_action (string), escalate (boolean). "
    "confidence is HIGH only when the root cause is directly visible in the log. "
    "Use MEDIUM when inferring state, LOW when the log is ambiguous."
)  # replace this empty string with your prompt

AGENT_CONFIG = {
    "model": "claude-opus-4-5-20251101",
    "max_tokens": 1024,
    "max_iterations": 3,
    "context_fields": [
        "log_snippet",
        "build_number",
        "repo"
    ]
}

# ── Five-step agentic loop functions ────────────────────────────────────────────────────────

def write_prompt(log: str) -> tuple:
    """
    Step 1 — Write prompt.

    Separating prompt construction from the API call means you can unit-test
    the prompt independently (e.g. verify the user message contains key fields)
    without making any API call.

    system_prompt + user_msg as tuple

    Returns a (system_prompt, user_message) tuple.
    """
    user_msg = (
        f"Context:\n{log}\n"
    )
    return SYSTEM_PROMPT, user_msg


def call_api(system: str, user: str) -> dict:
    """
    Step 2 — Call the Claude API (or return mock).

    Isolating the API call lets you mock this step in tests without touching
    any of the prompt or action logic.
    """
    if MOCK_MODE:
        print("[MOCK MODE] Skipping Claude API — returning pre-defined response.\n")
        return MOCK_RESPONSE
    return ask(system=system, user=user, model=AGENT_CONFIG["model"], max_tokens=AGENT_CONFIG["max_tokens"])


def parse_json(result: dict) -> dict:
    """
    Step 3 — Parse and validate the JSON response.

    Raises ValueError if any required key is missing. This is the contract
    enforcement step — if Claude returns an unexpected schema, fail here
    rather than silently passing bad data to the action step.
    """
    required = {"diagnosis", "confidence", "recommended_action", "escalate"}
    missing = required - set(result.keys())
    if missing:
        raise ValueError(
            f"Agent response missing required keys: {missing}\n"
            f"Got: {list(result.keys())}"
        )
    valid_confidence = {"HIGH", "MEDIUM", "LOW"}
    if result["confidence"] not in valid_confidence:
        raise ValueError(
            f"Invalid confidence value '{result['confidence']}'. "
            f"Expected one of {valid_confidence}."
        )
    return result


def execute_action(result: dict) -> None:
    """
    Step 4 — Execute the action.

    In a real system this step would call the GitHub API, send a Slack message,
    trigger a rollback, or open a PagerDuty incident. Here we print the action
    and escalation notice so you can see what an agent would do.
    """
    print(f"\n[ACTION] Confidence     : {result['confidence']}")
    print(f"[ACTION] Recommendation : {result['recommended_action']}")

    if result.get("escalate"):
        print("[ACTION] 🔴 ESCALATION REQUIRED")
        print(to_github_issue(result, module=2))
    else:
        print("[ACTION] ✅ No escalation — agent handled autonomously")


def verify_result(result: dict) -> bool:
    """
    Step 5 — Verify the result meets success criteria.

    Returns True if the output is well-formed and actionable.
    In a production agent this might gate whether to proceed with an auto-fix
    or to fall back to human review.
    """
    has_valid_confidence = result.get("confidence") in ("HIGH", "MEDIUM", "LOW")
    has_recommendation = bool(result.get("recommended_action"))
    return has_valid_confidence and has_recommendation

def load_sample() -> str:
    sample = Path(__file__).parent / "sample_log.txt"
    return sample.read_text()


def run_agent() -> dict:
    context = load_sample()
   
    # TODO: Call ask() with SYSTEM_PROMPT and the log content.
    #
    # ask() signature:
    #   ask(system=..., user=..., model=..., max_tokens=...)
    #
    # - system: use SYSTEM_PROMPT (defined above)
    # - user:   pass the log as  f"Context:\n{context}"
    # - model and max_tokens: use AGENT_CONFIG["model"] and AGENT_CONFIG["max_tokens"]
    #
    # Assign the return value to `result`.
    
    # Step 1 of Agentic Loop
    system, user = write_prompt(context)
    # Step 2  of Agentic Loop
    raw_result = call_api(system, user)
    # Step 3  of Agentic Loop
    result = parse_json(raw_result)
    # Step 4  of Agentic Loop
    execute_action(result)
    # Step 5  of Agentic Loop
    success = verify_result(result)

    print(json.dumps(result, indent=2))
    save_json(result, module=2)
    print(to_step_summary(result, title="Module 2 Agent Result"))
    print(f"\n[VERIFY] All checks passed: {success}")
    return result


if __name__ == "__main__":
    run_agent()
