"""
module2/triage_agent.py
Build Your First AI Agent — Module 2 exercise script.

Your task: fill in the SYSTEM_PROMPT and complete the run_agent() function
so the agent reads sample_log.txt, calls Claude, and returns a structured
JSON diagnosis.

Usage
-----
    python module2/triage_agent.py              # real API call
    python module2/triage_agent.py --mock       # mock mode (no API key needed)
    MOCK_MODE=1 python module2/triage_agent.py  # same as --mock via env var

What you need to fill in
------------------------
1. SYSTEM_PROMPT: define the agent's role and output schema (JSON keys).
2. run_agent(): load the sample log, call ask(), return the result dict.

Reference implementation: module2/solutions/solution.py
"""

import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.claude_client import ask
from shared.output import save_json, to_step_summary, to_github_issue

# ── Mock mode ──────────────────────────────────────────────────────────────────
MOCK_MODE = "--mock" in sys.argv or os.environ.get("MOCK_MODE") == "1"

MOCK_RESPONSE = {
    "summary":      "The Node.js test suite failed with 3 assertion errors in auth.test.js. Memory climbed to 87% during the run.",
    "likely_cause": "Test fixtures are not cleaned up between test cases, retaining heap references and causing assertion failures on retry.",
    "next_step":    "Add explicit cleanup in the afterEach hook and reduce the fixture dataset from 10,000 to 100 records.",
    "confidence":   "HIGH",
    "escalate":     False,
}

# TODO: Write your system prompt here.
# Your prompt must instruct Claude to:
#   1. Take the role of a CI/CD triage agent
#   2. Analyse the build log provided by the user
#   3. Return ONLY valid JSON — no explanation, no markdown, just the JSON object
#   4. Include exactly these keys:
#      - summary      (string)            one sentence describing what failed
#      - likely_cause (string)            one sentence on the root cause
#      - next_step    (string)            one concrete remediation action
#      - confidence   (HIGH|MEDIUM|LOW)   your confidence in the diagnosis
#      - escalate     (boolean)           true only if the issue needs human intervention
#
# Hint: be explicit about when escalate should be true vs false.
# Check solutions/solution.py only after you have made your own attempt.
SYSTEM_PROMPT = (
    "You are a CI/CD diagnostic agent. Analyse the build log and return ONLY valid JSON "
    "with keys: diagnosis (string), confidence (HIGH|MEDIUM|LOW), "
    "recommended_action (string), escalate (boolean). "
    "confidence is HIGH only when the root cause is directly visible in the log. "
    "Use MEDIUM when inferring state, LOW when the log is ambiguous."
)  # Replace this empty string with your prompt

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
        f"Build log:\n{log}\n\n"
        "Diagnose the failure. Identify root cause, confidence level, and recommended action."
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
    return ask(system=system, user=user, max_tokens=512)


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
    """Load the CI failure log from sample_log.txt."""
    sample = Path(__file__).parent / "sample_log.txt"
    return sample.read_text()


def run_agent() -> dict:
    """
    TODO: Complete this function.

    Steps:
    1. Load the sample log using load_sample().
    2. If MOCK_MODE is True, return MOCK_RESPONSE directly (already done for you).
    3. Otherwise, call ask() with SYSTEM_PROMPT and the log as the user message.
    4. Return the result dict.
    """
    log_content = load_sample()

    if MOCK_MODE:
        print("[MOCK MODE] Skipping Claude API — returning pre-defined response.")
        print("[MOCK MODE] Set ANTHROPIC_API_KEY and remove --mock to call the real API.\n")
        return MOCK_RESPONSE    
    else:
        # Step 1 of Agentic Loop
        system, user = write_prompt(log_content)
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


def main():
    return run_agent()


if __name__ == "__main__":
    main()
