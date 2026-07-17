import asyncio
from mcp.client import mcp_client_manager

async def main():
    await mcp_client_manager.initialize()
    
    # Find the Canvas tool
    tool = next(t for t in mcp_client_manager.tools if t.name == 'canvas_list_student_courses')
    
    print(f'Tool name: {tool.name}')
    print(f'Tool type: {type(tool)}')
    print(f'Has args_schema: {hasattr(tool, "args_schema")}')
    
    if hasattr(tool, "args_schema"):
        print(f'Args schema: {tool.args_schema}')
        if hasattr(tool.args_schema, "__annotations__"):
            print(f'Args schema annotations: {tool.args_schema.__annotations__}')
    
    print(f'Has coroutine: {hasattr(tool, "coroutine")}')
    print(f'Has func: {hasattr(tool, "func")}')
    print(f'Has _run: {hasattr(tool, "_run")}')
    print(f'Has run: {hasattr(tool, "run")}')
    print(f'Has invoke: {hasattr(tool, "invoke")}')
    print(f'Has ainvoke: {hasattr(tool, "ainvoke")}')
    
    # Try to inspect the args_schema more deeply
    if hasattr(tool, "args_schema"):
        print("\nArgs schema details:")
        schema_dir = dir(tool.args_schema)
        print(f'Schema dir: {schema_dir}')
        
        if hasattr(tool.args_schema, "schema"):
            print(f'Schema schema: {tool.args_schema.schema()}')
        
        if hasattr(tool.args_schema, "model_fields"):
            print(f'Schema model_fields: {tool.args_schema.model_fields}')
    
    # Try to inspect the coroutine
    if hasattr(tool, "coroutine"):
        print("\nCoroutine details:")
        print(f'Coroutine: {tool.coroutine}')
        print(f'Coroutine signature: {tool.coroutine.__code__.co_varnames if hasattr(tool.coroutine, "__code__") else "No code attribute"}')

if __name__ == "__main__":
    asyncio.run(main())
