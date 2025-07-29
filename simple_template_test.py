#!/usr/bin/env python3
"""
简单的模板测试
"""

import os
import sys

def test_template_discovery():
    """测试模板发现机制"""
    print("=== 模板发现测试 ===")
    
    try:
        from config import app_config
        
        template_dir = app_config.get_templates_dir()
        print(f"配置的模板目录: {template_dir}")
        print(f"模板目录存在: {os.path.exists(template_dir)}")
        
        if os.path.exists(template_dir):
            print("模板目录内容:")
            for item in os.listdir(template_dir):
                item_path = os.path.join(template_dir, item)
                print(f"  - {item} ({'文件' if os.path.isfile(item_path) else '目录'})")
        
        # 检查关键模板文件
        index_path = os.path.join(template_dir, 'index.html')
        album_path = os.path.join(template_dir, 'album.html')
        
        print(f"index.html 存在: {os.path.exists(index_path)}")
        print(f"album.html 存在: {os.path.exists(album_path)}")
        
        return os.path.exists(index_path) and os.path.exists(album_path)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_import():
    """测试Flask应用导入"""
    print("\n=== Flask应用导入测试 ===")
    
    try:
        import app
        print(f"Flask应用导入成功")
        print(f"Flask应用模板文件夹: {app.app.template_folder}")
        print(f"Flask应用静态文件夹: {app.app.static_folder}")
        
        # 检查Jinja2环境
        jinja_env = app.app.jinja_env
        print(f"Jinja2环境: {jinja_env}")
        
        # 检查模板加载器
        loader = jinja_env.loader
        print(f"模板加载器: {loader}")
        
        if hasattr(loader, 'searchpath'):
            print(f"搜索路径: {loader.searchpath}")
        
        return True
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_exists_in_flask():
    """测试Flask是否能找到模板"""
    print("\n=== Flask模板存在性测试 ===")
    
    try:
        import app
        
        # 使用Flask的方式检查模板是否存在
        with app.app.app_context():
            jinja_env = app.app.jinja_env
            
            try:
                # 尝试获取模板源码
                source, filename = jinja_env.loader.get_source(jinja_env, 'index.html')
                print("✅ index.html 模板找到")
                print(f"   文件路径: {filename}")
                print(f"   内容长度: {len(source)} 字符")
            except Exception as e:
                print(f"❌ index.html 模板未找到: {e}")
                return False
            
            try:
                source, filename = jinja_env.loader.get_source(jinja_env, 'album.html')
                print("✅ album.html 模板找到")
                print(f"   文件路径: {filename}")
                print(f"   内容长度: {len(source)} 字符")
            except Exception as e:
                print(f"❌ album.html 模板未找到: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("简单模板测试")
    print("=" * 50)
    
    print(f"当前工作目录: {os.getcwd()}")
    print(f"脚本目录: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"Python路径: {sys.path[:3]}...")  # 只显示前3个路径
    
    # 运行测试
    test1 = test_template_discovery()
    test2 = test_flask_import()
    test3 = test_template_exists_in_flask()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果:")
    print(f"模板发现: {'✅ 通过' if test1 else '❌ 失败'}")
    print(f"Flask导入: {'✅ 通过' if test2 else '❌ 失败'}")
    print(f"Flask模板检测: {'✅ 通过' if test3 else '❌ 失败'}")
    
    all_passed = test1 and test2 and test3
    print(f"\n总体结果: {'✅ 所有测试通过' if all_passed else '❌ 部分测试失败'}")
    
    if all_passed:
        print("\n🎉 模板系统工作正常！")
        print("如果仍然遇到TemplateNotFound错误，可能是运行时环境问题。")
    else:
        print("\n⚠️  发现问题，请检查上述错误信息。")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
