"""
Eval orchestrator: runs all regression + adversarial tests.

Usage:
    cd api
    python -m tests.eval.run_all             # run everything
    python -m tests.eval.run_all -v          # verbose
    python -m tests.eval.run_all --regression-only   # regression only
    python -m tests.eval.run_all --adversarial-only  # adversarial only
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Delay between tests to avoid Groq TPD rate limit (free tier: 100k tokens/day)
_TEST_DELAY = 2.0

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dotenv import load_dotenv

load_dotenv()

from tests.eval.adversarial import run_adversarial
from tests.eval.fixtures import ADVERSARIAL_FIXTURES, REGRESSION_FIXTURES
from tests.eval.metrics import print_result, summary
from tests.eval.regression import run_regression


def get_agent():
    from app.agents.graph import rag_agent

    return rag_agent


def run_all(args):
    """Run the full eval suite."""
    print(f"\n{'='*60}")
    print(f"  COMPLISO.AI — FULL EVAL SUITE")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    agent = get_agent()
    all_results = []

    # ── Regression ────────────────────────────────────────
    if not args.adversarial_only:
        reg_fixtures = REGRESSION_FIXTURES
        print(f"\n--- REGRESSION ({len(reg_fixtures)} tests) ---\n")
        for fixture in reg_fixtures:
            start = time.time()
            result = run_regression(fixture, agent=agent, verbose=args.verbose)
            elapsed = time.time() - start
            result.notes += f" ({elapsed:.1f}s)"
            all_results.append(("regression", result))
            print(print_result(result, verbose=args.verbose))
            time.sleep(_TEST_DELAY)

    # ── Adversarial ───────────────────────────────────────
    if not args.regression_only:
        adv_fixtures = ADVERSARIAL_FIXTURES
        print(f"\n--- ADVERSARIAL ({len(adv_fixtures)} tests) ---\n")
        for fixture in adv_fixtures:
            start = time.time()
            result = run_adversarial(fixture, agent=agent, verbose=args.verbose)
            elapsed = time.time() - start
            result.notes += f" ({elapsed:.1f}s)"
            all_results.append(("adversarial", result))
            print(print_result(result, verbose=args.verbose))
            time.sleep(_TEST_DELAY)

    # ── Summary ───────────────────────────────────────────
    reg_results = [r for t, r in all_results if t == "regression"]
    adv_results = [r for t, r in all_results if t == "adversarial"]
    reg_stats = summary(reg_results) if reg_results else {}
    adv_stats = summary(adv_results) if adv_results else {}
    total_stats = summary([r for _, r in all_results])

    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    if reg_stats:
        print(f"  Regression:   {reg_stats['passed']}/{reg_stats['total']} ({reg_stats['pass_rate']})")
    if adv_stats:
        print(f"  Adversarial:  {adv_stats['passed']}/{adv_stats['total']} ({adv_stats['pass_rate']})")
    print(f"  {'─'*40}")
    print(f"  Total:        {total_stats['passed']}/{total_stats['total']} ({total_stats['pass_rate']})")
    print(f"{'='*60}\n")

    # ── Save report ───────────────────────────────────────
    if args.output:
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": total_stats,
            "regression": reg_stats,
            "adversarial": adv_stats,
            "results": [
                {
                    "type": t,
                    "id": r.fixture_id,
                    "question": r.question,
                    "passed": r.passed,
                    "keyword_misses": r.keyword_misses,
                    "forbidden_hits": r.forbidden_hits,
                    "answer_preview": r.answer[:500],
                }
                for t, r in all_results
            ],
        }
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {output_path}")

    # Exit with non-zero if any failures
    failed = total_stats.get("failed", 0)
    sys.exit(0 if failed == 0 else 1)


def main():
    parser = argparse.ArgumentParser(description="Run full Compliso eval suite")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--regression-only", action="store_true")
    parser.add_argument("--adversarial-only", action="store_true")
    parser.add_argument("--output", type=str, help="Save JSON report to file")
    args = parser.parse_args()
    run_all(args)


if __name__ == "__main__":
    main()
