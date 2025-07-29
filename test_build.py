#!/usr/bin/env python3
"""
PicSpider 构建测试脚本
测试各个模块是否正常工作
"""

import sys
import os
import importlib.util

def test_import(module_name, file_path=None):
    """测试模块导入"""
    try:
        if file_path:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        else:
            __import__(module_name)
        print(f"✅ {module_name} 导入成功")
        return True
    except Exception as e:
        print(f"❌ {module_name} 导入失败: {e}")
        return False

def test_config():
    """测试配置模块"""
    try:
        from config import app_config
        
        # 测试基本配置获取
        photo_dir = app_config.get_photo_dir()
        templates_dir = app_config.get_templates_dir()
        
        print(f"✅ 配置模块正常")
        print(f"   图片目录: {photo_dir}")
        print(f"   模板目录: {templates_dir}")
        return True
    except Exception as e:
        print(f"❌ 配置模块测试失败: {e}")
        return False

def test_flask_app():
    """测试Flask应用"""
    try:
        import app
        print("✅ Flask应用模块正常")
        return True
    except Exception as e:
        print(f"❌ Flask应用测试失败: {e}")
        return False

def test_crawler():
    """测试爬虫模块"""
    try:
        import main
        print("✅ 爬虫模块正常")
        return True
    except Exception as e:
        print(f"❌ 爬虫模块测试失败: {e}")
        return False

def test_gui():
    """测试GUI模块"""
    try:
        # 只测试导入，不启动GUI
        import tkinter
        import gui
        print("✅ GUI模块正常")
        return True
    except ImportError as e:
        if "tkinter" in str(e):
            print("⚠️  tkinter不可用，GUI功能将无法使用")
            return False
        else:
            print(f"❌ GUI模块测试失败: {e}")
            return False
    except Exception as e:
        print(f"❌ GUI模块测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖包"""
    dependencies = [
        "flask",
        "requests",
        ("beautifulsoup4", "bs4"),  # beautifulsoup4包名，但导入名是bs4
        "concurrent.futures",
        "threading",
        "json",
        "pathlib",
        "time",
        "os",
        "sys"
    ]
    
    failed = []
    for dep in dependencies:
        if isinstance(dep, tuple):
            # 处理包名和导入名不同的情况
            package_name, import_name = dep
            if not test_import(import_name):
                failed.append(package_name)
        else:
            if not test_import(dep):
                failed.append(dep)
    
    if failed:
        print(f"❌ 以下依赖包缺失: {', '.join(failed)}")
        return False
    else:
        print("✅ 所有依赖包正常")
        return True

def test_file_structure():
    """测试文件结构"""
    required_files = [
        "config.py",
        "app.py", 
        "main.py",
        "gui.py",
        "run.py",
        "requirements.txt",
        "templates/index.html",
        "templates/album.html"
    ]
    
    missing = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing.append(file_path)
    
    if missing:
        print(f"❌ 以下文件缺失: {', '.join(missing)}")
        return False
    else:
        print("✅ 文件结构完整")
        return True

def main():
    """主测试函数"""
    print("PicSpider 构建测试")
    print("=" * 50)
    
    tests = [
        ("文件结构", test_file_structure),
        ("依赖包", test_dependencies),
        ("配置模块", test_config),
        ("Flask应用", test_flask_app),
        ("爬虫模块", test_crawler),
        ("GUI模块", test_gui),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n测试 {test_name}...")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 所有测试通过，可以进行打包")
        return True
    else:
        print("❌ 部分测试失败，请修复后再打包")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
