#!/usr/bin/env python3
"""
PicSpider 安装脚本
自动安装依赖并进行环境检查
"""

import sys
import subprocess
import os
import platform

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    print(f"当前Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 7):
        print("❌ 错误: 需要Python 3.7或更高版本")
        return False
    else:
        print("✅ Python版本检查通过")
        return True

def check_pip():
    """检查pip是否可用"""
    print("检查pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip可用")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip不可用")
        return False

def install_requirements():
    """安装依赖包"""
    print("安装依赖包...")
    try:
        # 升级pip
        print("升级pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True)
        
        # 安装依赖
        print("安装项目依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def check_tkinter():
    """检查tkinter是否可用"""
    print("检查tkinter...")
    try:
        import tkinter
        print("✅ tkinter可用")
        return True
    except ImportError:
        print("❌ tkinter不可用")
        print("请安装tkinter:")
        
        system = platform.system().lower()
        if system == "linux":
            print("Ubuntu/Debian: sudo apt-get install python3-tk")
            print("CentOS/RHEL: sudo yum install tkinter")
            print("或: sudo dnf install python3-tkinter")
        elif system == "darwin":
            print("macOS: tkinter应该已经包含在Python中")
            print("如果没有，请重新安装Python或使用Homebrew")
        elif system == "windows":
            print("Windows: tkinter应该已经包含在Python中")
            print("如果没有，请重新安装Python并确保选择了tkinter组件")
        
        return False

def create_desktop_shortcut():
    """创建桌面快捷方式（可选）"""
    system = platform.system().lower()
    current_dir = os.path.abspath(".")
    
    if system == "windows":
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "PicSpider.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = os.path.join(current_dir, "run.py")
            shortcut.WorkingDirectory = current_dir
            shortcut.IconLocation = sys.executable
            shortcut.save()
            
            print("✅ 已创建桌面快捷方式")
            return True
        except ImportError:
            print("⚠️  无法创建桌面快捷方式（缺少winshell或pywin32）")
            return False
    
    elif system == "linux":
        try:
            desktop_dir = os.path.expanduser("~/Desktop")
            if not os.path.exists(desktop_dir):
                desktop_dir = os.path.expanduser("~/桌面")
            
            if os.path.exists(desktop_dir):
                shortcut_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=PicSpider
Comment=写真爬取展示系统
Exec={sys.executable} {os.path.join(current_dir, "run.py")}
Icon=applications-internet
Path={current_dir}
Terminal=false
StartupNotify=true
"""
                shortcut_path = os.path.join(desktop_dir, "PicSpider.desktop")
                with open(shortcut_path, "w") as f:
                    f.write(shortcut_content)
                os.chmod(shortcut_path, 0o755)
                print("✅ 已创建桌面快捷方式")
                return True
        except Exception as e:
            print(f"⚠️  创建桌面快捷方式失败: {e}")
            return False
    
    print("⚠️  当前平台不支持自动创建桌面快捷方式")
    return False

def main():
    """主函数"""
    print("PicSpider 安装程序")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 检查pip
    if not check_pip():
        return False
    
    # 安装依赖
    if not install_requirements():
        return False
    
    # 检查tkinter
    if not check_tkinter():
        print("⚠️  GUI功能可能不可用，但命令行功能仍然可以使用")
    
    # 询问是否创建桌面快捷方式
    try:
        create_shortcut = input("\n是否创建桌面快捷方式？(y/N): ").lower().strip()
        if create_shortcut in ['y', 'yes', '是']:
            create_desktop_shortcut()
    except KeyboardInterrupt:
        print("\n安装被中断")
        return False
    
    print("\n" + "=" * 50)
    print("✅ 安装完成！")
    print("\n使用方法:")
    print("1. GUI模式: python run.py")
    print("2. 爬虫模式: python run.py --mode crawler")
    print("3. 服务器模式: python run.py --mode server")
    print("4. 打包应用: python build.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    
    # 询问是否立即运行
    try:
        run_now = input("\n是否立即运行PicSpider？(y/N): ").lower().strip()
        if run_now in ['y', 'yes', '是']:
            print("启动PicSpider...")
            os.system(f"{sys.executable} run.py")
    except KeyboardInterrupt:
        print("\n再见！")
