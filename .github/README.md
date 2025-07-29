# GitHub Workflows 说明

本项目配置了自动化的GitHub Actions工作流，用于自动构建和发布PicSpider应用程序。

## 工作流概述

### 1. Release工作流 (`release.yml`)

**触发条件**: 当创建新的GitHub Release时自动触发

**功能**:
- 在Windows、macOS、Linux三个平台上独立并行构建应用程序
- 执行`build.py`脚本进行打包
- 将构建产物自动上传到Release页面
- **容错机制**: 各平台独立构建，单个平台失败不影响其他平台

**构建产物**:
- `PicSpider-Windows.zip` - Windows可执行文件包
- `PicSpider-macOS.zip` - macOS应用程序包
- `PicSpider-Linux.tar.gz` - Linux可执行文件包

### 1.1. Release汇总工作流 (`release-summary.yml`)

**触发条件**: Release工作流完成后自动触发

**功能**:
- 检查各平台构建状态并生成汇总报告
- 自动更新Release描述显示构建结果
- 全部构建失败时自动创建Issue提醒
- 提供构建状态的可视化反馈

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

## 独立构建架构

### 设计理念

从2024-07-29开始，我们将原来的matrix构建策略改为独立的并行构建，每个平台都有自己的构建作业：

- **`build-windows`**: 专门构建Windows版本
- **`build-macos`**: 专门构建macOS版本
- **`build-linux`**: 专门构建Linux版本

### 优势

1. **容错性**: 单个平台构建失败不会影响其他平台
2. **并行性**: 三个平台同时构建，总体时间不变
3. **可维护性**: 每个平台的配置独立，便于调试和维护
4. **可靠性**: 即使部分平台失败，用户仍可获得可用的构建产物

### 构建状态追踪

- **自动汇总**: `release-summary.yml`会在所有构建完成后生成状态报告
- **Release更新**: 自动在Release描述中显示各平台构建状态
- **失败提醒**: 全部构建失败时自动创建Issue

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

### 4. 重新运行失败构建脚本
```bash
python scripts/rerun-failed-builds.py
```
功能：
- 检查最新Release的构建状态
- 识别失败的平台构建
- 一键重新运行失败的工作流
- 提供构建状态的详细报告

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

4. **Unicode编码错误 (Windows)**:
   - 错误信息: `UnicodeEncodeError: 'charmap' codec can't encode characters`
   - 解决方案: 已在build.py中添加UTF-8编码处理
   - 环境变量: 工作流中设置了`PYTHONIOENCODING=utf-8`和`PYTHONUTF8=1`

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

### 2024-07-29 - Actions版本更新和编码修复
- ✅ 更新 `actions/upload-artifact` 从 v3 到 v4
- ✅ 更新 `actions/setup-python` 从 v4 到 v5
- ✅ 更新 `actions/cache` 从 v3 到 v4
- ✅ 替换已弃用的 `actions/upload-release-asset@v1` 为 GitHub CLI
- ✅ 修复Windows环境下的Unicode编码问题
- ✅ 将build.py中的中文注释改为英文，避免编码错误
- ✅ 添加UTF-8环境变量确保跨平台兼容性

### 主要改进
- **更好的性能**: 新版本Actions提供更快的执行速度
- **增强的安全性**: 最新版本包含安全修复
- **更好的兼容性**: 支持最新的GitHub功能
- **简化的上传**: 使用GitHub CLI替代已弃用的upload-release-asset
- **编码问题修复**: 解决Windows环境下的Unicode编码错误
- **跨平台兼容**: 统一使用英文输出，避免编码问题
- **独立构建**: 各平台独立构建，提高容错性和可靠性
- **智能汇总**: 自动生成构建状态报告和失败提醒

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
