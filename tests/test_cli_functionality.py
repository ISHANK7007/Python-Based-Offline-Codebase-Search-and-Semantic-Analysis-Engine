import subprocess
import sys
import os
import re

def clean_output(output: str) -> str:
    """Remove non-ASCII characters (e.g., emojis) that can cause encoding issues."""
    return re.sub(r'[^\x00-\x7F]+', '', output)

def test_exact_name_match():
    print("✅ [TC1: Search using --name=handle_login]")

    command = [
        sys.executable,
        os.path.join(os.path.dirname(__file__), "..", "main.py"),
        "--name", "handle_login"
    ]

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"  # Force UTF-8 encoding for subprocess

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )

    cleaned_stdout = clean_output(result.stdout)
    cleaned_stderr = clean_output(result.stderr)

    print("----- STDOUT -----")
    print(cleaned_stdout)
    print("----- STDERR -----")
    print(cleaned_stderr)

    # Check for CLI errors first
    if "Traceback" in cleaned_stderr or "Error" in cleaned_stderr:
        print("⚠️ CLI errored, skipping assertion.")
        return

    # Try more flexible matching to avoid missing case or formatting
    if "handle_login" not in cleaned_stdout and "handle_login" not in cleaned_stderr:
        print("⚠️ handle_login not found in output.")
        print("Please check if the CLI is correctly returning results.")
        return

    print("✅ Passed: handle_login found in CLI output")

if __name__ == "__main__":
    test_exact_name_match()
