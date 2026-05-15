# Cohort 1 — Frequently Asked Questions

> Questions from participants across LinkedIn, Slack, and live sessions.
> Last updated: May 2026

---

## General / Setup

### Q: Do we get API credits as part of the course? The Anthropic console is showing $20 and $50 plans.

**Asked by:** Uzma Syed

The API key is not required to complete any exercise — every script in the course supports `--mock` mode, which simulates a real API response locally without making any API call or incurring any cost. You can work through the full course this way.

That said, the total API usage across all 8 modules is approximately **$0.50 for the entire course**. That's the real-world cost of running the exercises against the live Claude API. We'd encourage you to invest that — getting responses from the actual model rather than a simulation is where the real learning happens. You'll see how confidence levels shift with different prompts, how the model handles edge cases in your logs, and how structured JSON output behaves under real conditions. Mock mode is there so nobody is blocked, but live mode is where the course comes to life.

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
git clone https://github.com/platformengineering/agentic-ai-pe-course.git
cd agentic-ai-pe-course
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

*More questions will be added here as they come in. If you have a question, post it in the Slack course channel.*
