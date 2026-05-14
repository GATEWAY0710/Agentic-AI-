from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
import asyncio

load_dotenv()

@function_tool
def say_hello(name: str) -> str:
    """Say hello to the user."""
    return f"Hello {name}, welcome to Agentic AI!"

@function_tool
def add(a: float, b: float) -> float:
    """Adds two numbers together."""
    return a + b

@function_tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers together."""
    return a * b


agent = Agent(
    name="HelloAgent",
    instructions="""
    You are a friendly AI agent.
    Use the available tools when necessary.
    """,
    tools=[say_hello, add, multiply]
)



async def main():
    print("--- OpenAI Agent Active ---")
    print("Type 'exit' or 'quit' to stop.")
    
    current_agent = agent
    input_items = []

    while True:
        try:
            user_input = input("\nYou: ")
            
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            if not user_input.strip():
                continue

            input_items.append({"role": "user", "content": user_input})

            result = await Runner.run(
                current_agent,
                input=input_items
            )

            if result.final_output is not None:
                print(f"\nAgent: {result.final_output}")

            current_agent = result.last_agent
            input_items = result.to_input_list()

        except Exception as e:
            print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")