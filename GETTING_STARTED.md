# Getting started with Model Check Monitor

This guide is for Codex users who want to use the skill without needing to understand its internal implementation.

## What are tokens?

Tokens are small pieces of text that Codex processes. A longer request, many files, long responses, and a large conversation history can use more tokens. More tokens do not automatically mean a better answer, but they can increase usage and context pressure.

Token counts are not the same as credits or money. The exact credit impact depends on the provider's pricing and service rules. Model Check Monitor does not invent prices.

## What is a model?

A model is the AI that performs your task. The model catalog can contain several models with different descriptions. For example, the catalog used while writing this document included:

- **GPT-5.6-Luna** — described in the catalog as fast and affordable;
- **GPT-5.6-Terra** — described as a model for everyday work;
- **GPT-5.6-Sol** — described as an advanced agentic coding model.

Model names and catalog contents can change. The skill reads the current catalog instead of assuming that GPT-5.6 is the only or newest family.

## How the recommendation works

The skill does not use invented product categories. It looks directly at the available model catalog, each model's description, supported reasoning levels, and the task's complexity. It then recommends a concrete model, reasoning level, and service tier.

## Why the choice matters

A model with too little reasoning for the task can misunderstand a coupled task, miss a dependency, or require several correction attempts. The total usage can then be higher than if a suitable stronger model had been chosen at the start.

A model that is too strong can spend extra reasoning on a task that did not need it. That can increase latency and usage without improving the result.

The goal is not “always use the cheapest model” or “always use the strongest model”. The goal is the cheapest model that is likely to complete the task reliably.

## Illustrative token-spending examples

The numbers below are **illustrative examples**, not measured prices or promises. They show how total usage can change when a model needs retries or extra reasoning.

| Task | Model choice | Illustrative result | Illustrative total |
|---|---|---|---:|
| Rename one variable | GPT-5.4-Mini · low | one short pass | 3,000 tokens |
| Rename one variable | GPT-5.6-Sol · high | correct, but unnecessary depth | 12,000 tokens |
| Update several related files | GPT-5.4 · medium | one normal implementation pass | 18,000 tokens |
| Debug three coupled services | GPT-5.4-Mini · low | misses a dependency, then needs retries | 42,000 tokens |
| Debug three coupled services | GPT-5.5 · high | one deeper investigation | 35,000 tokens |

These figures demonstrate a pattern only. They must not be read as provider pricing, guaranteed model behavior, or an exact credit conversion.

## Simple installation

The simple setup is for ordinary users. It copies the skill into Codex; it does not install Python packages and does not require a virtual environment.

### macOS

Open Terminal and paste:

```sh
mkdir -p "$HOME/.codex/skills/model-check"
cp -R skill/. "$HOME/.codex/skills/model-check/"
```

If you downloaded the repository elsewhere, run the commands from the repository directory first:

```sh
cd /path/to/model-check-monitor
mkdir -p "$HOME/.codex/skills/model-check"
cp -R skill/. "$HOME/.codex/skills/model-check/"
```

Start a new Codex task and use `\$model-check` or `\$model-check-monitor`.

### Linux

Open a terminal and paste:

```sh
mkdir -p "$HOME/.codex/skills/model-check"
cp -R skill/. "$HOME/.codex/skills/model-check/"
```

If you downloaded the repository elsewhere, run the commands from the repository directory first:

```sh
cd /path/to/model-check-monitor
mkdir -p "$HOME/.codex/skills/model-check"
cp -R skill/. "$HOME/.codex/skills/model-check/"
```

Start a new Codex task and use `\$model-check` or `\$model-check-monitor`.

## Worked examples with exact output

The following outputs are examples of what the user sees. The model names are examples from one catalog snapshot, including models below GPT-5.6. The current catalog and active settings depend on the local Codex installation.

The seven lines answer seven practical questions:

