import subprocess
import sys
import re

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing command: {command}")
        print(f"Error output: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def setup_poetry_dynamic_versioning():
    print("Setting up poetry-dynamic-versioning...")
    run_command("poetry self add \"poetry-dynamic-versioning[plugin]\"")
    
    # Update pyproject.toml
    with open("pyproject.toml", "r") as f:
        content = f.read()
    
    if "[tool.poetry-dynamic-versioning]" not in content:
        content += "\n[tool.poetry-dynamic-versioning]\nenable = true\nvcs = \"git\"\nstyle = \"semver\"\n"
    
    if "poetry-dynamic-versioning" not in content:
        content = re.sub(
            r'\[build-system\]\nrequires = \[(.*?)\]',
            '[build-system]\nrequires = [\\1, "poetry-dynamic-versioning"]',
            content,
            flags=re.DOTALL
        )
        content = content.replace(
            'build-backend = "poetry.core.masonry.api"',
            'build-backend = "poetry_dynamic_versioning.backend"'
        )
    
    with open("pyproject.toml", "w") as f:
        f.write(content)
    
    print("poetry-dynamic-versioning setup complete.")

def get_latest_tag():
    return run_command("git describe --tags --abbrev=0")

def build_and_publish():
    print("Building package...")
    run_command("poetry build")
    
    print("Publishing package...")
    run_command("poetry publish")
    
    print("Package published successfully.")

def main():
    setup_poetry_dynamic_versioning()
    
    latest_tag = get_latest_tag()
    print(f"Latest tag: {latest_tag}")
    
    # Check if we're on the tagged commit
    current_commit = run_command("git rev-parse HEAD")
    tag_commit = run_command(f"git rev-list -n 1 {latest_tag}")
    
    if current_commit == tag_commit:
        print("On tagged commit. Proceeding with build and publish.")
        build_and_publish()
    else:
        print("Not on a tagged commit. Skipping publish.")
        sys.exit(0)

if __name__ == "__main__":
    main()