"""
Script to run tests for the SWE agent.
"""

import unittest
import asyncio
import argparse
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

from tests.test_agent import TestSWEAgent, run_async_test

# Import integration tests
try:
    from tests.integration.run_all_tests import run_all_tests

    INTEGRATION_TESTS_AVAILABLE = True
except ImportError:
    INTEGRATION_TESTS_AVAILABLE = False
    print("Integration tests not available. Skipping.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tests for the SWE agent.")
    parser.add_argument("--unit", action="store_true", help="Run unit tests.")
    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests."
    )
    parser.add_argument(
        "--test-types",
        nargs="+",
        choices=["basic", "tool_check", "tool_exec", "reasoning"],
        help="Types of integration tests to run. If not specified, runs all tests.",
    )
    parser.add_argument(
        "--use-server",
        action="store_true",
        help="Use the actual server for tests. If not specified, uses mock responses.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-3.5-turbo",
        help="Model to use for tests. Default is gpt-3.5-turbo.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with more verbose output.",
    )
    args = parser.parse_args()

    # If no test type is specified, run all tests
    if not args.unit and not args.integration:
        args.unit = True
        args.integration = True

    # Run unit tests
    if args.unit:
        print("Running unit tests...")
        suite = unittest.TestSuite()
        suite.addTest(TestSWEAgent("test_initialize"))
        runner = unittest.TextTestRunner()
        runner.run(suite)

    # Run integration tests
    if args.integration and INTEGRATION_TESTS_AVAILABLE:
        print("Running integration tests...")
        # Import the test_base module to set the USE_ACTUAL_SERVER flag
        import tests.integration.test_base as test_base

        # Set the test_base module options based on the command-line options
        if args.use_server:
            print("Using actual server for tests...")
            test_base.USE_ACTUAL_SERVER = True
        else:
            print("Using mock responses for tests...")
            test_base.USE_ACTUAL_SERVER = False

        # Set the model to use
        print(f"Using model {args.model} for tests...")
        test_base.TEST_MODEL = args.model

        # Set debug mode
        if args.debug:
            print("Debug mode enabled...")
            test_base.DEBUG_MODE = True

        asyncio.run(run_all_tests(args.test_types))
