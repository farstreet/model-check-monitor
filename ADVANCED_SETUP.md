# Advanced setup and maintenance

This guide is for developers and maintainers. For normal use, [Getting started](GETTING_STARTED.md) is enough.

## Development environment

The scripts use only the Python standard library. A virtual environment is therefore not required for end users, but is recommended for isolated development:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m unittest discover -s tests -v
deactivate
```

## Local data sources

- `~/.codex/config.toml`: current model, reasoning, and service-tier settings when available.
- `~/.codex/models_cache.json`: sanitized catalog with model descriptions and supported levels.
- Local Codex JSONL sessions: recent token and model-settings metadata.

The scripts do not replay conversation content to reconstruct usage.

## Weekly automation

Use Codex Scheduled Tasks with the instructions in [`skill/references/weekly-automation.md`](skill/references/weekly-automation.md). Do not use raw cron. Check for an existing automation with the same name first to avoid duplicates.

## Validation

```sh
python -m compileall -q skill/scripts
python -m unittest discover -s tests -v
python skill/scripts/model_catalog.py --help
python skill/scripts/codex_usage_summary.py --help
python skill/scripts/compare_session_profile.py --help
```

## Platform status

The scripts use the Python standard library and are designed for macOS and Linux. Public documentation claims only the concrete OS and Python versions tested during release validation. Windows and untested Linux distributions are not automatically guaranteed.

## Release and privacy rules

Never commit local Codex metadata, prompts, responses, secrets, `.env` files, or virtual environments. Create release ZIP files only from a clean checkout. See [CONTRIBUTING.md](CONTRIBUTING.md), [PRIVACY.md](PRIVACY.md), and [SECURITY.md](SECURITY.md).
