#!/usr/bin/env python3
"""
Local build testing script for PicSpider
This script mimics what the GitHub Actions workflow does locally
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        print(f"✓ Command succeeded: {cmd}")
        if result.stdout:
            print(f"  Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Command failed: {cmd}")
        print(f"  Error: {e.stderr.strip()}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version < (3, 7):
        print(f"✗ Python {version.major}.{version.minor} is too old. Need Python 3.7+")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_dependencies():
    """Check if all dependencies can be imported"""
    dependencies = [
        'tkinter',
        'flask', 
        'requests',
        'bs4',  # beautifulsoup4
        'PyInstaller'
    ]
    
    failed = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep} is available")
        except ImportError:
            print(f"✗ {dep} is missing")
            failed.append(dep)
    
    return len(failed) == 0

def test_module_imports():
    """Test importing main application modules"""
    modules = ['gui', 'config', 'main']
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}.py imports successfully")
        except ImportError as e:
            print(f"⚠ {module}.py import failed: {e}")
        except Exception as e:
            print(f"⚠ {module}.py has issues: {e}")

def create_spec_file():
    """Create PyInstaller spec file"""
    platform_name = platform.system().lower()
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('config.json', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.scrolledtext',
        'flask',
        'requests',
        'beautifulsoup4',
        'concurrent.futures',
        'threading',
        'webbrowser',
        'json',
        'pathlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PicSpider',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)'''

    if platform_name == 'darwin':
        spec_content += '''

app = BUNDLE(
    exe,
    name='PicSpider.app',
    icon=None,
    bundle_identifier='com.picspider.app',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'NSRequiresAquaSystemAppearance': 'False',
    },
)'''

    with open('PicSpider.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✓ PyInstaller spec file created")
    return True

def test_build():
    """Test PyInstaller build"""
    print("Testing PyInstaller build...")
    return run_command("python -m PyInstaller PicSpider.spec --clean --noconfirm")

def verify_build():
    """Verify the build output"""
    platform_name = platform.system().lower()
    
    if platform_name == 'windows':
        exe_path = Path('dist/PicSpider.exe')
        if exe_path.exists():
            print(f"✓ Windows executable created: {exe_path}")
            print(f"  Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
            return True
        else:
            print("✗ Windows executable not found")
            return False
            
    elif platform_name == 'darwin':
        app_path = Path('dist/PicSpider.app')
        if app_path.exists():
            print(f"✓ macOS app bundle created: {app_path}")
            exe_path = app_path / 'Contents/MacOS/PicSpider'
            if exe_path.exists():
                print(f"  Executable size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
            return True
        else:
            print("✗ macOS app bundle not found")
            return False
            
    else:  # Linux
        exe_path = Path('dist/PicSpider')
        if exe_path.exists():
            print(f"✓ Linux executable created: {exe_path}")
            print(f"  Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
            return True
        else:
            print("✗ Linux executable not found")
            return False

def cleanup():
    """Clean up build artifacts"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['PicSpider.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ Cleaned directory: {dir_name}")
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"✓ Cleaned file: {file_name}")

def main():
    """Main test function"""
    print("PicSpider Local Build Test")
    print("=" * 50)
    
    # Change to project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    print(f"Working directory: {os.getcwd()}")
    
    # Run tests
    tests = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Module Imports", test_module_imports),
        ("Create Spec File", create_spec_file),
        ("PyInstaller Build", test_build),
        ("Verify Build", verify_build),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)}")
    
    # Cleanup option
    if input("\nClean up build artifacts? (y/N): ").lower().startswith('y'):
        cleanup()
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
