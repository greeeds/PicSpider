#!/usr/bin/env python3
"""
检查GitHub Actions工作流状态的脚本
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

def get_workflow_runs():
    """获取工作流运行状态"""
    print("获取工作流运行状态...")
    
    success, output, error = run_command("gh run list --limit 10 --json status,conclusion,workflowName,createdAt,headBranch,event", check=False)
    
    if not success:
        print(f"❌ 获取工作流状态失败: {error}")
        return None
    
    try:
        runs = json.loads(output)
        return runs
    except json.JSONDecodeError as e:
        print(f"❌ 解析工作流数据失败: {e}")
        return None

def format_datetime(iso_string):
    """格式化日期时间"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return iso_string

def display_workflow_status(runs):
    """显示工作流状态"""
    if not runs:
        print("没有找到工作流运行记录")
        return
    
    print("\n最近的工作流运行:")
    print("=" * 80)
    print(f"{'工作流':<20} {'状态':<12} {'结果':<12} {'分支':<15} {'触发':<10} {'时间':<20}")
    print("-" * 80)
    
    status_icons = {
        'completed': '✅',
        'in_progress': '🔄',
        'queued': '⏳',
        'requested': '📋'
    }
    
    conclusion_icons = {
        'success': '✅',
        'failure': '❌',
        'cancelled': '⚠️',
        'skipped': '⏭️',
        'neutral': '➖'
    }
    
    for run in runs:
        workflow_name = run.get('workflowName', 'Unknown')[:18]
        status = run.get('status', 'unknown')
        conclusion = run.get('conclusion', '')
        branch = run.get('headBranch', 'unknown')[:13]
        event = run.get('event', 'unknown')[:8]
        created_at = format_datetime(run.get('createdAt', ''))[:19]
        
        status_icon = status_icons.get(status, '❓')
        conclusion_icon = conclusion_icons.get(conclusion, '') if conclusion else ''
        
        status_display = f"{status_icon} {status}"
        conclusion_display = f"{conclusion_icon} {conclusion}" if conclusion else "-"
        
        print(f"{workflow_name:<20} {status_display:<12} {conclusion_display:<12} {branch:<15} {event:<10} {created_at:<20}")

def check_workflow_files():
    """检查工作流文件是否存在"""
    print("\n检查工作流文件:")
    print("-" * 40)
    
    workflow_files = [
        '.github/workflows/release.yml',
        '.github/workflows/build-test.yml'
    ]
    
    all_exist = True
    for file_path in workflow_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (缺失)")
            all_exist = False
    
    return all_exist

def get_latest_release():
    """获取最新Release信息"""
    print("\n检查最新Release:")
    print("-" * 40)
    
    success, output, error = run_command("gh release list --limit 1 --json tagName,name,publishedAt,assets", check=False)
    
    if not success:
        print("❌ 获取Release信息失败")
        return
    
    try:
        releases = json.loads(output)
        if not releases:
            print("📋 暂无Release")
            return
        
        release = releases[0]
        tag_name = release.get('tagName', 'Unknown')
        name = release.get('name', 'Unknown')
        published_at = format_datetime(release.get('publishedAt', ''))
        assets = release.get('assets', [])
        
        print(f"最新版本: {tag_name}")
        print(f"发布名称: {name}")
        print(f"发布时间: {published_at}")
        print(f"构建产物: {len(assets)} 个文件")
        
        if assets:
            print("产物列表:")
            for asset in assets:
                asset_name = asset.get('name', 'Unknown')
                download_count = asset.get('downloadCount', 0)
                print(f"  - {asset_name} (下载: {download_count})")
    
    except json.JSONDecodeError as e:
        print(f"❌ 解析Release数据失败: {e}")

def check_repository_info():
    """检查仓库信息"""
    print("\n仓库信息:")
    print("-" * 40)
    
    # 获取远程仓库URL
    success, output, _ = run_command("git remote get-url origin", check=False)
    if success:
        print(f"远程仓库: {output}")
    
    # 获取当前分支
    success, output, _ = run_command("git branch --show-current", check=False)
    if success:
        print(f"当前分支: {output}")
    
    # 检查是否有未推送的提交
    success, output, _ = run_command("git log origin/HEAD..HEAD --oneline", check=False)
    if success and output:
        print(f"未推送提交: {len(output.split(chr(10)))} 个")
    else:
        print("未推送提交: 0 个")

def main():
    """主函数"""
    print("GitHub Actions 工作流状态检查")
    print("=" * 50)
    
    # 检查工作流文件
    if not check_workflow_files():
        print("\n⚠️  部分工作流文件缺失，请先创建工作流文件")
    
    # 检查仓库信息
    check_repository_info()
    
    # 检查GitHub CLI
    if not check_gh_cli():
        print("\n⚠️  无法获取在线状态，请安装并登录GitHub CLI")
        return False
    
    # 获取工作流运行状态
    runs = get_workflow_runs()
    if runs is not None:
        display_workflow_status(runs)
    
    # 获取最新Release信息
    get_latest_release()
    
    print("\n" + "=" * 50)
    print("检查完成")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
