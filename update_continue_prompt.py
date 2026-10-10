#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
from datetime import datetime

# Path to the Continue config on Linux/Fedora
config_path = os.path.expanduser("~/.continue/config.yaml")
venv_dir = "/tmp/continue_yaml_venv"

print("============================================================")
print("Updating Continue YAML Configuration")
print("============================================================")

if not os.path.exists(config_path):
    print(f"❌ Error: Could not find Continue config at {config_path}")
    sys.exit(1)

# 1. Create a safe backup with a timestamp
backup_path = f"{config_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(config_path, backup_path)
print(f"✅ Backed up current config to: {backup_path}")

# 2. Create a temporary virtual environment for safe YAML editing
print("📦 Setting up isolated environment for safe YAML editing...")
subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)

pip_path = os.path.join(venv_dir, "bin", "pip")
python_venv_path = os.path.join(venv_dir, "bin", "python")

# Install the ruamel.yaml parser
subprocess.run([pip_path, "install", "--quiet", "ruamel.yaml"], check=True)

# 3. Create the injection script to run inside the virtual environment
inner_script = """
import os
from ruamel.yaml import YAML

config_path = os.path.expanduser("~/.continue/config.yaml")

# Initialize YAML parser configured to preserve comments and quotes
yaml = YAML()
yaml.preserve_quotes = True

with open(config_path, 'r') as f:
    config = yaml.load(f)

# The strict directive to force full-file outputs
prompt_addition = (
    "\\n\\nCRITICAL DIRECTIVE FOR FILE EDITS:\\n"
    "Never use find-and-replace or diff-based tools for modifying files. "
    "When asked to edit, refactor, or update code, you MUST output the completely rewritten, "
    "full file from the very first line to the very last line in a single code block. "
    "Do not use placeholders, do not truncate, and do not skip any sections."
)

current_message = config.get("systemMessage", "")

if "CRITICAL DIRECTIVE FOR FILE EDITS" in current_message:
    print("✅ The directive is already present in your systemMessage. No changes made.")
else:
    config["systemMessage"] = current_message + prompt_addition
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    print("✅ Successfully updated systemMessage in ~/.continue/config.yaml")
"""

script_path = "/tmp/update_yaml_inner.py"
with open(script_path, "w") as f:
    f.write(inner_script)

# 4. Execute the injection script
subprocess.run([python_venv_path, script_path], check=True)

# 5. Clean up
print("🧹 Cleaning up...")
shutil.rmtree(venv_dir)
os.remove(script_path)

print("\\n🔄 Important: Restart VSCode or use the 'Developer: Reload Window' command to apply changes.")
