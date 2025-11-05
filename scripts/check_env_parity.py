#!/usr/bin/env python3
"""
Environment Parity Check Script for StakeEasy.net

Verifies that the development environment matches production requirements
to prevent deployment issues.

Usage:
    python scripts/check_env_parity.py
    
Exit Codes:
    0 - All checks passed
    1 - One or more checks failed
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class ParityChecker:
    """Checks development/production environment parity."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0
        
    def print_header(self, text: str):
        """Print a section header."""
        print(f"\n{BLUE}{'=' * 60}{RESET}")
        print(f"{BLUE}{text}{RESET}")
        print(f"{BLUE}{'=' * 60}{RESET}")
        
    def print_check(self, name: str, passed: bool, details: str = ""):
        """Print check result."""
        status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
        print(f"{status} - {name}")
        if details:
            print(f"       {details}")
        
        if passed:
            self.checks_passed += 1
        else:
            self.checks_failed += 1
            
    def print_warning(self, message: str):
        """Print a warning message."""
        print(f"{YELLOW}⚠ WARNING{RESET} - {message}")
        self.warnings += 1
        
    def check_python_version(self) -> bool:
        """Check Python version is documented and appropriate."""
        self.print_header("Python Version Check")
        
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        print(f"Current Python version: {current_version}")
        
        # Check if .python-version file exists
        python_version_file = self.project_root / ".python-version"
        if python_version_file.exists():
            documented_version = python_version_file.read_text().strip()
            matches = documented_version.startswith(f"{sys.version_info.major}.{sys.version_info.minor}")
            self.print_check(
                ".python-version file exists and matches",
                matches,
                f"Documented: {documented_version}, Current: {current_version}"
            )
            return matches
        else:
            self.print_check(
                ".python-version file exists",
                False,
                "File not found. Run TASK-0005 to create it."
            )
            return False
            
    def check_required_env_vars(self) -> bool:
        """Check that all required environment variables are set."""
        self.print_header("Environment Variables Check")
        
        required_vars = [
            "SECRET_KEY",
            "FLASK_ENV",
            "EXCHANGE_RATE_API_KEY",
            "SECURITY_PASSWORD_SALT",
        ]
        
        # Check if running in development or production context
        flask_env = os.getenv("FLASK_ENV", "development")
        print(f"Current environment: {flask_env}")
        
        if flask_env == "development":
            required_vars.extend([
                "DEV_DB_HOST",
                "DEV_DB_NAME",
                "DEV_DB_USER",
                "DEV_DB_PASS",
            ])
        else:
            required_vars.extend([
                "DB_HOST_PROD",
                "DB_NAME_PROD",
                "DB_USER_PROD",
                "DB_PASS_PROD",
            ])
        
        all_present = True
        for var in required_vars:
            value = os.getenv(var)
            is_set = value is not None and value != ""
            self.print_check(
                f"Environment variable: {var}",
                is_set,
                "Not set" if not is_set else "Set"
            )
            if not is_set:
                all_present = False
                
        return all_present
        
    def check_uncommitted_migrations(self) -> bool:
        """Check for uncommitted migration files."""
        self.print_header("Database Migrations Check")
        
        migrations_dir = self.project_root / "migrations" / "versions"
        
        if not migrations_dir.exists():
            self.print_warning("Migrations directory not found")
            return True
            
        try:
            # Check git status for migrations directory
            result = subprocess.run(
                ["git", "status", "--porcelain", str(migrations_dir)],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            uncommitted = result.stdout.strip()
            if uncommitted:
                files = [line.split()[-1] for line in uncommitted.split('\n')]
                self.print_check(
                    "No uncommitted migrations",
                    False,
                    f"Uncommitted: {', '.join(files)}"
                )
                return False
            else:
                self.print_check("No uncommitted migrations", True)
                return True
                
        except subprocess.CalledProcessError as e:
            self.print_warning(f"Could not check git status: {e}")
            return True
            
    def check_static_assets(self) -> bool:
        """Check that static assets are built and present."""
        self.print_header("Static Assets Check")
        
        static_dir = self.project_root / "src" / "total_bankroll" / "static"
        
        if not static_dir.exists():
            self.print_check(
                "Static directory exists",
                False,
                f"Not found: {static_dir}"
            )
            return False
            
        # Check for key static directories
        checks = []
        
        css_dir = static_dir / "css"
        checks.append(("CSS directory exists", css_dir.exists()))
        
        js_dir = static_dir / "js"
        checks.append(("JavaScript directory exists", js_dir.exists()))
        
        images_dir = static_dir / "images"
        checks.append(("Images directory exists", images_dir.exists()))
        
        # Check if Vite build assets exist (if using Vite)
        vite_config = self.project_root / "vite.config.js"
        if vite_config.exists():
            assets_dir = static_dir / "assets"
            if assets_dir.exists():
                manifest = assets_dir / ".vite" / "manifest.json"
                checks.append(("Vite assets built", manifest.exists()))
            else:
                self.print_warning("Vite config exists but no assets directory. Run 'npm run build' if needed.")
        
        all_passed = True
        for check_name, passed in checks:
            self.print_check(check_name, passed)
            if not passed:
                all_passed = False
                
        return all_passed
        
    def check_dependencies(self) -> bool:
        """Check that dependencies are properly documented."""
        self.print_header("Dependencies Check")
        
        requirements_in = self.project_root / "requirements.in"
        requirements_txt = self.project_root / "requirements.txt"
        
        checks = []
        
        checks.append((
            "requirements.in exists",
            requirements_in.exists(),
            "Source dependency file"
        ))
        
        checks.append((
            "requirements.txt exists",
            requirements_txt.exists(),
            "Compiled dependency file"
        ))
        
        # Check if requirements.txt is newer than requirements.in
        if requirements_in.exists() and requirements_txt.exists():
            in_mtime = requirements_in.stat().st_mtime
            txt_mtime = requirements_txt.stat().st_mtime
            is_current = txt_mtime >= in_mtime
            checks.append((
                "requirements.txt is up to date",
                is_current,
                "Run 'pip-compile requirements.in' if not current"
            ))
        
        all_passed = True
        for check_name, passed, *details in checks:
            detail = details[0] if details else ""
            self.print_check(check_name, passed, detail)
            if not passed:
                all_passed = False
                
        return all_passed
        
    def check_flask_app_config(self) -> bool:
        """Check Flask app configuration."""
        self.print_header("Flask Configuration Check")
        
        flask_app = os.getenv("FLASK_APP")
        flask_env = os.getenv("FLASK_ENV", "production")
        
        checks = []
        
        checks.append((
            "FLASK_APP is set",
            flask_app is not None,
            f"Current: {flask_app}"
        ))
        
        checks.append((
            "FLASK_ENV is set",
            flask_env in ["development", "production"],
            f"Current: {flask_env}"
        ))
        
        # Warn if in production mode but certain dev features are enabled
        if flask_env == "production":
            debug_mode = os.getenv("FLASK_DEBUG", "0")
            if debug_mode == "1":
                self.print_warning("FLASK_DEBUG is enabled in production mode")
        
        all_passed = True
        for check_name, passed, *details in checks:
            detail = details[0] if details else ""
            self.print_check(check_name, passed, detail)
            if not passed:
                all_passed = False
                
        return all_passed
        
    def run_all_checks(self) -> bool:
        """Run all parity checks."""
        print(f"\n{BLUE}╔═══════════════════════════════════════════════════════════╗{RESET}")
        print(f"{BLUE}║  StakeEasy.net Environment Parity Check                   ║{RESET}")
        print(f"{BLUE}╚═══════════════════════════════════════════════════════════╝{RESET}")
        
        # Run all checks
        self.check_python_version()
        self.check_required_env_vars()
        self.check_flask_app_config()
        self.check_dependencies()
        self.check_uncommitted_migrations()
        self.check_static_assets()
        
        # Print summary
        self.print_header("Summary")
        print(f"Checks passed: {GREEN}{self.checks_passed}{RESET}")
        print(f"Checks failed: {RED}{self.checks_failed}{RESET}")
        print(f"Warnings:      {YELLOW}{self.warnings}{RESET}")
        
        if self.checks_failed == 0:
            print(f"\n{GREEN}✓ All checks passed! Environment is ready for deployment.{RESET}\n")
            return True
        else:
            print(f"\n{RED}✗ Some checks failed. Please address issues before deploying.{RESET}\n")
            return False


def main():
    """Main entry point."""
    # Load .env file if python-dotenv is available
    try:
        from dotenv import load_dotenv
        project_root = Path(__file__).parent.parent
        load_dotenv(project_root / ".env")
    except ImportError:
        print(f"{YELLOW}Warning: python-dotenv not installed. Environment variables may not be loaded.{RESET}")
    
    checker = ParityChecker()
    success = checker.run_all_checks()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
