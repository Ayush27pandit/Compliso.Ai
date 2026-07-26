"""
Regression tests: verify the agent answers questions correctly from true_data.

Usage:
    cd api
    python -m tests.eval.regression          # run all regression tests
    python -m tests.eval.regression -v        # verbose
    python -m tests.eval.regression --fixture REG-001  # run single test
"""

import argparse
import os
import sys
import time
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dotenv import load_dotenv

load_dotenv()

from tests.eval.fixtures import REGRESSION_FIXTURES
from tests.eval.metrics import EvalResult, print_result, score_answer, summary


def get_agent():
    """Lazy-load the compiled agent."""
    from app.agents.graph import rag_agent

    return rag_agent


def run_regression(fixture: dict, agent=None, verbose: bool = False) -> EvalResult:
    """Run a single regression test."""
    if agent is None:
        agent = get_agent()

    from app.agents.state import AgentState

    state: AgentState = {
        "messages": [{"role": "user", "content": fixture["question"]}],
        "current_query": fixture["question"],
        "documents": [],
        "plan": "",
        "status": "",
        "final_answer": "",
    }

    config = {"configurable": {"thread_id": f"eval-{fixture['id']}"}}

    try:
        result = agent.invoke(state, config=config)
        answer = result.get("final_answer", "")
    except Exception as e:
        answer = f"ERROR: {e}"

    return score_answer(fixture, answer)


def main():
    parser = argparse.ArgumentParser(description="Run regression eval tests")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--fixture", type=str, help="Run a specific fixture by ID")
    args = parser.parse_args()

    if args.fixture:
        fixtures = [f for f in REGRESSION_FIXTURES if f["id"] == args.fixture]
        if not fixtures:
            print(f"Fixture {args.fixture} not found")
            sys.exit(1)
    else:
        fixtures = REGRESSION_FIXTURES

    print(f"\n{'='*60}")
    print(f"  REGRESSION EVAL — {len(fixtures)} tests")
    print(f"{'='*60}\n")

    agent = get_agent()
    results = []

    for fixture in fixtures:
        start = time.time()
        result = run_regression(fixture, agent=agent, verbose=args.verbose)
        elapsed = time.time() - start
        result.notes += f" ({elapsed:.1f}s)"
        results.append(result)
        print(print_result(result, verbose=args.verbose))
        print()

    stats = summary(results)
    print(f"{'='*60}")
    print(f"  RESULTS: {stats['passed']}/{stats['total']} passed ({stats['pass_rate']})")
    print(f"{'='*60}\n")

    # Exit with non-zero if any failures
    sys.exit(0 if stats["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
