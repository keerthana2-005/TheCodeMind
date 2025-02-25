import json
import google.generativeai as genai
from config.config_reader import read_config  # Assuming you have a config reader

def analyze_with_gemini(ast_json, api_key=None):
    """Sends AST JSON to Gemini AI for logical error detection and returns a one-line error message."""

    # Read API key from config if not provided
    if not api_key:
        try:
            config = read_config()
            api_key = config.get('gemini', {}).get('api_key')
            if not api_key:
                raise ValueError("GEMINI_API_KEY is missing in config. Please check your configuration.")
        except Exception as e:
            return f"Error: Failed to read API key - {str(e)}"

    # Configure Gemini AI
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        return f"Error: Failed to configure Gemini API - {str(e)}"

    # Model generation settings
    generation_config = {
        "temperature": 0,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    # Define model with optimized system instructions
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction=(
            "You are a highly accurate Python bug detection AI. Your task is to analyze Abstract Syntax Tree (AST) JSON and "
            "detect only logical errors with precision.\n\n"

            "### 🔹 **Rules:**\n"
            "- Return **one-line error message** (no explanations, no extra details).\n"
            "- **Specify the exact issue & location** (function name, line number).\n"
            "- **Avoid redundant or vague errors** (e.g., do not flag function parameters as undefined variables).\n"
            "- **Do not return multiple errors; prioritize the most critical one.**\n\n"

            "### 🔹 **Detect & Report:**\n"
            "✅ **Infinite loops** (missing decrement, incorrect loop conditions).\n"
            "✅ **Undefined variables** (usage before assignment, non-existent references).\n"
            "✅ **Incorrect conditionals** (always-true/false branches, unreachable paths).\n"
            "✅ **Unreachable code** (dead code after return, break, continue).\n"
            "✅ **Division errors**:\n"
            "   - **Division by zero** (unchecked divisor).\n"
            "   - **Invalid division** (attempt to divide by non-numeric types like lists, strings).\n"
            "✅ **Faulty loops/functions** (incorrect iteration, list mutations, misplaced returns).\n"
            "✅ **Type mismatches** (operations between incompatible types, e.g., adding an int to a string).\n"
            "✅ **Function misuse** (wrong number/type of arguments in function calls).\n\n"

            "### 🔹 **Error Message Format:**\n"
            "✅ \"Error: Infinite loop in 'count_down' at line X - missing decrement on 'n'.\"\n"
            "✅ \"Error: Undefined variable 'x' in 'process_data' at line X.\"\n"
            "✅ \"Error: Division by zero in 'calculate' at line X - divisor is unchecked.\"\n"
            "✅ \"Error: Invalid division in 'compute' at line X - divisor is a list.\"\n"
            "✅ \"Error: Type mismatch in 'add_numbers' at line X - cannot add int and str.\"\n"
            "✅ \"Error: Function 'process_data' at line X expects 2 arguments but got 3.\"\n\n"

            "🚀 **Your goal: Deliver precise, structured, and instantly actionable one-line error messages.**"
        ),
    )

    # Structured prompt
    structured_prompt = {
        "task": "Analyze this AST JSON for logical errors and return a single-line error message.",
        "rules": [
            "Return only a single-line error message with issue & location.",
            "Do not provide explanations, suggestions, or multiple errors.",
            "Maintain precision and professionalism."
        ],
        "input_AST": ast_json  # AST JSON input
    }

    # Start a chat session
    try:
        chat_session = model.start_chat()
        response = chat_session.send_message(json.dumps(structured_prompt))
        return response.text.strip() if response and response.text else "Error: No response from Gemini."
    except Exception as e:
        return f"Error: Failed to process AST - {str(e)}"
