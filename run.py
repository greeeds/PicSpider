#!/usr/bin/env python3
"""
PicSpider 启动脚本
可以选择运行GUI界面或命令行模式
"""

import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="PicSpider 写真爬取展示系统")
    parser.add_argument("--mode", choices=["gui", "crawler", "server"], 
                       default="gui", help="运行模式 (默认: gui)")
    parser.add_argument("--host", default="127.0.0.1", help="Web服务器主机地址")
    parser.add_argument("--port", type=int, default=5000, help="Web服务器端口")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    if args.mode == "gui":
        # 启动GUI界面
        print("启动GUI界面...")
        from gui import main as gui_main
        gui_main()
        
    elif args.mode == "crawler":
        # 只运行爬虫
        print("启动爬虫...")
        from main import start_crawler
        start_crawler()
        
    elif args.mode == "server":
        # 只运行Web服务器
        print(f"启动Web服务器: http://{args.host}:{args.port}")
        from app import run_app
        run_app(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()
