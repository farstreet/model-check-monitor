import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill" / "scripts"


class ScriptSmokeTests(unittest.TestCase):
    def run_script(self, name, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / name), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout

    def test_model_catalog_handles_sanitized_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "models.json"
            path.write_text(json.dumps({"models": [{"slug": "demo", "display_name": "Demo"}]}))
            output = self.run_script("model_catalog.py", "--path", str(path), "--format", "json")
            report = json.loads(output)
            self.assertTrue(report["available"])
            self.assertEqual(report["models"][0]["slug"], "demo")

    def test_model_catalog_reports_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = self.run_script("model_catalog.py", "--path", str(Path(tmp) / "missing.json"), "--format", "json")
            self.assertFalse(json.loads(output)["available"])

    def test_usage_summary_ignores_malformed_lines_and_deduplicates_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            session_dir = Path(tmp) / "sessions"
            session_dir.mkdir()
            session = session_dir / "00000000-0000-0000-0000-000000000001.jsonl"
            event = {
                "timestamp": "2099-01-01T00:00:00Z",
                "payload": {"type": "token_count", "info": {"last_token_usage": {
                    "total_tokens": 10, "input_tokens": 6, "cached_input_tokens": 2,
                    "output_tokens": 4, "reasoning_output_tokens": 1,
                }}},
            }
            settings = {"timestamp": "2099-01-01T00:00:00Z", "payload": {
                "type": "thread_settings_applied", "thread_settings": {
                    "model": "demo", "reasoning_effort": "low", "service_tier": "normal"
                }
            }}
            session.write_text("not json\n" + json.dumps(settings) + "\n" + json.dumps(event) + "\n" + json.dumps(event) + "\n")
            output = self.run_script("codex_usage_summary.py", "--codex-home", tmp, "--days", "8", "--format", "json")
            report = json.loads(output)
            self.assertEqual(report["sessions"], 1)
            self.assertEqual(report["token_events"], 1)
            self.assertEqual(report["tokens"]["total"], 10)
            self.assertEqual(report["tokens"]["net"], 8)

    def test_compare_session_reports_missing_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = self.run_script("compare_session_profile.py", "--codex-home", tmp, "--session-id", "missing", "--format", "json")
            self.assertFalse(json.loads(output)["available"])

    def test_compare_session_reports_actual_tokens_without_double_counting(self):
        with tempfile.TemporaryDirectory() as tmp:
            session_dir = Path(tmp) / "sessions"
            session_dir.mkdir()
            session = session_dir / "00000000-0000-0000-0000-000000000002.jsonl"
            settings = {"type": "thread_settings_applied", "thread_settings": {
                "model": "demo", "reasoning_effort": "medium", "service_tier": "normal"
            }}
            usage = {"type": "token_count", "info": {"last_token_usage": {
                "total_tokens": 10, "input_tokens": 6, "cached_input_tokens": 2, "output_tokens": 4
            }}}
            session.write_text(json.dumps(settings) + "\n" + json.dumps(usage) + "\n")
            output = self.run_script("compare_session_profile.py", "--codex-home", tmp, "--session-id", "00000000-0000-0000-0000-000000000002", "--format", "json")
            report = json.loads(output)
            self.assertEqual(report["actual"]["tokens"], 10)
            self.assertEqual(report["actual"]["models"], {"demo": 1})
            self.assertEqual(report["estimated_task_complexity"], "simple")

    def test_profile_action_switches_when_models_differ(self):
        output = self.run_script(
            "profile_action.py",
            "--recommended-model", "GPT-5.6-Sol",
            "--recommended-reasoning", "low",
            "--recommended-tier", "normal service",
            "--current-model", "GPT-5.6-Luna",
            "--current-reasoning", "low",
            "--current-tier", "unknown",
            "--format", "json",
        )
        report = json.loads(output)
        self.assertEqual(report["decision"], "switch_profile")
        self.assertEqual(report["action"], "switch to GPT-5.6-Sol · low · normal service")

    def test_profile_action_keeps_matching_profile(self):
        output = self.run_script(
            "profile_action.py",
            "--recommended-model", "GPT-5.6-Luna",
            "--recommended-reasoning", "low",
            "--recommended-tier", "normal",
            "--current-model", "GPT-5.6-Luna",
            "--current-reasoning", "low",
            "--current-tier", "normal",
            "--format", "json",
        )
        self.assertEqual(json.loads(output)["decision"], "keep_current")

    def test_profile_action_changes_only_reasoning_when_model_matches(self):
        output = self.run_script(
            "profile_action.py",
            "--recommended-model", "GPT-5.6-Luna",
            "--recommended-reasoning", "medium",
            "--recommended-tier", "normal",
            "--current-model", "GPT-5.6-Luna",
            "--current-reasoning", "low",
            "--current-tier", "normal",
            "--format", "json",
        )
        report = json.loads(output)
        self.assertEqual(report["decision"], "change_reasoning")
        self.assertEqual(report["action"], "change reasoning level to medium")

    def test_profile_action_does_not_claim_full_match_when_tier_is_unknown(self):
        output = self.run_script(
            "profile_action.py",
            "--recommended-model", "GPT-5.6-Luna",
            "--recommended-reasoning", "low",
            "--recommended-tier", "normal",
            "--current-model", "GPT-5.6-Luna",
            "--current-reasoning", "low",
            "--current-tier", "unknown",
            "--format", "json",
        )
        report = json.loads(output)
        self.assertEqual(report["decision"], "keep_model_and_reasoning_tier_unknown")
        self.assertIn("service tier is unknown", report["action"])

    def test_profile_action_can_emit_dutch_action(self):
        output = self.run_script(
            "profile_action.py",
            "--recommended-model", "GPT-5.6-Sol",
            "--recommended-reasoning", "low",
            "--recommended-tier", "normal",
            "--current-model", "GPT-5.6-Luna",
            "--current-reasoning", "low",
            "--current-tier", "unknown",
            "--language", "nl",
        )
        self.assertEqual(output.strip(), "schakel over naar GPT-5.6-Sol · low · normal")


if __name__ == "__main__":
    unittest.main()
