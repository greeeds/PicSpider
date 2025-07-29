#!/usr/bin/env python3
"""
模板文件调试脚本
用于诊断模板文件路径问题
"""

import os
import sys
from pathlib import Path

def debug_paths():
    """调试路径信息"""
    print("=== 路径调试信息 ===")
    print(f"Python executable: {sys.executable}")
    print(f"Script path: {__file__}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"sys.frozen: {getattr(sys, 'frozen', False)}")
    
    if hasattr(sys, '_MEIPASS'):
        print(f"sys._MEIPASS: {sys._MEIPASS}")
    
    # 检查应用程序目录
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent
        print(f"App directory (frozen): {app_dir}")
    else:
        app_dir = Path(__file__).parent
        print(f"App directory (dev): {app_dir}")
    
    print(f"App directory exists: {app_dir.exists()}")
    
    # 检查可能的模板目录
    possible_template_dirs = [
        app_dir / "templates",
        app_dir / "_internal" / "templates",
    ]
    
    if hasattr(sys, '_MEIPASS'):
        possible_template_dirs.append(Path(sys._MEIPASS) / "templates")
    
    print("\n=== 模板目录检查 ===")
    for i, template_dir in enumerate(possible_template_dirs, 1):
        print(f"{i}. {template_dir}")
        print(f"   Exists: {template_dir.exists()}")
        
        if template_dir.exists():
            print(f"   Contents:")
            try:
                for item in template_dir.iterdir():
                    print(f"     - {item.name}")
            except Exception as e:
                print(f"     Error listing contents: {e}")
    
    # 检查当前目录下的templates
    current_templates = Path("templates")
    print(f"\n=== 当前目录templates检查 ===")
    print(f"./templates exists: {current_templates.exists()}")
    if current_templates.exists():
        print("Contents:")
        try:
            for item in current_templates.iterdir():
                print(f"  - {item.name}")
        except Exception as e:
            print(f"  Error: {e}")

def test_config():
    """测试配置模块"""
    print("\n=== 配置模块测试 ===")
    try:
        from config import app_config
        
        template_dir = app_config.get_templates_dir()
        static_dir = app_config.get_static_dir()
        
        print(f"Config template dir: {template_dir}")
        print(f"Config static dir: {static_dir}")
        print(f"Template dir exists: {os.path.exists(template_dir)}")
        
        if static_dir:
            print(f"Static dir exists: {os.path.exists(static_dir)}")
        
        # 检查具体的模板文件
        index_path = os.path.join(template_dir, 'index.html')
        album_path = os.path.join(template_dir, 'album.html')
        
        print(f"index.html path: {index_path}")
        print(f"index.html exists: {os.path.exists(index_path)}")
        print(f"album.html path: {album_path}")
        print(f"album.html exists: {os.path.exists(album_path)}")
        
    except Exception as e:
        print(f"Error testing config: {e}")
        import traceback
        traceback.print_exc()

def test_flask_app():
    """测试Flask应用创建"""
    print("\n=== Flask应用测试 ===")
    try:
        from config import app_config
        from flask import Flask
        
        template_dir = app_config.get_templates_dir()
        static_dir = app_config.get_static_dir()
        
        print(f"Creating Flask app with template_folder='{template_dir}'")
        
        if static_dir and os.path.exists(static_dir):
            app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
            print(f"Flask app created with static folder: {static_dir}")
        else:
            app = Flask(__name__, template_folder=template_dir)
            print("Flask app created without static folder")
        
        print(f"Flask template folder: {app.template_folder}")
        print(f"Flask static folder: {app.static_folder}")
        
        # 测试模板加载
        with app.app_context():
            try:
                from flask import render_template_string
                # 尝试列出模板
                template_loader = app.jinja_env.loader
                print(f"Template loader: {template_loader}")
                
                if hasattr(template_loader, 'searchpath'):
                    print(f"Template search paths: {template_loader.searchpath}")
                
                # 尝试渲染一个简单的模板
                result = render_template_string("Hello {{ name }}!", name="World")
                print(f"Template rendering test: {result}")
                
            except Exception as e:
                print(f"Template test error: {e}")
        
    except Exception as e:
        print(f"Error testing Flask app: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("模板文件调试脚本")
    print("=" * 50)
    
    debug_paths()
    test_config()
    test_flask_app()
    
    print("\n" + "=" * 50)
    print("调试完成")

if __name__ == "__main__":
    main()
