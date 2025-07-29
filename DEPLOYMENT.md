# PicSpider 部署和打包指南

## 概述

PicSpider 现在已经完全支持打包成跨平台的独立应用程序，用户无需安装Python环境即可使用。

## 🎯 主要改进

### 1. GUI界面
- 添加了完整的图形用户界面
- 支持爬虫配置和管理
- 实时日志显示
- Web服务器控制
- 配置文件管理

### 2. 跨平台支持
- **Windows**: 生成 `.exe` 可执行文件
- **macOS**: 生成 `.app` 应用程序包
- **Linux**: 生成可执行文件

### 3. 配置管理
- 自动生成和管理 `config.json` 配置文件
- 支持运行时配置修改
- 智能路径处理（开发环境 vs 打包环境）

### 4. 多种运行模式
- **GUI模式**: 图形界面（推荐）
- **命令行模式**: 传统命令行操作
- **服务器模式**: 仅运行Web服务
- **爬虫模式**: 仅运行爬虫

## 🚀 快速开始

### 方式一：直接使用（推荐）
```bash
# 1. 自动安装依赖
python install.py

# 2. 启动应用
python run.py
```

### 方式二：手动安装
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动GUI
python gui.py
```

## 📦 打包成独立应用

### 1. 环境准备
确保已安装所有依赖：
```bash
python install.py
```

### 2. 运行打包脚本
```bash
python build.py
```

### 3. 打包结果
打包完成后，在 `dist/` 目录中会生成：
- **Windows**: `PicSpider.exe` + 相关文件
- **macOS**: `PicSpider.app` + `PicSpider` 可执行文件
- **Linux**: `PicSpider` 可执行文件

### 4. 分发应用
将整个 `dist/` 目录复制到目标机器即可运行，无需安装Python。

## 🛠️ 开发和测试

### 测试构建环境
```bash
python test_build.py
```

### 启动脚本
- **Windows**: `start.bat`
- **Unix/Linux/macOS**: `start.sh`

### 多种启动方式
```bash
# GUI模式
python run.py

# 爬虫模式
python run.py --mode crawler

# 服务器模式
python run.py --mode server --host 0.0.0.0 --port 8000

# 调试模式
python run.py --mode server --debug
```

## 📁 文件结构

```
PicSpider/
├── gui.py              # GUI主界面
├── app.py              # Flask Web服务器
├── main.py             # 爬虫核心模块
├── config.py           # 配置管理
├── run.py              # 统一启动脚本
├── install.py          # 自动安装脚本
├── build.py            # 打包构建脚本
├── test_build.py       # 构建测试脚本
├── requirements.txt    # Python依赖
├── start.bat           # Windows启动脚本
├── start.sh            # Unix启动脚本
├── config.json         # 配置文件（自动生成）
├── templates/          # Web模板
├── downloaded/         # 图片存储目录
└── dist/              # 打包输出目录
```

## ⚙️ 配置说明

### config.json 配置文件
```json
{
  "photo_dir": "downloaded",
  "albums_per_page": 12,
  "flask_host": "127.0.0.1",
  "flask_port": 5000,
  "flask_debug": false,
  "max_workers": 5,
  "download_delay": 0.5,
  "retry_count": 3,
  "categories": {
    "https://everia.club/category/gravure/": 287,
    "https://everia.club/category/japan/": 274,
    "https://everia.club/category/korea/": 175,
    "https://everia.club/category/chinese/": 256,
    "https://everia.club/category/cosplay/": 115
  }
}
```

## 🔧 故障排除

### 常见问题

1. **GUI无法启动**
   - 确保安装了tkinter: `sudo apt-get install python3-tk` (Linux)
   - Windows/macOS通常已包含tkinter

2. **打包失败**
   - 运行 `python test_build.py` 检查环境
   - 确保所有依赖已正确安装

3. **Web服务无法访问**
   - 检查防火墙设置
   - 确认端口未被占用

4. **爬虫下载失败**
   - 检查网络连接
   - 调整重试次数和延迟时间

### 依赖问题
如果遇到依赖冲突，可以使用虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

## 🎉 使用建议

1. **首次使用**: 推荐使用GUI模式，界面友好
2. **服务器部署**: 使用命令行模式，更稳定
3. **批量处理**: 直接运行爬虫模式
4. **开发调试**: 启用调试模式

## 📝 更新日志

- ✅ 添加GUI界面支持
- ✅ 实现跨平台打包
- ✅ 配置文件管理
- ✅ 多种运行模式
- ✅ 自动安装脚本
- ✅ 构建测试工具
- ✅ 启动脚本优化

现在任何人都可以：
1. 下载源码后运行 `python install.py` 自动安装
2. 运行 `python run.py` 启动GUI界面
3. 或者使用 `python build.py` 打包成独立应用程序
4. 将打包后的应用分发给其他用户，无需Python环境即可使用
