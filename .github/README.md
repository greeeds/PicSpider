# GitHub Workflows 说明

本项目配置了自动化的GitHub Actions工作流，用于自动构建和发布PicSpider应用程序。

## 工作流概述

### 1. Release工作流 (`release.yml`)

**触发条件**: 当创建新的GitHub Release时自动触发

**功能**:
- 在Windows、macOS、Linux三个平台上自动构建应用程序
- 执行`build.py`脚本进行打包
- 将构建产物自动上传到Release页面

**构建产物**:
- `PicSpider-Windows.zip` - Windows可执行文件包
- `PicSpider-macOS.zip` - macOS应用程序包  
- `PicSpider-Linux.tar.gz` - Linux可执行文件包

### 2. 构建测试工作流 (`build-test.yml`)

**触发条件**: 
- 推送到main/master/gui分支时
- 创建Pull Request时

**功能**:
- 测试构建脚本在不同平台和Python版本上的兼容性
- 验证依赖安装和PyInstaller配置
- 快速语法检查和构建测试

## 如何发布新版本

### 方法一: 通过GitHub网页界面

1. **创建标签**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **创建Release**:
   - 访问GitHub仓库页面
   - 点击 "Releases" → "Create a new release"
   - 选择刚创建的标签 (v1.0.0)
   - 填写发布标题和说明
   - 点击 "Publish release"

3. **自动构建**:
   - GitHub Actions会自动开始构建
   - 大约10-15分钟后构建完成
   - 构建产物会自动上传到Release页面

### 方法二: 通过GitHub CLI

```bash
# 安装GitHub CLI (如果未安装)
# 详见: https://cli.github.com/

# 创建标签并推送
git tag v1.0.0
git push origin v1.0.0

# 创建Release
gh release create v1.0.0 \
  --title "PicSpider v1.0.0" \
  --notes "发布说明：
  - 新增功能A
  - 修复问题B
  - 性能优化C"
```

## 构建过程详解

### 构建环境
- **Windows**: windows-latest (Windows Server 2022)
- **macOS**: macos-latest (macOS 12)
- **Linux**: ubuntu-latest (Ubuntu 22.04)
- **Python版本**: 3.9
- **GitHub Actions版本**: 使用最新稳定版本
  - `actions/checkout@v4`
  - `actions/setup-python@v5`
  - `actions/cache@v4`
  - `actions/upload-artifact@v4`

### 构建步骤
1. **环境准备**:
   - 检出代码
   - 设置Python环境
   - 缓存pip依赖

2. **依赖安装**:
   - 安装系统依赖 (Linux需要python3-tk)
   - 安装Python依赖包

3. **执行构建**:
   - 运行`python build.py`
   - 生成跨平台可执行文件

4. **打包上传**:
   - 创建压缩包
   - 上传到Release页面

## 本地测试构建

在提交代码前，建议先本地测试构建：

```bash
# 测试构建脚本
python build.py

# 或使用测试脚本
python scripts/test-build.py
```

## 辅助脚本

项目提供了几个辅助脚本来简化发布流程：

### 1. 创建Release脚本
```bash
python scripts/create-release.py
```
功能：
- 自动检查Git状态
- 交互式输入版本号和发布说明
- 创建Git标签并推送
- 使用GitHub CLI创建Release

### 2. 工作流状态检查脚本
```bash
python scripts/check-workflows.py
```
功能：
- 检查工作流文件是否存在
- 显示最近的工作流运行状态
- 查看最新Release信息
- 检查仓库状态

### 3. 构建测试脚本
```bash
python scripts/test-build.py
```
功能：
- 本地模拟GitHub Actions构建过程
- 验证依赖和配置
- 测试PyInstaller构建

## 故障排除

### 常见问题

1. **构建失败 - 依赖问题**:
   - 检查`requirements.txt`是否包含所有必需依赖
   - 确认依赖版本兼容性

2. **构建失败 - 平台特定问题**:
   - Linux: 确保安装了`python3-tk`
   - macOS: 检查是否需要额外的系统权限
   - Windows: 确认PyInstaller配置正确

3. **上传失败**:
   - 检查Release是否已正确创建
   - 确认GitHub token权限

### 调试方法

1. **查看构建日志**:
   - 在GitHub Actions页面查看详细日志
   - 关注错误信息和警告

2. **下载调试产物**:
   - 每次构建都会上传调试产物
   - 包含dist目录和spec文件
   - 保留7天用于问题排查

3. **本地复现**:
   - 使用相同的Python版本
   - 安装相同的依赖版本
   - 运行相同的构建命令

## 自定义配置

### 修改构建平台

编辑`.github/workflows/release.yml`中的matrix配置：

```yaml
strategy:
  matrix:
    include:
      - os: windows-latest
        platform: windows
        # ... 其他配置
```

### 修改Python版本

```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.9'  # 修改为需要的版本
```

### 添加额外步骤

在构建步骤中添加自定义操作：

```yaml
- name: Custom step
  run: |
    echo "执行自定义操作"
    # 你的自定义命令
```

## 更新日志

### 2024-07-29 - Actions版本更新
- ✅ 更新 `actions/upload-artifact` 从 v3 到 v4
- ✅ 更新 `actions/setup-python` 从 v4 到 v5
- ✅ 更新 `actions/cache` 从 v3 到 v4
- ✅ 替换已弃用的 `actions/upload-release-asset@v1` 为 GitHub CLI
- ✅ 所有Actions现在使用最新稳定版本

### 主要改进
- **更好的性能**: 新版本Actions提供更快的执行速度
- **增强的安全性**: 最新版本包含安全修复
- **更好的兼容性**: 支持最新的GitHub功能
- **简化的上传**: 使用GitHub CLI替代已弃用的upload-release-asset

## 版本管理建议

### 语义化版本

建议使用语义化版本号：
- `v1.0.0` - 主要版本
- `v1.1.0` - 次要版本  
- `v1.1.1` - 补丁版本

### 发布频率

- **稳定版本**: 每月发布一次主要更新
- **补丁版本**: 根据bug修复需要随时发布
- **预发布版本**: 使用`v1.0.0-beta.1`格式

### 发布说明模板

```markdown
## 新增功能
- 功能A: 详细说明
- 功能B: 详细说明

## 问题修复  
- 修复问题A
- 修复问题B

## 性能优化
- 优化项A
- 优化项B

## 注意事项
- 重要变更说明
- 兼容性说明
```
