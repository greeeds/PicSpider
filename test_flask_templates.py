#!/usr/bin/env python3
"""
测试Flask模板加载
"""

import os
import sys
from pathlib import Path

def test_template_loading():
    """测试模板加载"""
    print("=== Flask模板加载测试 ===")
    
    try:
        # 导入配置和Flask应用
        from config import app_config
        import app
        
        print(f"Template directory: {app_config.get_templates_dir()}")
        print(f"Template directory exists: {os.path.exists(app_config.get_templates_dir())}")
        
        # 测试Flask应用
        with app.app.app_context():
            try:
                from flask import render_template
                
                # 尝试渲染index.html模板
                print("Testing index.html template...")
                # 创建一些测试数据
                test_albums = [
                    {'name': 'Test Album 1', 'image_count': 10},
                    {'name': 'Test Album 2', 'image_count': 15}
                ]
                test_pagination = {
                    'page': 1, 'total_pages': 1, 'has_prev': False,
                    'has_next': False, 'prev_num': 0, 'next_num': 2
                }
                
                result = render_template('index.html', 
                                       albums=test_albums, 
                                       pagination=test_pagination,
                                       search_query='')
                print("✅ index.html template rendered successfully")
                print(f"Rendered content length: {len(result)} characters")
                
                # 测试album.html模板
                print("Testing album.html template...")
                test_images = ['image1.jpg', 'image2.jpg', 'image3.jpg']
                result = render_template('album.html', 
                                       album_name='Test Album',
                                       images=test_images)
                print("✅ album.html template rendered successfully")
                print(f"Rendered content length: {len(result)} characters")
                
                return True
                
            except Exception as e:
                print(f"❌ Template rendering failed: {e}")
                import traceback
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"❌ Failed to import modules: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_server():
    """测试Flask服务器启动"""
    print("\n=== Flask服务器启动测试 ===")
    
    try:
        import app
        import threading
        import time
        import requests
        
        # 在后台线程启动服务器
        def run_server():
            app.run_app(host='127.0.0.1', port=5001, debug=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # 等待服务器启动
        time.sleep(2)
        
        # 测试服务器响应
        try:
            response = requests.get('http://127.0.0.1:5001/', timeout=5)
            if response.status_code == 200:
                print("✅ Flask server started successfully")
                print(f"Response status: {response.status_code}")
                print(f"Response content length: {len(response.text)} characters")
                return True
            else:
                print(f"❌ Server responded with status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to server: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("Flask模板和服务器测试")
    print("=" * 50)
    
    # 显示环境信息
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script directory: {Path(__file__).parent}")
    print(f"sys.frozen: {getattr(sys, 'frozen', False)}")
    
    if hasattr(sys, '_MEIPASS'):
        print(f"sys._MEIPASS: {sys._MEIPASS}")
    
    # 测试模板加载
    template_success = test_template_loading()
    
    # 测试服务器启动（可选）
    server_test = input("\n是否测试Flask服务器启动? (y/N): ").lower().startswith('y')
    server_success = True
    
    if server_test:
        server_success = test_flask_server()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果:")
    print(f"模板加载: {'✅ 成功' if template_success else '❌ 失败'}")
    if server_test:
        print(f"服务器启动: {'✅ 成功' if server_success else '❌ 失败'}")
    
    overall_success = template_success and server_success
    print(f"\n总体结果: {'✅ 所有测试通过' if overall_success else '❌ 部分测试失败'}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
