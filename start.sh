#!/bin/bash

echo ""
echo "========================================"
echo "  PicSpider 写真爬取展示系统"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "错误: 未找到Python，请先安装Python 3.7或更高版本"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# 检查Python版本
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.7"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "错误: Python版本过低，需要3.7或更高版本，当前版本: $PYTHON_VERSION"
    exit 1
fi

# 检查是否首次运行
if [ ! -f "config.json" ]; then
    echo "检测到首次运行，正在安装依赖..."
    $PYTHON_CMD install.py
    if [ $? -ne 0 ]; then
        echo "安装失败，请检查网络连接或手动安装依赖"
        exit 1
    fi
fi

# 启动应用
echo "启动PicSpider..."
$PYTHON_CMD run.py

echo "按任意键退出..."
read -n 1
