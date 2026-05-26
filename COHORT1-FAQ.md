# Cohort 1 — Frequently Asked Questions

> Questions from participants across LinkedIn, Slack, and live sessions.
> Last updated: May 2026

---

## General / Setup

### Q: Do we get API credits as part of the course? The Anthropic console is showing $20 and $50 plans.

**Asked by:** Uzma Syed

The API key is not required to complete any exercise — every script in the course supports `--mock` mode, which simulates a real API response locally without making any API call or incurring any cost. You can work through the full course this way.

That said, the total API usage across all 8 modules is small — a few dollars at most, depending on how many times you run each exercise. We'd encourage you to invest that — getting responses from the actual model rather than a simulation is where the real learning happens. You'll see how confidence levels shift with different prompts, how the model handles edge cases in your logs, and how structured JSON output behaves under real conditions. Mock mode is there so nobody is blocked, but live mode is where the course comes to life.

To get an API key:
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up and add a small credit (the minimum top-up covers the entire course several times over)
3. Generate a key and set it in your environment: `export ANTHROPIC_API_KEY=your_key_here`

No credits are provided as part of the course enrollment.

---

## Module 1

### Q: Where do I find and run the exercise files (verify_setup.py, hello_claude.py, etc.)?

**Asked by:** Anju Bala

All exercise files live in the course GitHub repository. Here is how to get to them:

**Step 1 — Clone the course repo**

If you haven't already, clone (or fork and clone) the course repository to your local machine:

```bash
git clone https://github.com/InternalDeveloperPlatform/pe-agentic-course.git
cd pe-agentic-course
```

**Step 2 — Navigate to the Module 1 folder**

Each module has its own folder. All the files you listed are inside `module1/`:

```
module1/
├── verify_setup.py       ← Run this first — pre-flight environment check
├── hello_claude.py       ← Primary exercise script — write your system prompt here
├── agent.py              ← Alternative entry point that saves output to file
├── sample_log.txt        ← Sample CI failure log (agent input)
├── agent-config.yml      ← Model and output schema configuration
└── solutions/
    └── solution.py       ← Reference implementation — read after your own attempt
```

**Step 3 — Run the pre-flight check first**

From the root of the repo, run:

```bash
python module1/verify_setup.py
```

This checks that your Python version, dependencies, and API key are all configured correctly. Fix any issues it flags before moving on to `hello_claude.py`.

**Step 4 — Set your API key (if using the Claude API)**

```bash
export ANTHROPIC_API_KEY=your_key_here
```

`hello_claude.py` supports two flags for running without making a live API call:

- `--manual` — prints the formatted prompt so you can paste it into Claude.ai for free. No API key needed.
- `--mock` — simulates a real API response locally. Useful for testing your code without consuming tokens.

```bash
python module1/hello_claude.py --manual   # paste prompt into Claude.ai manually
python module1/hello_claude.py --mock     # local mock response, no API call
```

---

> **A note on getting support:** LinkedIn works, but the fastest way to get help between sessions is the **Platform Engineering Slack workspace** — there's a dedicated course channel. Email support@platformengineering.org with your name and email address to be added. Questions posted there benefit the whole cohort, and often get answered by peers before the instructor gets to them.

---

### Q: The instructions say to clone the repo, but I need to fork it to add secrets for GitHub Actions. Which is correct?

**Asked by:** Steven

Fork first, then clone your fork. The distinction matters because GitHub Actions secrets (where you store your `ANTHROPIC_API_KEY`) can only be added to repositories you own. If you clone the original repo directly, you won't have a Settings tab and won't be able to add secrets.

