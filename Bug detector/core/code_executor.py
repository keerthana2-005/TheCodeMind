import sys
import traceback
from io import StringIO

def execute_code(code):
    """
    Executes the given Python code and captures both standard output and error messages.
    Returns:
        - A tuple containing (output, errors) as strings.
    """
    output_stream = StringIO()  # Capture standard output
    error_stream = StringIO()  # Capture error messages
    
    try:
        # Redirect stdout and stderr to capture execution output and errors
        sys.stdout = output_stream
        sys.stderr = error_stream

        exec(code, {})  # Execute the provided code in an isolated namespace

    except Exception as e:
        # Capture runtime errors and store traceback details
        error_stream.write(f"Runtime error: {e}\n")
        error_stream.write(traceback.format_exc())

    finally:
        # Restore original stdout and stderr to prevent unintended redirection
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    # Return captured output and errors as stripped strings
    return output_stream.getvalue().strip(), error_stream.getvalue().strip()
