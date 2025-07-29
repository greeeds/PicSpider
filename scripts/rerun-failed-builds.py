#!/usr/bin/env python3
"""
重新运行失败的构建作业
用于在部分平台构建失败时，重新运行特定平台的构建
"""

import os
import sys
import subprocess
import json
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

def check_gh_cli():
    """检查GitHub CLI是否可用"""
    success, version, _ = run_command("gh --version", check=False)
    if not success:
        print("❌ GitHub CLI未安装")
        print("请访问 https://cli.github.com/ 安装GitHub CLI")
        return False
    
    print(f"✅ GitHub CLI已安装: {version.split()[2]}")
    
    # 检查登录状态
    success, _, _ = run_command("gh auth status", check=False)
    if not success:
        print("❌ 未登录GitHub CLI")
        print("请运行 'gh auth login' 登录")
        return False
    
    print("✅ GitHub CLI已登录")
    return True

def get_latest_release():
    """获取最新Release信息"""
    success, output, error = run_command("gh release list --limit 1 --json tagName,name", check=False)
    
    if not success:
        print(f"❌ 获取Release信息失败: {error}")
        return None
    
    try:
        releases = json.loads(output)
        if not releases:
            print("📋 暂无Release")
            return None
        return releases[0]
    except json.JSONDecodeError as e:
        print(f"❌ 解析Release数据失败: {e}")
        return None

def check_release_assets(tag_name):
    """检查Release的构建产物"""
    success, output, error = run_command(f"gh api repos/$(gh repo view --json owner,name --jq '.owner.login + \"/\" + .name')/releases/tags/{tag_name} --jq '.assets[].name'", check=False)
    
    if not success:
        print(f"❌ 获取Release资产失败: {error}")
        return {}
    
    assets = output.split('\n') if output else []
    
    status = {
        'windows': 'PicSpider-Windows.zip' in assets,
        'macos': 'PicSpider-macOS.zip' in assets,
        'linux': 'PicSpider-Linux.tar.gz' in assets
    }
    
    return status

def get_workflow_runs(tag_name):
    """获取指定Release的工作流运行"""
    # 获取最近的工作流运行
    success, output, error = run_command(
        f"gh run list --workflow=release.yml --limit 10 --json status,conclusion,workflowName,createdAt,headBranch,event,databaseId",
        check=False
    )
    
    if not success:
        print(f"❌ 获取工作流运行失败: {error}")
        return []
    
    try:
        runs = json.loads(output)
        # 过滤出与当前Release相关的运行
        release_runs = []
        for run in runs:
            if run.get('event') == 'release':
                release_runs.append(run)
        return release_runs[:3]  # 最近3次运行
    except json.JSONDecodeError as e:
        print(f"❌ 解析工作流数据失败: {e}")
        return []

def rerun_workflow(run_id):
    """重新运行指定的工作流"""
    success, output, error = run_command(f"gh run rerun {run_id}", check=False)
    
    if success:
        print(f"✅ 工作流 {run_id} 重新运行成功")
        return True
    else:
        print(f"❌ 重新运行工作流失败: {error}")
        return False

def display_status(tag_name, assets_status):
    """显示构建状态"""
    print(f"\n📋 Release {tag_name} 构建状态:")
    print("-" * 50)
    
    platforms = {
        'windows': ('Windows', 'PicSpider-Windows.zip'),
        'macos': ('macOS', 'PicSpider-macOS.zip'),
        'linux': ('Linux', 'PicSpider-Linux.tar.gz')
    }
    
    failed_platforms = []
    
    for platform, (name, asset) in platforms.items():
        if assets_status.get(platform, False):
            print(f"✅ {name:<8}: {asset}")
        else:
            print(f"❌ {name:<8}: 构建失败或未完成")
            failed_platforms.append(platform)
    
    return failed_platforms

def main():
    """主函数"""
    print("重新运行失败的构建作业")
    print("=" * 50)
    
    # 检查GitHub CLI
    if not check_gh_cli():
        return False
    
    # 获取最新Release
    release = get_latest_release()
    if not release:
        return False
    
    tag_name = release['tagName']
    release_name = release['name']
    
    print(f"最新Release: {release_name} ({tag_name})")
    
    # 检查构建产物
    assets_status = check_release_assets(tag_name)
    failed_platforms = display_status(tag_name, assets_status)
    
    if not failed_platforms:
        print("\n🎉 所有平台构建都已成功！")
        return True
    
    print(f"\n⚠️  发现 {len(failed_platforms)} 个平台构建失败:")
    for platform in failed_platforms:
        print(f"  - {platform}")
    
    # 获取工作流运行
    runs = get_workflow_runs(tag_name)
    if not runs:
        print("\n❌ 未找到相关的工作流运行")
        return False
    
    print(f"\n找到 {len(runs)} 个相关工作流运行:")
    for i, run in enumerate(runs, 1):
        status = run.get('status', 'unknown')
        conclusion = run.get('conclusion', 'unknown')
        created_at = run.get('createdAt', '')
        run_id = run.get('databaseId', '')
        
        print(f"  {i}. ID: {run_id}, 状态: {status}, 结果: {conclusion}, 时间: {created_at[:19]}")
    
    # 询问是否重新运行
    print(f"\n是否重新运行最新的工作流来修复失败的构建？")
    response = input("输入 'y' 确认，其他键取消: ")
    
    if response.lower() != 'y':
        print("操作已取消")
        return False
    
    # 重新运行最新的工作流
    latest_run = runs[0]
    run_id = latest_run.get('databaseId')
    
    if not run_id:
        print("❌ 无法获取工作流ID")
        return False
    
    print(f"\n重新运行工作流 {run_id}...")
    success = rerun_workflow(run_id)
    
    if success:
        print(f"\n🚀 工作流已重新启动！")
        print(f"请访问以下链接查看进度:")
        print(f"https://github.com/$(gh repo view --json owner,name --jq '.owner.login + \"/\" + .name')/actions")
        print(f"\n构建完成后，失败的平台应该会重新构建并上传到Release页面。")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
