import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import pytest
from typing import AsyncIterator, Dict, Any

from langchain_core.agents import AgentAction
from langchain_core.messages import AIMessage, ToolMessage
from api.streaming_sse import sse_from_agent

class DummyAgentAction(AgentAction):
    def __init__(self, tool: str, tool_input: Any):
        super().__init__(tool=tool, tool_input=tool_input)
        self.id = "dummy-id"

class DummyToolMessage(ToolMessage):
    def __init__(self, content: str, tool_call_id: str):
        super().__init__(content=content, tool_call_id=tool_call_id)

@pytest.mark.asyncio
async def test_sse_from_agent_sequence():
    async def fake_agent_stream() -> AsyncIterator[Dict[str, Any]]:
        # Simulate AgentAction
        yield {"messages": [DummyAgentAction("tool1", {"param": "value"})]}
        # Simulate ToolMessage result
        yield {"messages": [DummyToolMessage("result", "dummy-id")]}
        # Simulate AIMessage text
        yield {"messages": [AIMessage(content="Hello world!")]}
    completion_id = "test-id"
    created_ts = 12345
    model = "test-model"
    events = []
    async for event in sse_from_agent(fake_agent_stream(), completion_id, created_ts, model):
        events.append(event.strip())
    # First event should be response.created
    assert events[0].startswith("event: response.created")
    # There should be a function call added event
    assert any("response.output_item.added" in e for e in events)
    # There should be argument delta events
    assert any("response.function_call_arguments.delta" in e for e in events)
    # There should be function_call_arguments.done
    assert any("response.function_call_arguments.done" in e for e in events)
    # There should be output_item.done for tool result
    assert any("response.output_item.done" in e for e in events)
    # There should be output_text.delta for assistant message
    assert any("response.output_text.delta" in e for e in events)
    # Last event should be response.completed
    assert events[-1].startswith("event: response.completed")
