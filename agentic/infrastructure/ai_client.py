import os
import json
import asyncio
import re
from typing import List, Dict, Any
from ollama import AsyncClient
from dotenv import load_dotenv
from agentic.infrastructure.tools import TOOLS, AVAILABLE_FUNCTIONS

load_dotenv()

class OllamaClient:
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
        self.host = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.client = AsyncClient(host=self.host)

    async def generate_response(self, history: List[Dict[str, str]], message: str) -> str:
        # 1. Strong system instruction for tool-calling reliability
        system_msg = {
            "role": "system", 
            "content": "You are a helpful assistant with access to tools. When you need to do math or check weather, you MUST use your tools. Answer the user directly once you have the results."
        }
        messages = [system_msg] + history + [{"role": "user", "content": message}]
        
        response = await self.client.chat(
            model=self.model,
            messages=messages,
            tools=TOOLS
        )

        # --- Tool Execution Loop ---
        while True:
            # Check for Native Tool Calls
            tool_calls = getattr(response.message, 'tool_calls', [])
            
            # --- Fallback: Check if the model typed JSON into the content field (Common in small models) ---
            if not tool_calls and response.message.content:
                json_match = re.search(r'\{.*"name".*\}', response.message.content, re.DOTALL)
                if json_match:
                    try:
                        potential_tool = json.loads(json_match.group())
                        if "name" in potential_tool:
                            from types import SimpleNamespace
                            # Handle different JSON formats the model might hallucinate
                            args = potential_tool.get("parameters", potential_tool.get("arguments", {}))
                            if isinstance(args, list) and len(args) > 0:
                                args = args[0]
                                
                            fake_tool = SimpleNamespace(
                                function=SimpleNamespace(
                                    name=potential_tool["name"],
                                    arguments=args
                                )
                            )
                            tool_calls = [fake_tool]
                            print(f"DEBUG: Caught hallucinated tool call: {potential_tool['name']}")
                    except: pass

            if not tool_calls:
                break

            # Process Tool Calls
            messages.append(response.message)
            for tool in tool_calls:
                function_name = tool.function.name
                args = tool.function.arguments
                
                # Small models sometimes send arguments as a JSON string
                if isinstance(args, str):
                    try: args = json.loads(args)
                    except: args = {}
                
                print(f"DEBUG: Executing tool '{function_name}' with {args}")

                if function_name in AVAILABLE_FUNCTIONS:
                    func = AVAILABLE_FUNCTIONS[function_name]
                    try:
                        result = await func(**args) if asyncio.iscoroutinefunction(func) else func(**args)
                    except Exception as e:
                        result = f"Error executing tool: {e}"
                    
                    messages.append({'role': 'tool', 'content': str(result), 'name': function_name})
                else:
                    messages.append({'role': 'tool', 'content': "Error: Tool not found", 'name': function_name})

            # Get next response from AI with the results
            response = await self.client.chat(model=self.model, messages=messages, tools=TOOLS)

        return response.message.content