Correct flow:
1. Go to [github.com/InternalDeveloperPlatform/pe-agentic-course](https://github.com/InternalDeveloperPlatform/pe-agentic-course) and click **Fork**
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/pe-agentic-course.git`
3. Add your API key: Settings → Secrets and variables → Actions → New repository secret → `ANTHROPIC_API_KEY`

The README has been updated to reflect this.

---

### Q: The exercise says to write the SYSTEM_PROMPT but it's already filled in inside hello_claude.py and agent.py. What am I supposed to do?

**Asked by:** Steven

Good catch — this was a bug in the exercise files. `hello_claude.py` has been updated: `SYSTEM_PROMPT` is now an empty string with TODO comments describing what the prompt must do. Your task is to write the prompt from scratch.

`agent.py` is intentionally pre-filled — it's the runner that GitHub Actions calls and is not the exercise file. The exercise file is `hello_claude.py` only.

If you already completed Module 1 with the filled-in prompt, you've still learned the key lesson (how the API call works and how structured output is produced). To get the full exercise value, clear the `SYSTEM_PROMPT` in your fork and write your own before checking `solutions/solution.py`.

---

### Q: The GitHub Actions workflow fails immediately — something about pip and a missing requirements.txt

**Asked by:** Steven

Correct — `requirements.txt` was missing from the root of the repo. It has been added. Pull the latest from the upstream repo (or add a `requirements.txt` containing just `anthropic` to the root of your fork) and the workflow will complete cleanly.

---

## Module 5

### Q: What are the threshold definitions and allowable values in quality-gates.json? What do the SAST findings thresholds mean?

**Asked by:** Kevin

Each gate in `quality-gates.json` has three fields that control its behaviour: a `metric` (what gets measured), a `threshold` (the value it's compared against), and an `operator` (the direction of comparison). A gate **passes** when `metric <operator> threshold` is true.

Here is a full breakdown of every gate:

---

**`test_coverage` — Unit Test Coverage**
- Metric: `coverage_pct` — percentage of lines covered by unit tests
- Default threshold: `95` with operator `>=`
- Passes when coverage is **at or above** the threshold
- Allowable values: any integer 0–100. The sample data ships with `coverage_pct: 81.4`, so this gate **fails** by default — try lowering the threshold to `80` to see it pass
- `rollback_trigger: false` — failing this gate blocks the deploy but does not trigger a post-deploy rollback recommendation

**`coverage_branch` — Branch Coverage**
- Metric: `coverage_branch_pct` — percentage of code branches (if/else paths) exercised by tests
- Default threshold: `80` with operator `>=`
- Allowable values: any integer 0–100. Branch coverage is stricter than line coverage and intentionally set lower

**`sast_findings` — SAST High-Severity Findings**
- Metric: `security_scan.high` — the **count** of HIGH-severity findings from the security scanner
- Default threshold: `0` with operator `<=`
- Meaning: zero HIGH findings are allowed. Even a single finding fails the gate
- The sample data has `"high": 1`, so this gate **fails out of the box** — that is intentional for the exercise
- Allowable values: any non-negative integer. Set to `1` to permit one finding through, `2` to permit two, and so on. In real production, keep this at `0`
- `rollback_trigger: true` — one of only two rollback-trigger gates. If this fires after deploy, `monitor.py` will escalate for human approval

**`lighthouse_score` — Lighthouse Performance Score**
- Metric: `lighthouse_score` — Google Lighthouse score for the checkout frontend (0–100 scale)
- Default threshold: `85` with operator `>=`
- Allowable values: any integer 0–100. Scores in real projects typically range 40–100; 85 is a fairly strict bar for a production checkout page

**`latency_p95_delta` — P95 Latency Regression**
- Metric: `latency_p95_delta_pct` — the **percentage increase** in P95 latency compared to the previous deployment. This is a delta, not an absolute millisecond value
- Default threshold: `10` with operator `<=`
- Meaning: P95 latency may increase by at most 10%. Set to `0` to require P95 to be the same or better; set to `20` to allow a larger regression through
- The mock rollback response in `monitor.py` deliberately uses `18.4%` to trigger this gate
- `rollback_trigger: true` — this and `sast_findings` are the only two gates that feed the post-deploy rollback monitor

**`cost_per_request_delta` — Cost Per Request Regression**
- Metric: `cost_per_request_delta_pct` — percentage increase in compute cost per request vs the previous deploy
- Default threshold: `10` with operator `<=`
- Allowable values: any non-negative number. Same delta-percentage pattern as latency

---

**The `operator` field** only takes two values across all gates:
- `>=` — passes if the measured value is **at or above** the threshold (used for coverage and Lighthouse)
- `<=` — passes if the measured value is **at or below** the threshold (used for findings count, latency delta, cost delta)

**Which script reads quality-gates.json?**

Only **`monitor.py`** (the post-deploy rollback watchdog) reads `quality-gates.json` at runtime, and it only loads the two gates where `rollback_trigger` is `true` (`sast_findings` and `latency_p95_delta`). Changing thresholds in `quality-gates.json` will affect `monitor.py` output only.

`triage_agent.py` does **not** read `quality-gates.json` — it loads `sample_data.json` directly and the gate thresholds are embedded in its `SYSTEM_PROMPT`. Editing `quality-gates.json` has no effect when running `triage_agent.py`.

**A note on mock vs live values**

The `MOCK_RESPONSE` in `triage_agent.py` shows `coverage: 74.1%` — this is a hand-crafted illustrative scenario, not a reflection of `sample_data.json` (which has `coverage_pct: 81.4`). In live mode the agent evaluates the actual sample data, which is a different scenario from the mock.

**A good experiment sequence (using monitor.py):**

1. Run `python module5/monitor.py --mock` — see the pre-built rollback scenario (18.4% P95 latency, exceeds the 10% threshold)
2. Set `latency_p95_delta.threshold` to `20` — the latency gate now passes; observe the rollback recommendation disappear
3. Set `latency_p95_delta.threshold` to `5` — tighten the bar; the gate fires sooner
4. Set `cost_per_request_delta.rollback_trigger` to `true` — this gate now feeds the monitor alongside the two that already fire
5. Set `sast_findings.threshold` to `1` — the security gate now permits one HIGH finding through

---

*More questions will be added here as they come in. If you have a question, post it in the Slack course channel.*
