import subprocess
import sys
import tempfile
import os

def run_python(code: str) -> str:
    """
    Execute Python code safely in a subprocess.
    Returns stdout + stderr output.
    """
    try:
        # Write code to a temp file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            f.write(code)
            temp_path = f.name

        # Run with timeout
        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        output = ""
        if result.stdout:
            output += f"Output:\n{result.stdout}"
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"

        if not output:
            output = "Code ran successfully with no output"

        if len(output) > 2000:
            output = output[:2000] + "\n\n[Output truncated...]"

        return output

    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out (10 seconds)"
    except Exception as e:
        return f"Error running code: {str(e)}"
    finally:
        # Clean up temp file
        if 'temp_path' in locals():
            os.unlink(temp_path)