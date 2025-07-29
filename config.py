import os
import sys
import json
from pathlib import Path

class Config:
    """配置管理类"""
    
    def __init__(self):
        # 获取应用程序目录
        if getattr(sys, 'frozen', False):
            # 打包后的环境
            self.app_dir = Path(sys.executable).parent
            self.is_frozen = True
        else:
            # 开发环境
            self.app_dir = Path(__file__).parent
            self.is_frozen = False
            
        # 配置文件路径
        self.config_file = self.app_dir / "config.json"
        
        # 默认配置
        self.default_config = {
            "photo_dir": "downloaded",
            "albums_per_page": 12,
            "flask_host": "127.0.0.1",
            "flask_port": 5000,
            "flask_debug": False,
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
        
        # 加载配置
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置和用户配置
                merged_config = self.default_config.copy()
                merged_config.update(config)
                return merged_config
            else:
                # 创建默认配置文件
                self.save_config(self.default_config)
                return self.default_config.copy()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return self.default_config.copy()
    
    def save_config(self, config=None):
        """保存配置文件"""
        try:
            config_to_save = config or self.config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置值"""
        self.config[key] = value
        return self.save_config()
    
    def get_photo_dir(self):
        """获取图片目录的绝对路径"""
        photo_dir = self.get("photo_dir", "downloaded")
        if os.path.isabs(photo_dir):
            return photo_dir
        else:
            return str(self.app_dir / photo_dir)
    
    def get_templates_dir(self):
        """获取模板目录路径"""
        if self.is_frozen:
            # 打包后，模板文件在_internal目录中
            return str(self.app_dir / "_internal" / "templates")
        else:
            return str(self.app_dir / "templates")
    
    def get_static_dir(self):
        """获取静态文件目录路径"""
        if self.is_frozen:
            return str(self.app_dir / "_internal" / "static")
        else:
            return str(self.app_dir / "static")

# 全局配置实例
app_config = Config()
