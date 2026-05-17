import os
import json
import asyncio
import re
from typing import List, Dict, Any, AsyncGenerator
from ollama import AsyncClient
from dotenv import load_dotenv
from agentic.infrastructure.tools import TOOLS, AVAILABLE_FUNCTIONS

load_dotenv()

class OllamaClient:
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
        self.host = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.client = AsyncClient(host=self.host)

    async def generate_response_stream(self, history: List[Dict[str, str]], message: str) -> AsyncGenerator[str, None]:
        # 1. System Instruction
        system_msg = {
            "role": "system", 
            "content": "You are a helpful assistant. Use tools for math, date, or weather. If no tools are needed, answer the user directly in plain text."
        }
        messages = [system_msg] + history + [{"role": "user", "content": message}]
        
        while True:
            # We do a non-streaming call first. 
            # This is actually FASTER on low RAM than opening a long-running stream connection.
            response = await self.client.chat(
                model=self.model,
                messages=messages,
                tools=TOOLS
            )

            tool_calls = getattr(response.message, 'tool_calls', [])
            
            # --- Fallback: Hallucinated JSON (Catch small model mistakes) ---
            if not tool_calls and response.message.content:
                json_match = re.search(r'\{.*"name".*\}', response.message.content, re.DOTALL)
                if json_match:
                    try:
                        potential_tool = json.loads(json_match.group())
                        if "name" in potential_tool:
                            from types import SimpleNamespace
                            args = potential_tool.get("parameters", potential_tool.get("arguments", {}))
                            if isinstance(args, list) and len(args) > 0: args = args[0]
                            fake_tool = SimpleNamespace(function=SimpleNamespace(name=potential_tool["name"], arguments=args))
                            tool_calls = [fake_tool]
                            print(f"DEBUG: Caught hallucinated tool call: {potential_tool['name']}")
                    except: pass

            # --- Case A: No Tools (The most common case) ---
            if not tool_calls:
                if response.message.content:
                    # SIMULATED STREAM: 
                    # Instead of a second AI call, we split the text and yield it.
                    # This feels like streaming to the UI but saves 90+ seconds of hardware wait.
                    words = response.message.content.split(' ')
                    for word in words:
                        yield word + ' '
                        await asyncio.sleep(0.02) # Standard human reading speed delay
                break

            # --- Case B: Tools Found (Math, Weather, Date) ---
            messages.append(response.message)
            for tool in tool_calls:
                function_name = tool.function.name
                args = tool.function.arguments
                
                # Cleanup arguments if they arrived as a string
                if isinstance(args, str):
                    try: args = json.loads(args)
                    except: args = {}
                
                print(f"DEBUG: Executing tool '{function_name}'")
                if function_name in AVAILABLE_FUNCTIONS:
                    func = AVAILABLE_FUNCTIONS[function_name]
                    try:
                        result = await func(**args) if asyncio.iscoroutinefunction(func) else func(**args)
                    except Exception as e:
                        result = f"Error executing tool: {e}"
                    
                    messages.append({'role': 'tool', 'content': str(result), 'name': function_name})
                else:
                    messages.append({'role': 'tool', 'content': "Error: Tool not found", 'name': function_name})

            # The loop continues, sending tool results back to get the final text answer.
