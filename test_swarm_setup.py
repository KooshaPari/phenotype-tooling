#!/usr/bin/env python
"""
Test script for swarm team generation and agent management.
"""

import asyncio
import json
import aiohttp

BASE_URL = "http://localhost:8005"

async def test_basic_agent_response():
    """Test that the basic agent is working."""
    print("🔧 Testing basic agent response...")
    
    request_data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "Hello! Please confirm you are working and ready for swarm operations."}
        ],
        "stream": False,
        "temperature": 0.7
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/v1/chat/completions",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    print(f"✅ Agent Response: {content}")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ Error {response.status}: {text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error testing basic agent: {e}")
        return False

async def test_agent_management_tools():
    """Test agent management capabilities."""
    print("\n🤖 Testing agent management tools...")
    
    # Test creating an agent
    request_data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "Please use agent management tools to create a new agent named 'test-worker-1' with the role 'code-reviewer'. Show me what tools you have available for agent management."}
        ],
        "stream": False,
        "temperature": 0.7
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/v1/chat/completions",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    print(f"✅ Agent Management Response: {content[:500]}...")
                    
                    # Check if it mentions agent management tools
                    if any(keyword in content.lower() for keyword in ["agent", "create", "management", "tool"]):
                        print("✅ Agent management tools detected in response")
                        return True
                    else:
                        print("⚠️ No agent management tools mentioned")
                        return False
                else:
                    text = await response.text()
                    print(f"❌ Error {response.status}: {text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error testing agent management: {e}")
        return False

async def test_team_communication():
    """Test team communication capabilities."""
    print("\n💬 Testing team communication...")
    
    request_data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "Please use team communication tools to register as an agent and check for any existing team members. What communication tools do you have available?"}
        ],
        "stream": False,
        "temperature": 0.7
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/v1/chat/completions",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    print(f"✅ Team Communication Response: {content[:500]}...")
                    
                    # Check if it mentions communication tools
                    if any(keyword in content.lower() for keyword in ["communication", "team", "register", "member"]):
                        print("✅ Team communication tools detected")
                        return True
                    else:
                        print("⚠️ No team communication tools mentioned")
                        return False
                else:
                    text = await response.text()
                    print(f"❌ Error {response.status}: {text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error testing team communication: {e}")
        return False

async def test_task_coordination():
    """Test basic task coordination."""
    print("\n📋 Testing task coordination...")
    
    request_data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "Please create a simple task for a swarm team: 'Review the codebase and identify potential improvements'. Use any task management tools you have available."}
        ],
        "stream": False,
        "temperature": 0.7
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/v1/chat/completions",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    print(f"✅ Task Coordination Response: {content[:500]}...")
                    
                    # Check if it mentions task management
                    if any(keyword in content.lower() for keyword in ["task", "management", "coordinate", "assign"]):
                        print("✅ Task coordination capabilities detected")
                        return True
                    else:
                        print("⚠️ No task coordination mentioned")
                        return False
                else:
                    text = await response.text()
                    print(f"❌ Error {response.status}: {text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error testing task coordination: {e}")
        return False

async def test_streaming_with_cot():
    """Test streaming with Chain of Thought."""
    print("\n🌊 Testing streaming with COT...")
    
    request_data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "Please think through how to set up a basic swarm team and then create one agent. Use your reasoning process."}
        ],
        "stream": True,
        "temperature": 0.7
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/v1/chat/completions",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    print("✅ Streaming response started...")
                    
                    has_thinking = False
                    has_tool_call = False
                    chunk_count = 0
                    
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]
                            
                            if data_str == '[DONE]':
                                print("✅ Streaming completed with [DONE]")
                                break
                            
                            try:
                                chunk_data = json.loads(data_str)
                                content = chunk_data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                
                                if content:
                                    if "<thinking>" in content:
                                        has_thinking = True
                                        print("✅ Found <thinking> tag in stream")
                                    
                                    if "<tool-call" in content:
                                        has_tool_call = True
                                        print("✅ Found <tool-call> tag in stream")
                                    
                                    chunk_count += 1
                                    
                            except json.JSONDecodeError:
                                continue
                    
                    print(f"✅ Streaming test completed: {chunk_count} chunks")
                    print(f"   - Has thinking tags: {'✅' if has_thinking else '❌'}")
                    print(f"   - Has tool calls: {'✅' if has_tool_call else '❌'}")
                    
                    return chunk_count > 0
                else:
                    text = await response.text()
                    print(f"❌ Streaming error {response.status}: {text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error testing streaming: {e}")
        return False

async def main():
    """Run all swarm setup tests."""
    print("🚀 Starting Swarm Team Generation Test")
    print("=" * 50)
    
    tests = [
        ("Basic Agent", test_basic_agent_response),
        ("Agent Management", test_agent_management_tools),
        ("Team Communication", test_team_communication),
        ("Task Coordination", test_task_coordination),
        ("Streaming COT", test_streaming_with_cot),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            result = await test_func()
            results[test_name] = result
            print(f"{'✅ PASSED' if result else '❌ FAILED'}: {test_name}")
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("🏁 SWARM TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed >= 3:  # At least basic functionality working
        print("🎉 Ready for basic swarm operations!")
        print("\nNext steps:")
        print("1. ✅ Basic agent working")
        print("2. 🔄 Test agent CRUD operations")
        print("3. 🔄 Test inter-agent communication")
        print("4. 🔄 Test coordinated task execution")
    else:
        print("⚠️ Need to fix basic functionality before swarm operations")

if __name__ == "__main__":
    asyncio.run(main())
