import os
import asyncio
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment variables.")
    client = None
else:
    client = genai.Client(api_key=api_key)

HISTORY_FILE = "chat_history.json"

def save_history(history):
    """Saves the chat history to a JSON file."""
    with open(HISTORY_FILE, "w") as f:
        # Convert history objects to dictionaries for JSON serialization
        json_history = [content.model_dump(exclude_none=True) for content in history]
        json.dump(json_history, f, indent=4)

def load_history():
    """Loads the chat history from a JSON file."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                json_history = json.load(f)
                return [types.Content(**content) for content in json_history]
        except Exception as e:
            print(f"Warning: Could not load history: {e}")
    return []

def say_hello(name: str) -> str:
    """Say hello to the user.

    Args:
        name: The name of the person to greet.
    """
    return f"Hello {name}, welcome to the new Gemini AI SDK!"

def add(a: float, b: float) -> float:
    """Adds two numbers together.

    Args:
        a: The first number.
        b: The second number.
    """
    return a + b

def sum_all(numbers: list[float]) -> float:
    """Adds a list of multiple numbers together.

    Args:
        numbers: A list of numbers to sum up.
    """
    return sum(numbers)

def multiply_all(numbers: list[float]) -> float:
    """Multiplies a list of multiple numbers together.

    Args:
        numbers: A list of numbers to multiply.
    """
    if not numbers:
        return 0
    result = 1
    for n in numbers:
        result *= n
    return result

def multiply(a: float, b: float) -> float:
    """Multiplies two numbers together.

    Args:
        a: The first number.
        b: The second number.
    """
    return a * b

def division(a: float, b: float) -> float:
    """Divides the first number by the second.

    Args:
        a: The numerator.
        b: The denominator.
    """
    if b == 0:
        return "Error: Division by zero is not allowed."
    return a / b

def subtraction(a: float, b: float) -> float:
    """Subtracts the second number from the first.

    Args:
        a: The first number.
        b: The second number to subtract.
    """
    return a - b

# RUNNER
async def main():
    if not client:
        return

    
    history = load_history()
    if history:
        print(f"--- Loaded {len(history)} messages from history ---")

    chat = client.aio.chats.create(
        model='gemini-2.0-flash', 
        history=history,
        config=types.GenerateContentConfig(
            tools=[say_hello, add, multiply, division, subtraction, sum_all, multiply_all],
            system_instruction="You are a friendly AI agent. Use the available tools when necessary."
        )
    )

    print("--- Gemini Agent Active ---")
    print("Type 'exit' or 'quit' to stop.")

    while True:
        try:
            user_input = input("\nYou: ")
            
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            if not user_input.strip():
                continue

            response = await chat.send_message(user_input)
            
            print(f"\nGemini: {response.text}")

            save_history(chat.history)

        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
