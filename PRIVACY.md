# Privacy

Model Check Monitor is designed to inspect local metadata without storing conversation content.

## Read data

When available, the skill reads model settings from `~/.codex/config.toml`, model descriptions from `~/.codex/models_cache.json`, and recent token/model metadata from local Codex JSONL session files.

## Not read or stored

The scripts do not intentionally read or store prompts, responses, secrets, authentication data or full conversation content. Reports contain aggregate counts and model-settings metadata only.

Cloud history may expose less metadata than local Codex sessions. Such gaps are reported as limitations rather than inferred as facts.
