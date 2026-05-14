import httpx
from typing import Dict, Any, List

# --- Tool Implementations (Python Logic) ---
# We add explicit type casting (float(a)) because small models often send numbers as strings.

async def get_weather(latitude: Any, longitude: Any) -> str:
    """Fetches current weather for coordinates."""
    try:
        lat = float(latitude)
        lon = float(longitude)
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                temp = data['current_weather']['temperature']
                wind = data['current_weather']['windspeed']
                return f"The current temperature at {lat}, {lon} is {temp}°C with wind speeds of {wind} km/h."
    except Exception as e:
        return f"Error fetching weather: {e}"
    return "Error: Could not fetch weather data."

def say_hello(name: str) -> str:
    """Say hello to the user."""
    return f"Hello {name}, welcome to your agentic AI system!"

def add(a: Any, b: Any) -> str:
    """Adds two numbers."""
    try:
        return str(float(a) + float(b))
    except:
        return "Error: Invalid numbers for addition."

def sum_all(numbers: Any) -> str:
    """Sums a list of numbers."""
    try:
        if isinstance(numbers, str):
            import json
            numbers = json.loads(numbers)
        return str(sum([float(n) for n in numbers]))
    except:
        return "Error: Invalid list of numbers."

def multiply_all(numbers: Any) -> str:
    """Multiplies a list of numbers."""
    try:
        if isinstance(numbers, str):
            import json
            numbers = json.loads(numbers)
        if not numbers: return "0"
        result = 1
        for n in numbers: result *= float(n)
        return str(result)
    except:
        return "Error: Invalid list of numbers."

def multiply(a: Any, b: Any) -> str:
    """Multiplies two numbers."""
    try:
        return str(float(a) * float(b))
    except:
        return "Error: Invalid numbers for multiplication."

def division(a: Any, b: Any) -> str:
    """Divides a by b."""
    try:
        val_a = float(a)
        val_b = float(b)
        if val_b == 0: return "Error: Division by zero."
        return str(val_a / val_b)
    except:
        return "Error: Invalid numbers for division."

def subtraction(a: Any, b: Any) -> str:
    """Subtracts b from a."""
    try:
        return str(float(a) - float(b))
    except:
        return "Error: Invalid numbers for subtraction."

# --- Tool Registry ---

AVAILABLE_FUNCTIONS = {
    'get_weather': get_weather,
    'say_hello': say_hello,
    'add': add,
    'sum_all': sum_all,
    'multiply_all': multiply_all,
    'multiply': multiply,
    'division': division,
    'subtraction': subtraction,
}

# --- Tool Definitions (JSON Schemas for Ollama) ---

TOOLS = [
    {
        'type': 'function',
        'function': {
            'name': 'get_weather',
            'description': 'Fetches current weather for coordinates.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'latitude': {'type': 'number'},
                    'longitude': {'type': 'number'},
                },
                'required': ['latitude', 'longitude'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'say_hello',
            'description': 'Say hello to the user.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                },
                'required': ['name'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'add',
            'description': 'Adds two numbers.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'a': {'type': 'number'},
                    'b': {'type': 'number'},
                },
                'required': ['a', 'b'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'sum_all',
            'description': 'Sums a list of numbers.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'numbers': {'type': 'array', 'items': {'type': 'number'}},
                },
                'required': ['numbers'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'multiply_all',
            'description': 'Multiplies a list of numbers.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'numbers': {'type': 'array', 'items': {'type': 'number'}},
                },
                'required': ['numbers'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'multiply',
            'description': 'Multiplies two numbers.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'a': {'type': 'number'},
                    'b': {'type': 'number'},
                },
                'required': ['a', 'b'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'division',
            'description': 'Divides a by b.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'a': {'type': 'number'},
                    'b': {'type': 'number'},
                },
                'required': ['a', 'b'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'subtraction',
            'description': 'Subtracts b from a.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'a': {'type': 'number'},
                    'b': {'type': 'number'},
                },
                'required': ['a', 'b'],
            },
        },
    }
]
