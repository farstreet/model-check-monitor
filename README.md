# Model Check Monitor

Model Check Monitor helps you choose an appropriate Codex model before a task and understand whether your Codex usage remains efficient over time.

> **Status:** version 1.0.0 in preparation. Codex is the primary target.

## In plain language: choosing the right vehicle

Imagine that you need to bring a full shopping cart home while it is raining. Your goal is clear: bring **all** the groceries home, keep them **dry**, and spend as little as possible.

- With a **bicycle**, you spend very little, but you cannot carry the full cart and some groceries get wet. The vehicle is too light for the job.
- With a **bus**, the price may still be low and you may stay dry, but you still cannot take the full cart with you. The vehicle is still not suitable.
- With a **Ferrari**, you can carry everything quickly and stay dry, but you spend far more than necessary. The vehicle is more powerful than the job requires.
- With an **ordinary car**, you bring the full cart home dry at a much lower cost. It is the cheapest vehicle that completes the job reliably.

This is what Model Check Monitor does for Codex. It looks at the task, considers the available models and reasoning levels, and recommends the cheapest concrete configuration that is likely to complete the job properly. It recommends; it never changes your settings automatically.

## Choose your guide

- **[Getting started](GETTING_STARTED.md)** — for users who want to install the skill and understand its recommendations.
- **[Advanced setup](ADVANCED_SETUP.md)** — only for developers and maintainers who install, test, or manage the monitor. You do not need this guide just to use the weekly monitor.

## What does the skill do?

- `\$model-check` is the short alias for checking only the current task.
- `\$model-check-monitor` also includes the weekly read-only monitor and retrospective session comparison.
- The skill considers available models and chooses the cheapest suitable model and reasoning level.
- The impact line describes likely usage qualitatively; exact credits are not claimed without a reliable pricing mapping.

## Privacy and scope

The native target is Codex. ChatGPT cloud sessions, Claude, Gemini, Grok, and other providers are not automatically measured. The monitor reads only locally available Codex metadata and does not store prompts, responses, secrets, or authentication data. See [PRIVACY.md](PRIVACY.md).

## Weekly monitor

The weekly monitor is not “advanced” for the person reading its report. It gives a simple summary of recent usage and points out material overuse or underpowered choices. The setup is documented separately because creating or changing a Scheduled Task is an administrative action and should not be mixed into the beginner installation.

## For developers

The scripts use only the Python standard library. Tests, releases, and contribution rules are documented in [CONTRIBUTING.md](CONTRIBUTING.md). Possible future work is listed in [ROADMAP.md](ROADMAP.md).

## License

MIT. Third-party attribution is documented in [`skill/references/third-party.md`](skill/references/third-party.md).
