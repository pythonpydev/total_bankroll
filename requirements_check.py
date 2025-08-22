import os
import subprocess
import difflib
import sys

# Configuration
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS_FILE = os.path.join(PROJECT_DIR, "requirements.txt")
TEMP_FILE = os.path.join(PROJECT_DIR, "requirements_temp.txt")
IGNORE_DIRS = "venv,.venv,tests,__pycache__,migrations"
AUTO_INSTALL = True  # Set to False if you don't want to auto-install new packages

def run_pipreqs():
    """Generate a temporary requirements file based on imports using pipreqs."""
    print("🔍 Scanning project for imports with pipreqs...")
    try:
        subprocess.run([
            "pipreqs", PROJECT_DIR,
            "--force", "--ignore", IGNORE_DIRS,
            "--encoding", "utf-8", "--savepath", TEMP_FILE
        ], check=True)
    except FileNotFoundError:
        print("❌ pipreqs not found. Install with: pip install pipreqs")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("❌ pipreqs failed. Check for encoding issues or problematic files.")
        sys.exit(1)

def compare_and_update():
    """Compare old and new requirements, then update if there are changes."""
    if not os.path.exists(REQUIREMENTS_FILE):
        print("📄 No requirements.txt found. Creating a new one...")
        os.rename(TEMP_FILE, REQUIREMENTS_FILE)
        print("✅ Created requirements.txt")
        return True

    with open(REQUIREMENTS_FILE, encoding="utf-8") as old, open(TEMP_FILE, encoding="utf-8") as new:
        old_lines = old.readlines()
        new_lines = new.readlines()

    if old_lines == new_lines:
        print("✅ requirements.txt is already up to date.")
        os.remove(TEMP_FILE)
        return False

    print("⚠️ Detected changes in dependencies:")
    diff = difflib.unified_diff(old_lines, new_lines, fromfile='current', tofile='new')
    for line in diff:
        print(line.strip())

    os.replace(TEMP_FILE, REQUIREMENTS_FILE)
    print("✅ requirements.txt updated with latest dependencies.")
    return True

def install_missing():
    """Install missing packages from the updated requirements.txt."""
    print("📦 Installing/Updating packages from requirements.txt...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE], check=True)
        print("✅ All packages are up to date.")
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages. Check your environment or permissions.")

if __name__ == "__main__":
    run_pipreqs()
    updated = compare_and_update()
    if updated and AUTO_INSTALL:
        install_missing()
