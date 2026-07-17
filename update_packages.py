#!/usr/bin/env python
"""
Script to update packages to fix Pydantic compatibility with Python 3.12
"""
import subprocess
import sys

def update_packages():
    """Update packages to fix Pydantic compatibility with Python 3.12"""
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    try:
        # Install the latest version of Pydantic
        print("Installing Pydantic 2.5.0+...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", 
            "pydantic>=2.5.0", "pydantic-core>=2.14.0"
        ])
        
        # Check the installed version
        print("\nChecking installed Pydantic version:")
        subprocess.check_call([
            sys.executable, "-m", "pip", "show", "pydantic"
        ])
        
        print("\nChecking installed Pydantic-core version:")
        subprocess.check_call([
            sys.executable, "-m", "pip", "show", "pydantic-core"
        ])
        
        print("\nPackages updated successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error updating packages: {e}")
        return False
    
    return True

if __name__ == "__main__":
    update_packages()
