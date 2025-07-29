#!/usr/bin/env python3
"""
PicSpider 打包脚本
支持Windows、macOS、Linux跨平台打包
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def get_platform_info():
    """获取平台信息"""
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
    """清理构建目录"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name)
    
    # 清理.spec文件
    spec_files = [f for f in os.listdir(".") if f.endswith(".spec")]
    for spec_file in spec_files:
        print(f"删除文件: {spec_file}")
        os.remove(spec_file)

def install_dependencies():
    """安装依赖"""
    print("安装依赖包...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("依赖安装完成")
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        return False
    return True

def create_pyinstaller_spec():
    """创建PyInstaller配置文件"""
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
    
    print("PyInstaller配置文件已创建: PicSpider.spec")

def build_application():
    """构建应用程序"""
    print("开始构建应用程序...")
    
    try:
        # 使用PyInstaller构建
        cmd = [sys.executable, "-m", "PyInstaller", "PicSpider.spec", "--clean"]
        subprocess.run(cmd, check=True)
        print("应用程序构建完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False

def copy_additional_files():
    """复制额外的文件到dist目录"""
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("dist目录不存在")
        return
    
    # 查找应用程序目录
    app_dirs = [d for d in dist_dir.iterdir() if d.is_dir()]
    if not app_dirs:
        print("未找到应用程序目录")
        return
    
    app_dir = app_dirs[0]  # 通常是第一个目录
    
    # 复制README文件
    if os.path.exists("README.md"):
        shutil.copy2("README.md", app_dir / "README.md")
        print("已复制README.md")
    
    # 创建示例配置文件
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
    print("已创建配置文件")

def create_startup_scripts():
    """创建启动脚本"""
    platform_name, ext = get_platform_info()
    dist_dir = Path("dist")
    
    if platform_name == "windows":
        # Windows批处理文件
        bat_content = '''@echo off
cd /d "%~dp0"
PicSpider.exe
pause
'''
        with open(dist_dir / "start.bat", "w", encoding="utf-8") as f:
            f.write(bat_content)
        print("已创建Windows启动脚本: start.bat")
        
    elif platform_name in ["macos", "linux"]:
        # Unix shell脚本
        sh_content = '''#!/bin/bash
cd "$(dirname "$0")"
./PicSpider
'''
        script_path = dist_dir / "start.sh"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(sh_content)
        # 添加执行权限
        os.chmod(script_path, 0o755)
        print("已创建Unix启动脚本: start.sh")

def main():
    """主函数"""
    print("PicSpider 应用程序打包工具")
    print("=" * 50)
    
    platform_name, ext = get_platform_info()
    print(f"当前平台: {platform_name}")
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        return False
    
    # 步骤1: 清理构建目录
    print("\n步骤1: 清理构建目录")
    clean_build_dirs()
    
    # 步骤2: 安装依赖
    print("\n步骤2: 安装依赖")
    if not install_dependencies():
        return False
    
    # 步骤3: 创建PyInstaller配置
    print("\n步骤3: 创建PyInstaller配置")
    create_pyinstaller_spec()
    
    # 步骤4: 构建应用程序
    print("\n步骤4: 构建应用程序")
    if not build_application():
        return False
    
    # 步骤5: 复制额外文件
    print("\n步骤5: 复制额外文件")
    copy_additional_files()
    
    # 步骤6: 创建启动脚本
    print("\n步骤6: 创建启动脚本")
    create_startup_scripts()
    
    print("\n" + "=" * 50)
    print("打包完成！")
    print(f"应用程序位于: dist/")
    print("\n使用说明:")
    print("1. 进入dist目录")
    print("2. 运行PicSpider可执行文件")
    print("3. 或者使用提供的启动脚本")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
