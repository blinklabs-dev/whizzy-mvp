#!/usr/bin/env python3
"""
Setup script for Text2SOQL MVP
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command)
    
    return result


def setup_environment():
    """Setup the development environment."""
    print("🚀 Setting up Text2SOQL MVP environment...")
    
    # Check if Python 3.11+ is available
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create virtual environment if it doesn't exist
    venv_path = Path("venv")
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        run_command("python -m venv venv")
    
    # Determine activation command based on OS
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Install dependencies
    print("📦 Installing dependencies...")
    run_command(f"{pip_cmd} install --upgrade pip")
    run_command(f"{pip_cmd} install -e .")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        run_command(f"cp env.example .env")
        print("⚠️  Please edit .env file with your Salesforce credentials")
    
    print("✅ Environment setup complete!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your Salesforce credentials")
    print("2. Test the MCP server: python -m mcp_server.main")
    print("3. Add the MCP configuration to Cursor")
    print("4. Try querying Salesforce from Cursor Chat!")


def test_mcp_server():
    """Test the MCP server."""
    print("🧪 Testing MCP server...")
    
    try:
        # This is a basic test - in a real scenario you'd want more comprehensive testing
        result = run_command("python -c \"import mcp_server.main; print('✅ MCP server imports successfully')\"")
        print("✅ MCP server test passed")
    except subprocess.CalledProcessError:
        print("❌ MCP server test failed")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_mcp_server()
    else:
        setup_environment()
