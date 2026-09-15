"""
Week 3 deliverable: run the classifier against ~30 sample questions and
report domain / subtopic accuracy.

Run directly for a human-readable report:
    python -m tests.test_classifier

Run under pytest for a pass/fail gate (defaults: domain >= 0.85, subtopic >= 0.6):
    pytest tests/test_classifier.py
"""
import asyncio
import json
import os

import pytest

from app.classifier import classify_question

SAMPLES_PATH = os.path.join(os.path.dirname(__file__), "sample_questions.json")


def load_samples():
    with open(SAMPLES_PATH) as f:
        return json.load(f)


async def _run_all(samples):
    results = []
    for s in samples:
        intent = await classify_question(s["text"])
        results.append({
            "text": s["text"],
            "expected_domain": s["expected_domain"],
            "expected_subtopic": s["expected_subtopic"],
            "got_domain": intent.domain,
            "got_subtopic": intent.subtopic,
            "confidence": intent.confidence,
        })
    return results


def _score(results):
    n = len(results)
    domain_correct = sum(r["got_domain"] == r["expected_domain"] for r in results)
    subtopic_correct = sum(
        r["got_domain"] == r["expected_domain"] and r["got_subtopic"] == r["expected_subtopic"]
        for r in results
    )
    return domain_correct / n, subtopic_correct / n


def _print_report(results, domain_acc, subtopic_acc):
    print(f"\n{'question':60s} {'expected':30s} {'got':30s}")
    print("-" * 122)
    for r in results:
        expected = f"{r['expected_domain']}/{r['expected_subtopic']}"
        got = f"{r['got_domain']}/{r['got_subtopic']} ({r['confidence']:.2f})"
        mark = "OK" if got.startswith(expected.split("(")[0].strip()) else "XX"
        print(f"[{mark}] {r['text'][:56]:56s} {expected:30s} {got:30s}")
    print("-" * 122)
    print(f"Domain accuracy:   {domain_acc:.0%}")
    print(f"Subtopic accuracy: {subtopic_acc:.0%}")


@pytest.mark.asyncio
async def test_classifier_accuracy():
    """Requires a running Ollama instance with the configured model pulled."""
    samples = load_samples()
    results = await _run_all(samples)
    domain_acc, subtopic_acc = _score(results)
    _print_report(results, domain_acc, subtopic_acc)
    assert domain_acc >= 0.85, f"domain accuracy too low: {domain_acc:.0%}"
    assert subtopic_acc >= 0.60, f"subtopic accuracy too low: {subtopic_acc:.0%}"


if __name__ == "__main__":
    samples = load_samples()
    results = asyncio.run(_run_all(samples))
    domain_acc, subtopic_acc = _score(results)
    _print_report(results, domain_acc, subtopic_acc)
