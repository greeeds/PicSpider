#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PicSpider Build Script
Cross-platform packaging for Windows, macOS, Linux
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform.startswith('win'):
    import locale
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

def get_platform_info():
    """Get platform information"""
    system = platform.system().lower()
    arch = platform.machine().lower()

    if system == "windows":
        return "windows", "exe"
    elif system == "darwin":
        return "macos", "app"
    elif system == "linux":
        return "linux", ""
    else:
        return "unknown", ""

def clean_build_dirs():
    """Clean build directories"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning directory: {dir_name}")
            shutil.rmtree(dir_name)

    # Clean .spec files
    spec_files = [f for f in os.listdir(".") if f.endswith(".spec")]
    for spec_file in spec_files:
        print(f"Removing file: {spec_file}")
        os.remove(spec_file)

def install_dependencies():
    """Install dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                      check=True)
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False
    return True

def create_pyinstaller_spec():
    """Create PyInstaller configuration file"""
    platform_name, ext = get_platform_info()

    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

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
    hooksconfig={{}},
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
    console=False,  # 设置为False以隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标文件路径
)
'''

    # 如果是macOS，添加app bundle配置
    if platform_name == "macos":
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
)
'''

    with open("PicSpider.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)

    print("PyInstaller configuration file created: PicSpider.spec")

def build_application():
    """Build application"""
    print("Starting application build...")

    try:
        # Build with PyInstaller
        cmd = [sys.executable, "-m", "PyInstaller", "PicSpider.spec", "--clean"]
        subprocess.run(cmd, check=True)
        print("Application build completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False

def copy_additional_files():
    """Copy additional files to dist directory"""
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("dist directory does not exist")
        return

    # Find application directory
    app_dirs = [d for d in dist_dir.iterdir() if d.is_dir()]
    if not app_dirs:
        print("Application directory not found")
        return

    app_dir = app_dirs[0]  # Usually the first directory

    # Copy README file
    if os.path.exists("README.md"):
        shutil.copy2("README.md", app_dir / "README.md")
        print("README.md copied")

    # Create example configuration file
    config_example = {
        "photo_dir": "downloaded",
        "albums_per_page": 12,
        "flask_host": "127.0.0.1",
        "flask_port": 5000,
        "flask_debug": False,
        "max_workers": 5,
        "download_delay": 0.5,
        "retry_count": 3,
        "categories": {
            "https://everia.club/category/gravure/": 287,
            "https://everia.club/category/japan/": 274,
            "https://everia.club/category/korea/": 175,
            "https://everia.club/category/chinese/": 256,
            "https://everia.club/category/cosplay/": 115
        }
    }

    import json
    with open(app_dir / "config.json", "w", encoding="utf-8") as f:
        json.dump(config_example, f, indent=2, ensure_ascii=False)
    print("Configuration file created")

def create_startup_scripts():
    """Create startup scripts"""
    platform_name, ext = get_platform_info()
    dist_dir = Path("dist")

    if platform_name == "windows":
        # Windows batch file
        bat_content = '''@echo off
cd /d "%~dp0"
PicSpider.exe
pause
'''
        with open(dist_dir / "start.bat", "w", encoding="utf-8") as f:
            f.write(bat_content)
        print("Windows startup script created: start.bat")

    elif platform_name in ["macos", "linux"]:
        # Unix shell script
        sh_content = '''#!/bin/bash
cd "$(dirname "$0")"
./PicSpider
'''
        script_path = dist_dir / "start.sh"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(sh_content)
        # Add execute permission
        os.chmod(script_path, 0o755)
        print("Unix startup script created: start.sh")

def main():
    """Main function"""
    print("PicSpider Application Build Tool")
    print("=" * 50)

    platform_name, ext = get_platform_info()
    print(f"Current platform: {platform_name}")

    # Check Python version
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        return False

    # Step 1: Clean build directories
    print("\nStep 1: Clean build directories")
    clean_build_dirs()

    # Step 2: Install dependencies
    print("\nStep 2: Install dependencies")
    if not install_dependencies():
        return False

    # Step 3: Create PyInstaller configuration
    print("\nStep 3: Create PyInstaller configuration")
    create_pyinstaller_spec()

    # Step 4: Build application
    print("\nStep 4: Build application")
    if not build_application():
        return False

    # Step 5: Copy additional files
    print("\nStep 5: Copy additional files")
    copy_additional_files()

    # Step 6: Create startup scripts
    print("\nStep 6: Create startup scripts")
    create_startup_scripts()

    print("\n" + "=" * 50)
    print("Build completed!")
    print(f"Application located at: dist/")
    print("\nUsage instructions:")
    print("1. Navigate to dist directory")
    print("2. Run PicSpider executable")
    print("3. Or use the provided startup scripts")

    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