- **Recommended:** which actual model, reasoning level, and service tier to use;
- **Current:** what is active now;
- **Action:** what to do next;
- **Why:** why that choice fits this task;
- **Impact:** the likely usage direction, without invented prices;
- **Confidence:** how clear the task-to-model match is;
- **Recheck:** when a new assessment becomes useful.

### Example 1: simple task — suitable model choice

Task:

```text
$model-check Should I rename this variable in one file?
```

The check is run with **GPT-5.4-Mini · low · normal service**. The task is small and local, so this concrete configuration is appropriate.

```text
Recommended: GPT-5.4-Mini · low · normal service
Current: GPT-5.4-Mini · low · normal service
Action: keep current model and reasoning level
Why: one small local edit with no coupled dependencies
Impact: illustrative 3,000 tokens for one short pass; exact credits are unavailable
Confidence: high
Recheck: after the edit only if the task expands
```

### Example 2: simple task — reasoning was unnecessarily high

Task:

```text
$model-check Summarize this short meeting note in five bullets.
```

The task is run with **GPT-5.6-Sol · high**. The answer may be correct, but this model and reasoning level are unnecessary for this task.

```text
Recommended: GPT-5.4-Mini · low · normal service
Current: GPT-5.6-Sol · high · normal service
Action: switch to the recommended model
Why: a short summary does not require this model or reasoning level
Impact: illustrative 12,000 tokens now versus 3,000 tokens for the smaller configuration; exact credits are unavailable
Confidence: high
Recheck: after the next similar task
```

### Example 3: complex task — reasoning was too low

Task:

```text
$model-check Diagnose a failure involving authentication, Docker networking, and a database migration.
```

The task is run with **GPT-5.4-Mini · low**. Several systems are coupled, so this model and reasoning level are likely to cause missed dependencies or recovery attempts.

```text
Recommended: GPT-5.5 · high · normal service
Current: GPT-5.4-Mini · low · normal service
Action: switch to the recommended model
Why: diagnosis spans authentication, networking, and migration dependencies
Impact: illustrative 42,000 tokens after retries now versus 35,000 tokens for one deeper investigation; exact credits are unavailable
Confidence: high
Recheck: after the initial diagnosis
```

### Example 4: ordinary project work — suitable model choice

Task:

```text
$model-check Update three related scripts and add regression tests.
```

The task is run with **GPT-5.6-Terra · medium**. It spans multiple files and needs moderate reasoning, but not the most demanding configuration.

```text
Recommended: GPT-5.6-Terra · medium · normal service
Current: GPT-5.6-Terra · medium · normal service
Action: keep current model and reasoning level
Why: multiple-file implementation with routine validation
Impact: illustrative 18,000 tokens for one implementation and test pass; exact credits are unavailable
Confidence: medium
Recheck: after the first test run
```

### Example 5: weekly monitor

Task:

```text
$model-check-monitor weekly-run
```

The weekly monitor runs read-only with a low-cost model and low reasoning. A material finding might look like this:

```text
Coverage: local Codex metadata only; cloud metadata is not included
Usage: 18 sessions and 124,000 recorded tokens in the last 8 days
Distribution: most sessions used GPT-5.6-Sol with high reasoning
Pressure: 3 sessions had 30 or more turns
Finding: several routine tasks may have used a stronger model or reasoning level than needed
Action: use GPT-5.4-Mini or GPT-5.4 for summaries and small edits
Confidence: medium
Impact: illustrative 124,000 tokens were recorded across the window; exact credits are unavailable
```

## Weekly monitor

The weekly monitor is read-only. When you set it up, use Codex Scheduled Tasks. The advanced instructions are in [ADVANCED_SETUP.md](ADVANCED_SETUP.md).

## Scope limits

This v1 release is designed for Codex. Users of other AI platforms can read the documentation, but those platforms are not automatically monitored with equivalent data. Missing data is reported as unknown or limited coverage.

## Troubleshooting

If the skill is not found, check that the directory is named `model-check` and that `SKILL.md` is directly inside it. If local metadata is missing, the skill can still provide task advice, but the current model settings or usage may be unknown.
