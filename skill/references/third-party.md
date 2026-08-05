# Third-party attribution

The token-event aggregation approach is derived from
`huajiexiewenfeng/codex-token-usage-skill` (`codex-token-usage`), MIT licensed:

https://github.com/huajiexiewenfeng/codex-token-usage-skill

It sums `last_token_usage` events and deliberately does not sum cumulative
`total_token_usage` values, which would overcount usage.

The required license notice is included in
`references/LICENSE-codex-token-usage.txt`.
