"""
Adversarial tests: verify the agent handles tricky/noisy inputs correctly.

Usage:
    cd api
    python -m tests.eval.adversarial          # run all adversarial tests
    python -m tests.eval.adversarial -v        # verbose
    python -m tests.eval.adversarial --fixture ADV-001  # run single test
"""

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dotenv import load_dotenv

load_dotenv()

from tests.eval.fixtures import ADVERSARIAL_FIXTURES
from tests.eval.metrics import EvalResult, print_result, score_answer, summary


def get_agent():
    """Lazy-load the compiled agent."""
    from app.agents.graph import rag_agent

    return rag_agent


def run_adversarial(fixture: dict, agent=None, verbose: bool = False) -> EvalResult:
    """Run a single adversarial test."""
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
    parser = argparse.ArgumentParser(description="Run adversarial eval tests")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--fixture", type=str, help="Run a specific fixture by ID")
    args = parser.parse_args()

    if args.fixture:
        fixtures = [f for f in ADVERSARIAL_FIXTURES if f["id"] == args.fixture]
        if not fixtures:
            print(f"Fixture {args.fixture} not found")
            sys.exit(1)
    else:
        fixtures = ADVERSARIAL_FIXTURES

    print(f"\n{'='*60}")
    print(f"  ADVERSARIAL EVAL — {len(fixtures)} tests")
    print(f"{'='*60}\n")

    agent = get_agent()
    results = []

    for fixture in fixtures:
        start = time.time()
        result = run_adversarial(fixture, agent=agent, verbose=args.verbose)
        elapsed = time.time() - start
        result.notes += f" ({elapsed:.1f}s)"
        results.append(result)
        print(print_result(result, verbose=args.verbose))
        print()

    stats = summary(results)
    print(f"{'='*60}")
    print(f"  RESULTS: {stats['passed']}/{stats['total']} passed ({stats['pass_rate']})")
    print(f"{'='*60}\n")

    sys.exit(0 if stats["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
