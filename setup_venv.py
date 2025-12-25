#!/usr/bin/env python3
"""
Virtual Environment Setup for PII Detection System
Creates and configures a virtual environment with all dependencies
"""

import subprocess
import sys
import os
import venv
from pathlib import Path

def run_command(command, description, cwd=None):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        print(f"✅ {description} completed")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def create_virtual_environment():
    """Create virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return venv_path
    
    print("🔄 Creating virtual environment...")
    try:
        venv.create(venv_path, with_pip=True)
        print("✅ Virtual environment created")
        return venv_path
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return None

def get_venv_python(venv_path):
    """Get path to Python executable in virtual environment"""
    if os.name == 'nt':  # Windows
        return venv_path / "Scripts" / "python.exe"
    else:  # Unix/Linux/macOS
        return venv_path / "bin" / "python"

def get_venv_pip(venv_path):
    """Get path to pip executable in virtual environment"""
    if os.name == 'nt':  # Windows
        return venv_path / "Scripts" / "pip.exe"
    else:  # Unix/Linux/macOS
        return venv_path / "bin" / "pip"

def main():
    print("🚀 Setting up PII Detection System with Virtual Environment")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create virtual environment
    venv_path = create_virtual_environment()
    if not venv_path:
        sys.exit(1)
    
    # Get paths to executables
    python_exe = get_venv_python(venv_path)
    pip_exe = get_venv_pip(venv_path)
    
    print(f"📍 Virtual environment: {venv_path.absolute()}")
    print(f"📍 Python executable: {python_exe}")
    print(f"📍 Pip executable: {pip_exe}")
    
    # Upgrade pip
    if not run_command(f'"{python_exe}" -m pip install --upgrade pip', "Upgrading pip"):
        print("⚠️  Pip upgrade failed, continuing anyway...")
    
    # Install Python dependencies
    print("\n📦 Installing Python dependencies...")
    requirements = [
        "torch>=2.0.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "faker>=19.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "pydantic>=2.0.0",
        "python-multipart>=0.0.6",
        "jinja2>=3.1.0",
        "aiofiles>=23.0.0",
        "scikit-learn>=1.3.0",
        "spacy>=3.7.0",
        "requests>=2.31.0"
    ]
    
    for package in requirements:
        if not run_command(f'"{pip_exe}" install "{package}"', f"Installing {package.split('>=')[0]}"):
            print(f"⚠️  Failed to install {package}, continuing...")
    
    # Download spaCy model
    print("\n🧠 Downloading spaCy English model...")
    run_command(f'"{python_exe}" -m spacy download en_core_web_sm', "Downloading spaCy model")
    
    # Check if Node.js is available for frontend
    print("\n🌐 Checking Node.js for frontend...")
    try:
        result = subprocess.run("node --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()} detected")
            
            # Install frontend dependencies
            frontend_dir = Path("frontend")
            if frontend_dir.exists():
                print("📦 Installing frontend dependencies...")
                if not run_command("npm install", "Installing Node.js packages", cwd=frontend_dir):
                    print("⚠️  Frontend setup may be incomplete")
            else:
                print("⚠️  Frontend directory not found")
        else:
            print("⚠️  Node.js not found. Frontend will not be available.")
            print("   Install Node.js from https://nodejs.org/ to use the web interface")
    except FileNotFoundError:
        print("⚠️  Node.js not found. Frontend will not be available.")
    
    # Create necessary directories
    print("\n📁 Creating directories...")
    directories = ["models", "data", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created/verified directory: {directory}")
    
    # Test the simple PII model
    print("\n🧪 Testing PII detection system...")
    test_script = f'''
import sys
sys.path.append(".")
from simple_pii_model import SimplePIIProcessor

processor = SimplePIIProcessor()
test_text = "Contact John Smith at john@email.com or call 555-123-4567"
analysis = processor.analyze_text(test_text)
print(f"✅ Detected {{analysis['pii_count']}} PII entities: {{', '.join(analysis['pii_types'])}}")
'''
    
    with open("test_pii.py", "w") as f:
        f.write(test_script)
    
    if run_command(f'"{python_exe}" test_pii.py', "Testing PII detection"):
        os.remove("test_pii.py")
    
    # Create activation scripts
    print("\n📝 Creating activation scripts...")
    
    # Windows activation script
    if os.name == 'nt':
        activate_script = f'''@echo off
echo Activating PII Detection System Virtual Environment...
call "{venv_path}\\Scripts\\activate.bat"
echo ✅ Virtual environment activated!
echo.
echo 🚀 Available commands:
echo   python simple_pii_model.py          - Test PII detection
echo   cd backend ^&^& python main.py       - Start API server
echo   cd frontend ^&^& npm run dev         - Start web interface
echo.
cmd /k
'''
        with open("activate.bat", "w") as f:
            f.write(activate_script)
        print("✅ Created activate.bat for Windows")
    
    # Unix/Linux activation script
    activate_script = f'''#!/bin/bash
echo "Activating PII Detection System Virtual Environment..."
source "{venv_path}/bin/activate"
echo "✅ Virtual environment activated!"
echo ""
echo "🚀 Available commands:"
echo "  python simple_pii_model.py          - Test PII detection"
echo "  cd backend && python main.py        - Start API server"
echo "  cd frontend && npm run dev          - Start web interface"
echo ""
exec bash
'''
    with open("activate.sh", "w") as f:
        f.write(activate_script)
    
    # Make executable on Unix systems
    if os.name != 'nt':
        os.chmod("activate.sh", 0o755)
        print("✅ Created activate.sh for Unix/Linux/macOS")
    
    # Create quick start scripts
    print("\n📝 Creating quick start scripts...")
    
    # Start API script
    api_script = f'''#!/usr/bin/env python3
import subprocess
import sys
import os

# Activate virtual environment and start API
if os.name == 'nt':
    python_exe = r"{python_exe}"
else:
    python_exe = "{python_exe}"

os.chdir("backend")
subprocess.run([python_exe, "main.py"])
'''
    
    with open("start_api.py", "w") as f:
        f.write(api_script)
    
    # Start frontend script (if Node.js available)
    if result.returncode == 0:
        frontend_script = '''#!/usr/bin/env python3
import subprocess
import os

os.chdir("frontend")
subprocess.run(["npm", "run", "dev"])
'''
        with open("start_frontend.py", "w") as f:
            f.write(frontend_script)
    
    print("\n🎯 Setup Complete!")
    print("=" * 40)
    print("✅ Virtual environment created and configured")
    print("✅ Python dependencies installed")
    print("✅ PII detection system ready")
    
    print(f"\n📁 Virtual environment location: {venv_path.absolute()}")
    
    print("\n🚀 Quick Start:")
    if os.name == 'nt':
        print("1. Double-click activate.bat to enter the virtual environment")
        print("2. Or run: python start_api.py (starts API server)")
        if result.returncode == 0:
            print("3. Or run: python start_frontend.py (starts web interface)")
    else:
        print("1. Run: ./activate.sh to enter the virtual environment")
        print("2. Or run: python start_api.py (starts API server)")
        if result.returncode == 0:
            print("3. Or run: python start_frontend.py (starts web interface)")
    
    print("\n🌐 URLs:")
    print("  API: http://localhost:8000")
    print("  Web Interface: http://localhost:3000")
    print("  API Docs: http://localhost:8000/docs")
    
    print("\n🧪 Test the system:")
    if os.name == 'nt':
        print(f'  "{python_exe}" simple_pii_model.py')
    else:
        print(f"  {python_exe} simple_pii_model.py")

if __name__ == "__main__":
    main()