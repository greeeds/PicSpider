# PicSpider 写真爬取展示

[![Build Test](https://github.com/YOUR_USERNAME/PicSpider/actions/workflows/build-test.yml/badge.svg)](https://github.com/YOUR_USERNAME/PicSpider/actions/workflows/build-test.yml)
[![Release](https://github.com/YOUR_USERNAME/PicSpider/actions/workflows/release.yml/badge.svg)](https://github.com/YOUR_USERNAME/PicSpider/actions/workflows/release.yml)

## 项目简介

PicSpider是一个优雅的写真相册展示系统，提供了简洁美观的界面来浏览和管理图片相册。系统采用现代化的UI设计，支持相册预览、图片浏览、搜索等功能，为用户提供流畅的浏览体验。
项目99%由ai编写

## web展示
![image](https://github.com/user-attachments/assets/aff7d938-9ec3-408c-a48d-09172263df73)

## 主要功能

- **相册展示**：以网格布局展示所有相册，支持缩略图预览
- **响应式设计**：完美适配各种屏幕尺寸，从移动设备到桌面显示器
- **搜索功能**：支持按相册名称搜索
- **分页浏览**：相册列表支持分页显示
- **优雅的UI**：采用现代简约设计风格，提供流畅的用户体验
- **图片预览**：支持查看相册内的完整图片内容

## 技术栈

- **后端框架**：Python Flask
- **前端框架**：
  - Bootstrap 5.3.3
  - PhotoSwipe 5.4.3（图片查看器）
- **UI组件**：
  - Bootstrap Icons
  - 自定义CSS样式

## 目录结构

```
├── app.py          # Web服务器入口
│                   # - 提供相册浏览和图片展示功能
│                   # - 实现相册分页和搜索功能
│                   # - 处理图片文件的访问请求
│                   # - 管理相册缩略图缓存
├── main.py         # 爬虫核心模块
│                   # - 实现并发下载功能
│                   # - 智能任务队列管理
│                   # - 图片处理和存储
│                   # - 异常处理和重试机制
├── templates/      # 前端模板目录
│   ├── index.html  # 首页模板 - 展示相册网格和搜索功能
│   └── album.html  # 相册详情页 - 支持图片预览和浏览
└── downloaded/     # 相册图片存储目录
                    # - 按相册分类存储图片
                    # - 支持增量更新
```

## 快速开始

### 方式一：使用安装脚本（推荐）

1. **自动安装**：
```bash
python install.py
```
安装脚本会自动：
- 检查Python版本
- 安装所有依赖
- 检查环境配置
- 可选创建桌面快捷方式

2. **启动应用**：
```bash
python run.py
```

### 方式二：手动安装

1. **确保Python版本**：需要Python 3.7或更高版本

2. **安装依赖包**：
```bash
pip install -r requirements.txt
```

3. **运行应用**：
```bash
# GUI模式（推荐）
python run.py

# 或者分别运行
python gui.py
```

## 使用方式

### GUI界面模式（推荐）
```bash
python run.py
```
提供友好的图形界面，包含：
- 爬虫控制和配置
- Web服务器管理
- 实时日志显示
- 配置管理

### 命令行模式
```bash
# 只运行爬虫
python run.py --mode crawler

# 只运行Web服务器
python run.py --mode server --host 0.0.0.0 --port 8000

# 启用调试模式
python run.py --mode server --debug
```

### 传统方式
```bash
# 先运行爬虫
python main.py

# 再启动Web服务
python app.py
```

## 打包成独立应用

### 本地打包

支持打包成跨平台的独立可执行文件：

```bash
python build.py
```

打包后的应用位于 `dist/` 目录，可以在没有Python环境的机器上直接运行。

支持的平台：
- Windows (.exe)
- macOS (.app)
- Linux (可执行文件)

### 自动化构建和发布

项目配置了GitHub Actions工作流，可以自动进行跨平台构建和发布：

#### 工作流说明
- **Release工作流**: 在创建GitHub Release时自动触发，执行跨平台独立构建
- **构建测试工作流**: 在代码推送和PR时运行，验证构建脚本的正确性
- **Release汇总工作流**: 构建完成后自动生成状态报告和失败提醒

#### 独立构建特性
- **容错机制**: 各平台独立构建，单个平台失败不影响其他平台
- **并行构建**: Windows、macOS、Linux同时构建，提高效率
- **智能汇总**: 自动检查构建状态并更新Release描述
- **失败恢复**: 提供脚本一键重新运行失败的构建

#### 创建发布版本
1. 为你的代码创建标签：
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. 在GitHub上创建Release：
   - 进入仓库页面，点击"Releases" → "Create a new release"
   - 选择刚才创建的标签 (v1.0.0)
   - 填写发布标题和说明
   - 点击"Publish release"

3. 自动构建：
   - GitHub Actions会自动构建Windows、macOS和Linux版本
   - 构建完成后会自动上传到Release页面
   - 整个过程大约需要10-15分钟

#### 构建产物
每次发布会自动生成以下文件：
- `PicSpider-Windows.zip` - Windows可执行文件
- `PicSpider-macOS.zip` - macOS应用程序包
- `PicSpider-Linux.tar.gz` - Linux可执行文件

#### 本地测试构建
在提交代码前，可以使用测试脚本验证构建：
```bash
python scripts/test-build.py
```

#### 构建失败恢复
如果部分平台构建失败，可以使用恢复脚本：
```bash
python scripts/rerun-failed-builds.py
```

#### 构建环境
- **Python版本**: 3.9
- **支持平台**: Windows、macOS、Linux
- **构建工具**: PyInstaller
- **依赖缓存**: 自动缓存pip依赖以加速构建

更多详细信息请查看 [GitHub工作流文档](.github/README.md)。

## 功能说明

### GUI界面功能
- **主页**：一键启动爬虫和Web服务，查看运行状态
- **爬虫配置**：设置下载目录、线程数、延迟等参数
- **服务器配置**：配置Web服务器地址、端口等
- **日志查看**：实时查看运行日志和错误信息

### Web界面功能
1. **浏览相册**
   - 首页以网格形式展示所有相册
   - 点击相册可进入详情页查看完整图片集
   - 支持分页浏览，使用页面底部的分页控件导航

2. **搜索相册**
   - 使用顶部搜索框输入关键词
   - 系统会实时过滤并显示匹配的相册

3. **查看图片**
   - 在相册详情页面可查看所有图片
   - 支持图片放大、滑动浏览等功能

### 配置管理
- 自动生成配置文件 `config.json`
- 支持自定义下载目录、服务器设置等
- 配置更改实时生效

## 文件结构

```
PicSpider/
├── gui.py              # GUI主界面
├── app.py              # Flask Web服务器
├── main.py             # 爬虫核心模块
├── config.py           # 配置管理
├── run.py              # 统一启动脚本
├── install.py          # 自动安装脚本
├── build.py            # 打包构建脚本
├── requirements.txt    # Python依赖
├── config.json         # 配置文件（自动生成）
├── templates/          # Web模板
│   ├── index.html      # 首页模板
│   └── album.html      # 相册详情页模板
└── downloaded/         # 图片存储目录（自动创建）
```

## 系统要求

- **Python**: 3.7或更高版本
- **操作系统**: Windows 7+, macOS 10.12+, Linux
- **内存**: 建议2GB以上
- **存储**: 根据下载内容而定
- **网络**: 需要互联网连接进行爬取

## 常见问题

### Q: GUI界面无法启动？
A: 请确保安装了tkinter：
- Ubuntu/Debian: `sudo apt-get install python3-tk`
- CentOS/RHEL: `sudo yum install tkinter`
- Windows/macOS: 通常已包含在Python中

### Q: 爬虫下载失败？
A: 检查网络连接和目标网站状态，可以调整重试次数和延迟时间

### Q: Web服务无法访问？
A: 检查防火墙设置，确保端口未被占用

### Q: 打包后的应用无法运行？
A: 确保目标机器的操作系统架构匹配，检查是否缺少系统依赖

## 开发说明

### 添加新的爬取源
1. 修改 `config.json` 中的 `categories` 配置
2. 根据需要调整 `main.py` 中的解析逻辑

### 自定义界面
1. 修改 `templates/` 目录下的HTML模板
2. 调整 `app.py` 中的路由和逻辑

### 扩展功能
1. 在 `gui.py` 中添加新的界面组件
2. 在 `config.py` 中添加新的配置选项

## 爬虫功能

### 工作原理

- **目标网站**：写真网站的内容获取
- **数据获取**：使用requests库进行HTTP请求，beautifulsoup4解析HTML内容
- **处理流程**：
  1. 解析目标页面获取相册信息
  2. 提取图片URL和相关元数据
  3. 下载并保存图片到本地

### 主要功能

- **并发下载**：
  - 多线程并发下载提升效率
  - 智能任务队列管理
  - 动态调整并发数

- **图片处理**：
  - 自动生成缩略图

- **数据管理**：
  - 相册信息本地存储
  - 增量更新机制
  - 重复图片检测

### 性能优化

- **请求优化**：
  - 动态调整请求间隔
  - 自动重试机制
  - 代理IP支持

- **资源控制**：
  - 内存使用优化
  - 磁盘空间管理
  - 带宽占用控制

