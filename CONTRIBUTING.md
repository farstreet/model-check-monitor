# Contributing

Keep this project read-only with respect to usage data and avoid adding provider-specific claims without a reliable metadata source.

## Local setup

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m compileall -q skill/scripts
python -m unittest discover -s tests -v
```

The scripts currently use only the standard library, so no dependency installation is required. Do not commit `.venv/`.

## Before a pull request

- Run the compile and `--help` checks from the README.
- Test missing, malformed and empty metadata inputs.
- Check that prompts, responses, secrets and auth data are not written to output.
- Update the README, changelog or privacy documentation when behavior changes.
- Use a focused commit and explain any compatibility change.
- Generate release ZIP files from a clean checkout; do not commit local ZIP archives.

## Versioning

Use Semantic Versioning. Breaking behavior or metadata-contract changes require a major version; compatible features use a minor version; fixes use a patch version.
