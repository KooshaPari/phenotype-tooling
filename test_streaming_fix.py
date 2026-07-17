#!/usr/bin/env python
"""
Test script to verify streaming is working correctly with COT events.
"""

import asyncio
import json
import aiohttp

async def test_streaming_response():
    """Test that streaming responses are properly formatted and processable."""
    print("Testing streaming response...")
    
    # Test data
    test_request = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "Hello, please use a tool to help me with something simple."}
        ],
        "stream": True,
        "temperature": 0.7
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8002/v1/chat/completions",
                json=test_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                print(f"Response status: {response.status}")
                print(f"Response headers: {dict(response.headers)}")
                
                if response.status != 200:
                    text = await response.text()
                    print(f"Error response: {text}")
                    return False
                
                # Check that it's actually streaming
                if response.headers.get("content-type") != "text/event-stream":
                    print(f"❌ Wrong content type: {response.headers.get('content-type')}")
                    return False
                
                print("✅ Correct content-type: text/event-stream")
                
                # Read streaming chunks
                chunk_count = 0
                has_thinking = False
                has_tool_call = False
                has_tool_response = False
                has_final_response = False
                has_done = False
                
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    
                    if not line_str:
                        continue
                    
                    print(f"Chunk {chunk_count}: {line_str}")
                    
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        
                        if data_str == '[DONE]':
                            has_done = True
                            print("✅ Received [DONE] marker")
                            break
                        
                        try:
                            chunk_data = json.loads(data_str)
                            
                            # Validate chunk structure
                            if not isinstance(chunk_data, dict):
                                print(f"❌ Chunk is not a dict: {type(chunk_data)}")
                                continue
                            
                            required_fields = ["id", "object", "created", "model", "choices"]
                            for field in required_fields:
                                if field not in chunk_data:
                                    print(f"❌ Missing field '{field}' in chunk")
                                    continue
                            
                            # Check choices structure
                            choices = chunk_data.get("choices", [])
                            if not choices:
                                print("❌ No choices in chunk")
                                continue
                            
                            choice = choices[0]
                            delta = choice.get("delta", {})
                            content = delta.get("content", "")
                            
                            if content:
                                print(f"  Content: {content[:100]}...")
                                
                                # Check for COT elements
                                if "<thinking>" in content:
                                    has_thinking = True
                                    print("  ✅ Found <thinking> tag")
                                
                                if "<tool-call" in content:
                                    has_tool_call = True
                                    print("  ✅ Found <tool-call> tag")
                                
                                if "<tool-response" in content:
                                    has_tool_response = True
                                    print("  ✅ Found <tool-response> tag")
                                
                                # Check if this looks like a final response
                                if not any(tag in content for tag in ["<thinking>", "<tool-call", "<tool-response"]):
                                    has_final_response = True
                                    print("  ✅ Found final response content")
                            
                            chunk_count += 1
                            
                        except json.JSONDecodeError as e:
                            print(f"❌ Invalid JSON in chunk: {e}")
                            print(f"  Raw data: {data_str}")
                            continue
                
                # Summary
                print(f"\n=== STREAMING TEST SUMMARY ===")
                print(f"Total chunks received: {chunk_count}")
                print(f"Has <thinking> tags: {'✅' if has_thinking else '❌'}")
                print(f"Has <tool-call> tags: {'✅' if has_tool_call else '❌'}")
                print(f"Has <tool-response> tags: {'✅' if has_tool_response else '❌'}")
                print(f"Has final response: {'✅' if has_final_response else '❌'}")
                print(f"Has [DONE] marker: {'✅' if has_done else '❌'}")
                
                # Overall success
                success = (
                    chunk_count > 0 and
                    has_done and
                    (has_thinking or has_tool_call or has_final_response)
                )
                
                if success:
                    print("✅ STREAMING TEST PASSED!")
                else:
                    print("❌ STREAMING TEST FAILED!")
                
                return success
                
    except Exception as e:
        print(f"❌ Error testing streaming: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_non_streaming_comparison():
    """Test non-streaming response for comparison."""
    print("\nTesting non-streaming response for comparison...")
    
    test_request = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "Hello, please respond briefly."}
        ],
        "stream": False,
        "temperature": 0.7
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8002/v1/chat/completions",
                json=test_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status != 200:
                    text = await response.text()
                    print(f"Error response: {text}")
                    return False
                
                data = await response.json()
                print(f"Non-streaming response structure: {list(data.keys())}")
                
                if "choices" in data and data["choices"]:
                    content = data["choices"][0].get("message", {}).get("content", "")
                    print(f"Non-streaming content preview: {content[:100]}...")
                
                return True
                
    except Exception as e:
        print(f"❌ Error testing non-streaming: {e}")
        return False

async def main():
    """Run streaming tests."""
    print("Streaming Fix Test")
    print("==================")
    
    success1 = await test_non_streaming_comparison()
    success2 = await test_streaming_response()
    
    if success1 and success2:
        print("\n✅ All streaming tests passed!")
        print("Streaming should now work correctly with COT events.")
    else:
        print("\n❌ Some streaming tests failed!")

if __name__ == "__main__":
    asyncio.run(main())
