#!/usr/bin/env python3
"""Derive the only valid model-check action from two model profiles."""

import argparse
import json


UNKNOWN = {"", "unknown", "onbekend", "none", "null", "n/a", "-"}


def known(value):
    """Return a stripped value, or None when the value explicitly is unknown."""
    value = (value or "").strip()
    return value if value.casefold() not in UNKNOWN else None


def same(left, right):
    return left is not None and right is not None and left.casefold() == right.casefold()


def recommended_profile(model, reasoning, tier):
    parts = [model]
    if reasoning:
        parts.append(reasoning)
    if tier:
        parts.append(tier)
    return " · ".join(parts)


def derive_action(recommended_model, recommended_reasoning, recommended_tier,
                  current_model, current_reasoning, current_tier, language="en"):
    """Return a deterministic, user-facing action and a machine-readable decision."""
    recommended_model = known(recommended_model)
    recommended_reasoning = known(recommended_reasoning)
    recommended_tier = known(recommended_tier)
    current_model = known(current_model)
    current_reasoning = known(current_reasoning)
    current_tier = known(current_tier)

    if language not in {"en", "nl"}:
        raise ValueError("language must be en or nl")
    texts = {
        "current_unknown": {
            "en": "current model is unknown; do not claim that the current settings can be kept",
            "nl": "huidige model is onbekend; beweer niet dat de huidige instellingen behouden kunnen blijven",
        },
        "tier_unknown": {
            "en": "keep current model and reasoning level; service tier is unknown",
            "nl": "behoud huidig model en redeneerniveau; serviceniveau is onbekend",
        },
        "keep": {"en": "keep current settings", "nl": "behoud de huidige instellingen"},
    }
    if not recommended_model:
        raise ValueError("recommended model is required")
    if not current_model:
        return {
            "decision": "current_model_unknown",
            "action": texts["current_unknown"][language],
        }
    if not same(recommended_model, current_model):
        return {
            "decision": "switch_profile",
            "action": (
                f"schakel over naar {recommended_profile(recommended_model, recommended_reasoning, recommended_tier)}"
                if language == "nl" else f"switch to {recommended_profile(recommended_model, recommended_reasoning, recommended_tier)}"
            ),
        }

    reasoning_differs = recommended_reasoning is not None and not same(recommended_reasoning, current_reasoning)
    tier_differs = recommended_tier is not None and current_tier is not None and not same(recommended_tier, current_tier)

    if reasoning_differs and tier_differs:
        return {
            "decision": "change_reasoning_and_tier",
            "action": (
                f"pas redeneerniveau aan naar {recommended_reasoning} en serviceniveau naar {recommended_tier}"
                if language == "nl" else f"change reasoning level to {recommended_reasoning} and service tier to {recommended_tier}"
            ),
        }
    if reasoning_differs:
        return {
            "decision": "change_reasoning",
            "action": f"pas redeneerniveau aan naar {recommended_reasoning}" if language == "nl" else f"change reasoning level to {recommended_reasoning}",
        }
    if tier_differs:
        return {
            "decision": "change_service_tier",
            "action": f"pas serviceniveau aan naar {recommended_tier}" if language == "nl" else f"change service tier to {recommended_tier}",
        }
    if recommended_tier is not None and current_tier is None:
        return {
            "decision": "keep_model_and_reasoning_tier_unknown",
            "action": texts["tier_unknown"][language],
        }
    return {"decision": "keep_current", "action": texts["keep"][language]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for prefix in ("recommended", "current"):
        parser.add_argument(f"--{prefix}-model", required=True)
        parser.add_argument(f"--{prefix}-reasoning", default="unknown")
        parser.add_argument(f"--{prefix}-tier", default="unknown")
    parser.add_argument("--language", choices=["en", "nl"], default="en")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()
    result = derive_action(
        args.recommended_model, args.recommended_reasoning, args.recommended_tier,
        args.current_model, args.current_reasoning, args.current_tier, args.language,
    )
    print(json.dumps(result, ensure_ascii=False) if args.format == "json" else result["action"])


if __name__ == "__main__":
    main()
