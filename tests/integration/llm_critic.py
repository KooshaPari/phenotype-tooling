"""
LLM critic for evaluating SWE agent responses.
"""
import os
import json
import asyncio
from typing import Dict, List, Any, Optional
import openai
from openai import OpenAI


class LLMCritic:
    """
    LLM critic for evaluating SWE agent responses.
    """

    def __init__(self, api_key: REDACTED_AIRLOCK = None):
        """
        Initialize the LLM critic.

        Args:
            api_key: REDACTED_AIRLOCK OpenAI API key. If None, uses the OPENAI_API_KEY environment variable.
        """
        self.client = OpenAI(api_key=REDACTED_AIRLOCK

    async def evaluate_basic_response(self, results_file: str) -> Dict[str, Any]:
        """
        Evaluate a basic response.

        Args:
            results_file: Path to the results file.

        Returns:
            The evaluation results.
        """
        # Load the results
        with open(results_file, "r") as f:
            results = json.load(f)

        # Extract the relevant information
        prompt = results["prompt"]
        response_content = results["response"]["content"]
        model = results["response"]["model"]
        streaming = results["response"]["streaming"]

        # Create the evaluation prompt
        evaluation_prompt = f"""
        You are an expert evaluator of AI assistant responses. You need to evaluate the following response to a basic question.

        Question: {prompt}
        Model: {model}
        Streaming: {streaming}
        Response: {response_content}

        Please evaluate the response based on the following criteria:
        1. Correctness: Is the response factually correct?
        2. Completeness: Does the response fully answer the question?
        3. Clarity: Is the response clear and easy to understand?
        4. Conciseness: Is the response appropriately concise?

        Provide a detailed critique and an overall score from 1-10.
        """

        # Get the evaluation
        evaluation = await self._get_evaluation(evaluation_prompt)

        # Update the results with the evaluation
        results["evaluation"]["critique"] = evaluation
        
        # Save the updated results
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        return results

    async def evaluate_tool_check_response(self, results_file: str) -> Dict[str, Any]:
        """
        Evaluate a tool check response.

        Args:
            results_file: Path to the results file.

        Returns:
            The evaluation results.
        """
        # Load the results
        with open(results_file, "r") as f:
            results = json.load(f)

        # Extract the relevant information
        prompt = results["prompt"]
        response_content = results["response"]["content"]
        model = results["response"]["model"]
        streaming = results["response"]["streaming"]
        config_tools = results["config_tools"]

        # Create the evaluation prompt
        evaluation_prompt = f"""
        You are an expert evaluator of AI assistant responses. You need to evaluate the following response to a question about MCP tools.

        Question: {prompt}
        Model: {model}
        Streaming: {streaming}
        Response: {response_content}

        The agent should have access to the following MCP tools according to the configuration:
        {json.dumps(config_tools, indent=2)}

        Please evaluate the response based on the following criteria:
        1. Tool Recognition: Does the response correctly identify the MCP tools available?
        2. Completeness: Does the response mention all the tools in the configuration?
        3. Accuracy: Is the description of the tools accurate?
        4. Clarity: Is the response clear and easy to understand?

        Provide a detailed critique and an overall score from 1-10.
        """

        # Get the evaluation
        evaluation = await self._get_evaluation(evaluation_prompt)

        # Update the results with the evaluation
        results["evaluation"]["critique"] = evaluation
        
        # Save the updated results
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        return results

    async def evaluate_tool_exec_response(self, results_file: str) -> Dict[str, Any]:
        """
        Evaluate a tool execution response.

        Args:
            results_file: Path to the results file.

        Returns:
            The evaluation results.
        """
        # Load the results
        with open(results_file, "r") as f:
            results = json.load(f)

        # Extract the relevant information
        prompt = results["prompt"]
        response_content = results["response"]["content"]
        model = results["response"]["model"]
        streaming = results["response"]["streaming"]
        tool_info = results["sequential_thinking_tool_info"]

        # Create the evaluation prompt
        evaluation_prompt = f"""
        You are an expert evaluator of AI assistant responses. You need to evaluate the following response to a request to use the Sequential Thinking tool.

        Request: {prompt}
        Model: {model}
        Streaming: {streaming}
        Response: {response_content}

        The Sequential Thinking tool information:
        {json.dumps(tool_info, indent=2)}

        Please evaluate the response based on the following criteria:
        1. Tool Usage: Does the response show evidence of using the Sequential Thinking tool?
        2. Step-by-Step Approach: Does the response break down the problem into sequential steps?
        3. Thoroughness: Does the response thoroughly address the problem?
        4. Clarity: Is the response clear and easy to understand?

        Provide a detailed critique and an overall score from 1-10.
        """

        # Get the evaluation
        evaluation = await self._get_evaluation(evaluation_prompt)

        # Update the results with the evaluation
        results["evaluation"]["critique"] = evaluation
        
        # Save the updated results
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        return results

    async def evaluate_reasoning_response(self, results_file: str) -> Dict[str, Any]:
        """
        Evaluate a reasoning response.

        Args:
            results_file: Path to the results file.

        Returns:
            The evaluation results.
        """
        # Load the results
        with open(results_file, "r") as f:
            results = json.load(f)

        # Extract the relevant information
        prompt = results["prompt"]
        response_content = results["response"]["content"]
        model = results["response"]["model"]
        streaming = results["response"]["streaming"]

        # Create the evaluation prompt
        evaluation_prompt = f"""
        You are an expert evaluator of AI assistant responses. You need to evaluate the following response to a question requiring reasoning.

        Question: {prompt}
        Model: {model}
        Streaming: {streaming}
        Response: {response_content}

        Please evaluate the response based on the following criteria:
        1. Conceptual Understanding: Does the response demonstrate a clear understanding of recursion?
        2. Example Quality: Is the example provided clear, correct, and illustrative?
        3. Explanation Quality: Is the explanation thorough and easy to understand?
        4. Technical Accuracy: Is the technical information accurate?

        Provide a detailed critique and an overall score from 1-10.
        """

        # Get the evaluation
        evaluation = await self._get_evaluation(evaluation_prompt)

        # Update the results with the evaluation
        results["evaluation"]["critique"] = evaluation
        
        # Save the updated results
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        return results

    async def _get_evaluation(self, prompt: str) -> str:
        """
        Get an evaluation from the LLM.

        Args:
            prompt: The evaluation prompt.

        Returns:
            The evaluation.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error getting evaluation: {e}"


async def evaluate_all_results():
    """
    Evaluate all test results.
    """
    # Create the LLM critic
    critic = LLMCritic()
    
    # Get all results files
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    if not os.path.exists(results_dir):
        print(f"Results directory {results_dir} does not exist.")
        return
    
    results_files = [
        os.path.join(results_dir, f)
        for f in os.listdir(results_dir)
        if f.endswith(".json")
    ]
    
    # Evaluate each results file
    for results_file in results_files:
        print(f"Evaluating {results_file}...")
        
        # Determine the evaluation function based on the file name
        if "basic" in results_file:
            await critic.evaluate_basic_response(results_file)
        elif "tool_check" in results_file:
            await critic.evaluate_tool_check_response(results_file)
        elif "tool_exec" in results_file:
            await critic.evaluate_tool_exec_response(results_file)
        elif "reasoning" in results_file:
            await critic.evaluate_reasoning_response(results_file)
        else:
            print(f"Unknown test type for {results_file}.")
    
    print("Evaluation complete.")


if __name__ == "__main__":
    asyncio.run(evaluate_all_results())
