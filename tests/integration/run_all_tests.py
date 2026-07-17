"""
Run all integration tests for the SWE agent.
"""

import os
import asyncio
import argparse
from typing import List, Optional

from tests.integration.test_basic import run_tests as run_basic_tests
from tests.integration.test_tool_check import run_tests as run_tool_check_tests
from tests.integration.test_tool_exec import run_tests as run_tool_exec_tests
from tests.integration.test_reasoning import run_tests as run_reasoning_tests
from tests.integration.llm_critic import evaluate_all_results


async def run_all_tests(test_types: Optional[List[str]] = None):
    """
    Run all integration tests.

    Args:
        test_types: Optional list of test types to run. If None, runs all tests.
    """
    # Create the results directory if it doesn't exist
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)

    # Run the tests
    if test_types is None or "basic" in test_types:
        print("Running basic tests...")
        await run_basic_tests()

    if test_types is None or "tool_check" in test_types:
        print("Running tool check tests...")
        await run_tool_check_tests()

    if test_types is None or "tool_exec" in test_types:
        print("Running tool execution tests...")
        await run_tool_exec_tests()

    if test_types is None or "reasoning" in test_types:
        print("Running reasoning tests...")
        await run_reasoning_tests()

    # Evaluate the results
    print("Evaluating results...")
    await evaluate_all_results()

    print("All tests complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run integration tests for the SWE agent."
    )
    parser.add_argument(
        "--test-types",
        nargs="+",
        choices=["basic", "tool_check", "tool_exec", "reasoning"],
        help="Types of tests to run. If not specified, runs all tests.",
    )
    args = parser.parse_args()

    asyncio.run(run_all_tests(args.test_types))
