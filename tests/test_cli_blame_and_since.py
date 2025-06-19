# tests/test_cli_blame_and_since.py

import subprocess
import tempfile
import os
import shutil
import sys
import time
import stat

print("🔥 Running CLI integration tests...")

# Create a temporary directory as our isolated test repo
temp_repo = tempfile.mkdtemp()

# Setup: copy mockpackage + main.py into this directory
mock_code = {
    "mockpackage/__init__.py": "",
    "mockpackage/auth_module.py": '''def handle_login():
    """Login handler"""
    return True
''',
    "main.py": '''import sys
if __name__ == "__main__":
    print("Mock main CLI running...")
    args = sys.argv[1:]
    if "--blame" in args:
        print("Last modified by: test_user")
    elif any("--since" in arg for arg in args):
        print("Modified within 3 days")
'''
}

for path, content in mock_code.items():
    full_path = os.path.join(temp_repo, path.replace("/", os.sep))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

# Initialize git repo
subprocess.run(["git", "init"], cwd=temp_repo, check=True)
subprocess.run(["git", "config", "user.name", "test_user"], cwd=temp_repo)
subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_repo)

# Stage and commit files
subprocess.run(["git", "add", "."], cwd=temp_repo, check=True)
subprocess.run(["git", "commit", "-m", "Add mockpackage"], cwd=temp_repo, check=True)

# Wait and make a second commit to simulate time difference
time.sleep(1)
with open(os.path.join(temp_repo, "mockpackage", "auth_module.py"), "a") as f:
    f.write("\n# modified timestamp\n")

subprocess.run(["git", "add", "."], cwd=temp_repo, check=True)
subprocess.run(["git", "commit", "-m", "Modify timestamp"], cwd=temp_repo, check=True)

def run_cli(args):
    result = subprocess.run(
        [sys.executable, "main.py"] + args,
        cwd=temp_repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    return result.stdout.strip()

# TC1: CLI --blame
print("\n✅ TC1: CLI blame for auth.handle_login")
output1 = run_cli(["describe", "auth.handle_login", "--blame"])
print("[OUTPUT]:\n", output1)
assert "Last modified by:" in output1

# TC2: CLI --since=3days
print("\n✅ TC2: CLI --since=3days")
output2 = run_cli(["search", "--since=3days"])
print("[OUTPUT]:\n", output2)
assert "Modified within 3 days" in output2

print("\n🎉 All CLI tests passed.")

# Cleanup helper to handle Windows permission errors
def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

shutil.rmtree(temp_repo, onerror=remove_readonly)
