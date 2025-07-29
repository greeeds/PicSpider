#!/usr/bin/env python3
"""
创建GitHub Release的辅助脚本
简化发布流程，自动创建标签和Release
"""

import os
import sys
import subprocess
import json
import re
from datetime import datetime

def run_command(cmd, check=True):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=check, 
            capture_output=True, 
            text=True
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_git_status():
    """检查Git状态"""
    print("检查Git状态...")
    
    # 检查是否在Git仓库中
    success, _, _ = run_command("git rev-parse --git-dir", check=False)
    if not success:
        print("❌ 当前目录不是Git仓库")
        return False
    
    # 检查是否有未提交的更改
    success, output, _ = run_command("git status --porcelain", check=False)
    if success and output:
        print("⚠️  有未提交的更改:")
        print(output)
        response = input("是否继续? (y/N): ")
        if not response.lower().startswith('y'):
            return False
    
    # 检查当前分支
    success, branch, _ = run_command("git branch --show-current", check=False)
    if success:
        print(f"当前分支: {branch}")
        if branch not in ['main', 'master']:
            print("⚠️  不在主分支上")
            response = input("是否继续? (y/N): ")
            if not response.lower().startswith('y'):
                return False
    
    print("✅ Git状态检查通过")
    return True

def get_existing_tags():
    """获取现有标签"""
    success, output, _ = run_command("git tag -l", check=False)
    if success:
        return [tag.strip() for tag in output.split('\n') if tag.strip()]
    return []

def validate_version(version):
    """验证版本号格式"""
    # 支持语义化版本号格式: v1.0.0, v1.0.0-beta.1 等
    pattern = r'^v\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?$'
    return re.match(pattern, version) is not None

def suggest_next_version(existing_tags):
    """建议下一个版本号"""
    if not existing_tags:
        return "v1.0.0"
    
    # 解析现有版本号
    versions = []
    for tag in existing_tags:
        match = re.match(r'^v(\d+)\.(\d+)\.(\d+)', tag)
        if match:
            major, minor, patch = map(int, match.groups())
            versions.append((major, minor, patch, tag))
    
    if not versions:
        return "v1.0.0"
    
    # 找到最新版本
    versions.sort(reverse=True)
    latest_major, latest_minor, latest_patch, _ = versions[0]
    
    # 建议版本号
    suggestions = [
        f"v{latest_major}.{latest_minor}.{latest_patch + 1}",  # 补丁版本
        f"v{latest_major}.{latest_minor + 1}.0",              # 次要版本
        f"v{latest_major + 1}.0.0"                            # 主要版本
    ]
    
    return suggestions

def get_version_input():
    """获取版本号输入"""
    existing_tags = get_existing_tags()
    
    if existing_tags:
        print(f"现有标签: {', '.join(existing_tags[-5:])}")  # 显示最近5个标签
        suggestions = suggest_next_version(existing_tags)
        if isinstance(suggestions, list):
            print("建议版本号:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        else:
            print(f"建议版本号: {suggestions}")
    
    while True:
        version = input("\n请输入版本号 (如 v1.0.0): ").strip()
        
        if not version:
            print("版本号不能为空")
            continue
        
        if not version.startswith('v'):
            version = 'v' + version
        
        if not validate_version(version):
            print("版本号格式无效，请使用语义化版本号格式 (如 v1.0.0)")
            continue
        
        if version in existing_tags:
            print(f"版本号 {version} 已存在")
            continue
        
        return version

def get_release_notes():
    """获取发布说明"""
    print("\n请输入发布说明 (支持Markdown格式):")
    print("输入完成后按Ctrl+D (Linux/Mac) 或 Ctrl+Z (Windows) 结束")
    
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    notes = '\n'.join(lines).strip()
    
    if not notes:
        # 提供默认模板
        notes = f"""## 新增功能
- 功能描述

## 问题修复
- 修复描述

## 性能优化
- 优化描述

## 注意事项
- 重要说明
"""
    
    return notes

def create_tag(version):
    """创建Git标签"""
    print(f"创建标签 {version}...")
    
    success, _, error = run_command(f"git tag -a {version} -m 'Release {version}'")
    if not success:
        print(f"❌ 创建标签失败: {error}")
        return False
    
    print("✅ 标签创建成功")
    return True

def push_tag(version):
    """推送标签到远程仓库"""
    print(f"推送标签 {version} 到远程仓库...")
    
    success, _, error = run_command(f"git push origin {version}")
    if not success:
        print(f"❌ 推送标签失败: {error}")
        return False
    
    print("✅ 标签推送成功")
    return True

def create_github_release(version, notes):
    """使用GitHub CLI创建Release"""
    print("检查GitHub CLI...")
    
    # 检查是否安装了GitHub CLI
    success, _, _ = run_command("gh --version", check=False)
    if not success:
        print("⚠️  未安装GitHub CLI")
        print("请访问 https://cli.github.com/ 安装GitHub CLI")
        print("或手动在GitHub网页上创建Release")
        return False
    
    # 检查是否已登录
    success, _, _ = run_command("gh auth status", check=False)
    if not success:
        print("⚠️  未登录GitHub CLI")
        print("请运行 'gh auth login' 登录")
        return False
    
    print(f"创建GitHub Release {version}...")
    
    # 创建临时文件保存发布说明
    notes_file = f"/tmp/release-notes-{version}.md"
    try:
        with open(notes_file, 'w', encoding='utf-8') as f:
            f.write(notes)
        
        # 创建Release
        cmd = f'gh release create {version} --title "PicSpider {version}" --notes-file "{notes_file}"'
        success, output, error = run_command(cmd)
        
        if success:
            print("✅ GitHub Release创建成功")
            print(f"Release URL: {output}")
            return True
        else:
            print(f"❌ 创建Release失败: {error}")
            return False
    
    finally:
        # 清理临时文件
        if os.path.exists(notes_file):
            os.remove(notes_file)

def main():
    """主函数"""
    print("PicSpider Release创建工具")
    print("=" * 50)
    
    # 检查Git状态
    if not check_git_status():
        return False
    
    # 获取版本号
    version = get_version_input()
    print(f"选择的版本号: {version}")
    
    # 获取发布说明
    notes = get_release_notes()
    
    # 确认信息
    print("\n" + "=" * 50)
    print("发布信息确认:")
    print(f"版本号: {version}")
    print("发布说明:")
    print("-" * 30)
    print(notes)
    print("-" * 30)
    
    response = input("\n确认创建Release? (y/N): ")
    if not response.lower().startswith('y'):
        print("取消创建Release")
        return False
    
    # 创建标签
    if not create_tag(version):
        return False
    
    # 推送标签
    if not push_tag(version):
        return False
    
    # 创建GitHub Release
    if create_github_release(version, notes):
        print("\n🎉 Release创建成功!")
        print("GitHub Actions将自动开始构建，请稍后查看Release页面获取构建产物。")
    else:
        print("\n⚠️  标签已创建并推送，但GitHub Release创建失败")
        print("请手动在GitHub网页上创建Release")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
