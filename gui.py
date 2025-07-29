import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import webbrowser
import subprocess
import sys
import os
from pathlib import Path
import time
import json

from config import app_config
import main
import app

class PicSpiderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PicSpider 写真爬取展示系统")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # 设置窗口图标（如果有的话）
        try:
            # 可以添加图标文件
            pass
        except:
            pass

        # 创建主界面
        self.create_widgets()

        # Flask服务器进程
        self.flask_process = None
        self.is_server_running = False

        # 爬虫线程
        self.crawler_thread = None
        self.is_crawling = False

    def create_widgets(self):
        """创建GUI组件"""
        # 创建笔记本控件（标签页）
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 主页标签
        self.create_main_tab(notebook)

        # 爬虫配置标签
        self.create_crawler_tab(notebook)

        # 服务器配置标签
        self.create_server_tab(notebook)

        # 日志标签
        self.create_log_tab(notebook)

    def create_main_tab(self, notebook):
        """创建主页标签"""
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="主页")

        # 标题
        title_label = ttk.Label(main_frame, text="PicSpider 写真爬取展示系统",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        # 描述
        desc_text = """
这是一个优雅的写真相册展示系统，提供了简洁美观的界面来浏览和管理图片相册。

主要功能：
• 相册展示：以网格布局展示所有相册，支持缩略图预览
• 响应式设计：完美适配各种屏幕尺寸
• 搜索功能：支持按相册名称搜索
• 分页浏览：相册列表支持分页显示
• 图片预览：支持查看相册内的完整图片内容
        """
        desc_label = ttk.Label(main_frame, text=desc_text, justify=tk.LEFT)
        desc_label.pack(pady=10, padx=20)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)

        # 启动爬虫按钮
        self.start_crawler_btn = ttk.Button(button_frame, text="启动爬虫",
                                           command=self.start_crawler, width=15)
        self.start_crawler_btn.pack(side=tk.LEFT, padx=10)

        # 停止爬虫按钮
        self.stop_crawler_btn = ttk.Button(button_frame, text="停止爬虫",
                                          command=self.stop_crawler, width=15, state=tk.DISABLED)
        self.stop_crawler_btn.pack(side=tk.LEFT, padx=10)

        # 启动Web服务器按钮
        self.start_server_btn = ttk.Button(button_frame, text="启动Web服务",
                                          command=self.start_server, width=15)
        self.start_server_btn.pack(side=tk.LEFT, padx=10)

        # 停止Web服务器按钮
        self.stop_server_btn = ttk.Button(button_frame, text="停止Web服务",
                                         command=self.stop_server, width=15, state=tk.DISABLED)
        self.stop_server_btn.pack(side=tk.LEFT, padx=10)

        # 打开浏览器按钮
        self.open_browser_btn = ttk.Button(button_frame, text="打开浏览器",
                                          command=self.open_browser, width=15, state=tk.DISABLED)
        self.open_browser_btn.pack(side=tk.LEFT, padx=10)

        # 状态标签
        self.status_label = ttk.Label(main_frame, text="就绪", foreground="green")
        self.status_label.pack(pady=10)

    def create_crawler_tab(self, notebook):
        """创建爬虫配置标签"""
        crawler_frame = ttk.Frame(notebook)
        notebook.add(crawler_frame, text="爬虫配置")

        # 配置框架
        config_frame = ttk.LabelFrame(crawler_frame, text="爬虫设置", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=10)

        # 下载目录
        ttk.Label(config_frame, text="下载目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.photo_dir_var = tk.StringVar(value=app_config.get("photo_dir", "downloaded"))
        photo_dir_frame = ttk.Frame(config_frame)
        photo_dir_frame.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        ttk.Entry(photo_dir_frame, textvariable=self.photo_dir_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(photo_dir_frame, text="浏览", command=self.browse_photo_dir, width=8).pack(side=tk.RIGHT, padx=(5, 0))

        # 最大工作线程
        ttk.Label(config_frame, text="最大工作线程:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.max_workers_var = tk.IntVar(value=app_config.get("max_workers", 5))
        ttk.Spinbox(config_frame, from_=1, to=10, textvariable=self.max_workers_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # 下载延迟
        ttk.Label(config_frame, text="下载延迟(秒):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.download_delay_var = tk.DoubleVar(value=app_config.get("download_delay", 0.5))
        ttk.Spinbox(config_frame, from_=0.1, to=5.0, increment=0.1, textvariable=self.download_delay_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # 重试次数
        ttk.Label(config_frame, text="重试次数:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.retry_count_var = tk.IntVar(value=app_config.get("retry_count", 3))
        ttk.Spinbox(config_frame, from_=1, to=10, textvariable=self.retry_count_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # 配置网格列权重
        config_frame.columnconfigure(1, weight=1)

        # 保存配置按钮
        ttk.Button(config_frame, text="保存配置", command=self.save_crawler_config).grid(row=4, column=1, sticky=tk.E, pady=10)

    def create_server_tab(self, notebook):
        """创建服务器配置标签"""
        server_frame = ttk.Frame(notebook)
        notebook.add(server_frame, text="服务器配置")

        # 配置框架
        config_frame = ttk.LabelFrame(server_frame, text="Web服务器设置", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=10)

        # 主机地址
        ttk.Label(config_frame, text="主机地址:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.flask_host_var = tk.StringVar(value=app_config.get("flask_host", "127.0.0.1"))
        ttk.Entry(config_frame, textvariable=self.flask_host_var, width=20).grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # 端口
        ttk.Label(config_frame, text="端口:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.flask_port_var = tk.IntVar(value=app_config.get("flask_port", 5000))
        ttk.Spinbox(config_frame, from_=1000, to=65535, textvariable=self.flask_port_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # 每页相册数
        ttk.Label(config_frame, text="每页相册数:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.albums_per_page_var = tk.IntVar(value=app_config.get("albums_per_page", 12))
        ttk.Spinbox(config_frame, from_=6, to=50, textvariable=self.albums_per_page_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # 调试模式
        self.flask_debug_var = tk.BooleanVar(value=app_config.get("flask_debug", False))
        ttk.Checkbutton(config_frame, text="调试模式", variable=self.flask_debug_var).grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # 保存配置按钮
        ttk.Button(config_frame, text="保存配置", command=self.save_server_config).grid(row=4, column=1, sticky=tk.E, pady=10)

    def create_log_tab(self, notebook):
        """创建日志标签"""
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="日志")

        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=25)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 清除日志按钮
        ttk.Button(log_frame, text="清除日志", command=self.clear_log).pack(pady=5)

    def log_message(self, message):
        """添加日志消息"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        """清除日志"""
        self.log_text.delete(1.0, tk.END)

    def browse_photo_dir(self):
        """浏览选择下载目录"""
        directory = filedialog.askdirectory(initialdir=self.photo_dir_var.get())
        if directory:
            self.photo_dir_var.set(directory)

    def save_crawler_config(self):
        """保存爬虫配置"""
        try:
            app_config.set("photo_dir", self.photo_dir_var.get())
            app.PHOTO_DIR = app_config.get_photo_dir()
            app_config.set("max_workers", self.max_workers_var.get())
            app_config.set("download_delay", self.download_delay_var.get())
            app_config.set("retry_count", self.retry_count_var.get())
            messagebox.showinfo("成功", "爬虫配置已保存")
            self.log_message("爬虫配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")

    def save_server_config(self):
        """保存服务器配置"""
        try:
            app_config.set("flask_host", self.flask_host_var.get())
            app_config.set("flask_port", self.flask_port_var.get())
            app_config.set("albums_per_page", self.albums_per_page_var.get())
            app.ALBUMS_PER_PAGE = self.albums_per_page_var.get()
            app_config.set("flask_debug", self.flask_debug_var.get())
            messagebox.showinfo("成功", "服务器配置已保存")
            self.log_message("服务器配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")

    def start_crawler(self):
        """启动爬虫"""
        if self.is_crawling:
            return

        self.is_crawling = True
        self.start_crawler_btn.config(state=tk.DISABLED)
        self.stop_crawler_btn.config(state=tk.NORMAL)
        self.status_label.config(text="爬虫运行中...", foreground="blue")

        # 在新线程中运行爬虫
        self.crawler_thread = threading.Thread(target=self.run_crawler, daemon=True)
        self.crawler_thread.start()

        self.log_message("爬虫已启动")

    def run_crawler(self):
        """运行爬虫的线程函数"""
        try:
            # 调用main.py的爬虫功能
            main.start_crawler(log_callback=self.log_message)
        except Exception as e:
            self.log_message(f"爬虫运行出错: {e}")
        finally:
            self.is_crawling = False
            self.root.after(0, self.crawler_finished)

    def crawler_finished(self):
        """爬虫完成后的UI更新"""
        self.start_crawler_btn.config(state=tk.NORMAL)
        self.stop_crawler_btn.config(state=tk.DISABLED)
        self.status_label.config(text="爬虫已完成", foreground="green")
        self.log_message("爬虫已完成")

    def stop_crawler(self):
        """停止爬虫"""
        if not self.is_crawling:
            return

        # 调用main.py的停止函数
        main.stop_crawler_func()
        self.is_crawling = False
        self.start_crawler_btn.config(state=tk.NORMAL)
        self.stop_crawler_btn.config(state=tk.DISABLED)
        self.status_label.config(text="爬虫已停止", foreground="orange")
        self.log_message("爬虫已停止")

    def start_server(self):
        """启动Web服务器"""
        if self.is_server_running:
            return

        try:
            # 在新线程中启动Flask服务器
            self.server_thread = threading.Thread(target=self.run_server, daemon=True)
            self.server_thread.start()

            self.is_server_running = True
            self.start_server_btn.config(state=tk.DISABLED)
            self.stop_server_btn.config(state=tk.NORMAL)
            self.open_browser_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Web服务运行中...", foreground="blue")
            self.log_message("Web服务器已启动")

        except Exception as e:
            messagebox.showerror("错误", f"启动Web服务器失败: {e}")
            self.log_message(f"启动Web服务器失败: {e}")

    def run_server(self):
        """运行Web服务器的线程函数"""
        try:
            host = self.flask_host_var.get()
            port = self.flask_port_var.get()
            debug = self.flask_debug_var.get()

            # 调用app.py的运行函数
            app.run_app(host=host, port=port, debug=debug)

        except Exception as e:
            self.log_message(f"Web服务器运行出错: {e}")

    def stop_server(self):
        """停止Web服务器"""
        # 注意：Flask开发服务器不容易优雅地停止，这里只是更新UI状态
        self.is_server_running = False
        self.start_server_btn.config(state=tk.NORMAL)
        self.stop_server_btn.config(state=tk.DISABLED)
        self.open_browser_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Web服务已停止", foreground="orange")
        self.log_message("Web服务器已停止")

    def open_browser(self):
        """打开浏览器"""
        if not self.is_server_running:
            messagebox.showwarning("警告", "Web服务器未运行")
            return

        url = f"http://{self.flask_host_var.get()}:{self.flask_port_var.get()}"
        webbrowser.open(url)
        self.log_message(f"已打开浏览器: {url}")

def gui_main():
    root = tk.Tk()
    app = PicSpiderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    gui_main()
