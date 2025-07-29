import os
import math
import sys
from pathlib import Path
from flask import Flask, render_template, url_for, send_from_directory, abort, request

# 导入配置
from config import app_config

# 获取模板和静态文件目录
template_dir = app_config.get_templates_dir()
static_dir = app_config.get_static_dir()

# 调试信息
print(f"Template directory: {template_dir}")
print(f"Static directory: {static_dir}")
print(f"Template directory exists: {os.path.exists(template_dir)}")
if static_dir:
    print(f"Static directory exists: {os.path.exists(static_dir)}")

# 检查模板文件是否存在
index_template = os.path.join(template_dir, 'index.html')
album_template = os.path.join(template_dir, 'album.html')
print(f"index.html exists: {os.path.exists(index_template)}")
print(f"album.html exists: {os.path.exists(album_template)}")

# 如果模板目录不存在，尝试使用当前目录下的templates
if not os.path.exists(template_dir):
    fallback_template_dir = os.path.join(os.getcwd(), 'templates')
    if os.path.exists(fallback_template_dir):
        print(f"Using fallback template directory: {fallback_template_dir}")
        template_dir = fallback_template_dir

# 创建Flask应用，指定模板和静态文件目录
if static_dir and os.path.exists(static_dir):
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
else:
    app = Flask(__name__, template_folder=template_dir)

# 配置Flask应用
app.config['SERVER_NAME'] = None  # 允许在任何主机上运行
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'

# --- 配置 ---
PHOTO_DIR = app_config.get_photo_dir()
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALBUMS_PER_PAGE = app_config.get("albums_per_page", 12)

# --- 内存缓存 ---
# 使用一个字典来缓存相册名 -> 缩略图文件名的映射
# 注意：这个缓存会在 Flask 服务器重启后清空
thumbnail_cache = {}
# 可以添加一个变量来控制是否强制刷新缓存（例如用于调试）
force_refresh_cache = False # 设置为 True 可以临时禁用缓存

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_first_image(album_path, album_name): # 传入 album_name 用于缓存键
    """获取缩略图，优先从缓存读取"""
    global thumbnail_cache, force_refresh_cache

    # 如果强制刷新或缓存中没有，则查找
    if force_refresh_cache or album_name not in thumbnail_cache:
        thumbnail_filename = None # 重置/初始化
        try:
            files = sorted(os.listdir(album_path))
            for filename in files:
                file_path = os.path.join(album_path, filename)
                if os.path.isfile(file_path) and allowed_file(filename):
                    thumbnail_filename = filename
                    break # 找到第一个就停止
        except OSError as e:
            print(f"警告：读取相册 {album_path} 时出错以获取缩略图：{e}")
        # 无论是否找到，都存入缓存（存入 None 表示查找过但没有）
        thumbnail_cache[album_name] = thumbnail_filename
        print(f"缓存更新：'{album_name}' -> {thumbnail_filename}") # 调试信息
        return thumbnail_filename
    else:
        # 从缓存读取
        # print(f"从缓存读取：'{album_name}'") # 调试信息
        return thumbnail_cache[album_name]

# --- 路由 ---

@app.route('/')
def index():
    global thumbnail_cache, force_refresh_cache
    if force_refresh_cache: # 如果设置了强制刷新，用完一次就关掉
        thumbnail_cache = {} # 清空缓存
        force_refresh_cache = False
        print("缓存已强制清空。")

    search_query = request.args.get('q', None)
    try:
        page = request.args.get('page', 1, type=int)
        if page < 1: page = 1
    except ValueError:
        page = 1

    all_albums_data = []
    if not os.path.isdir(PHOTO_DIR):
        print(f"错误：找不到目录 {PHOTO_DIR}")
        os.makedirs(PHOTO_DIR)
        # return f"错误：配置的图片目录不存在: {PHOTO_DIR}", 500

    try:
        all_items = sorted(os.listdir(PHOTO_DIR))
        for item in all_items:
            item_path = os.path.join(PHOTO_DIR, item)
            if os.path.isdir(item_path):
                if search_query and search_query.lower() not in item.lower():
                    continue

                # 从缓存或文件系统获取缩略图
                thumbnail_filename = get_first_image(item_path, item) # 传入 item 作为缓存键

                all_albums_data.append({
                    'name': item,
                    'thumbnail': thumbnail_filename
                })
    except OSError as e:
        print(f"错误：访问目录时出错 {PHOTO_DIR} - {e}")
        return "错误：读取相册列表时出错。", 500

    # --- 分页逻辑 (保持不变) ---
    total_albums = len(all_albums_data)
    total_pages = math.ceil(total_albums / ALBUMS_PER_PAGE)
    start_index = (page - 1) * ALBUMS_PER_PAGE
    end_index = start_index + ALBUMS_PER_PAGE
    albums_on_page = all_albums_data[start_index:end_index]
    pagination = {
        'page': page, 'total_pages': total_pages, 'has_prev': page > 1,
        'has_next': page < total_pages, 'prev_num': page - 1, 'next_num': page + 1
    }

    return render_template('index.html',
                           albums=albums_on_page,
                           pagination=pagination,
                           search_query=search_query)

# view_album 和 get_image 函数保持不变
@app.route('/album/<album_name>')
def view_album(album_name):
  album_path = os.path.join(PHOTO_DIR, album_name)
  if not os.path.isdir(album_path) or \
     not os.path.abspath(album_path).startswith(os.path.abspath(PHOTO_DIR)):
    print(f"错误：尝试访问无效或不存在的相册路径 {album_path}")
    abort(404)
  images = []
  try:
    for filename in os.listdir(album_path):
      file_path = os.path.join(album_path, filename)
      if os.path.isfile(file_path) and allowed_file(filename):
        images.append(filename)
    images.sort()
  except OSError as e:
    print(f"错误：访问相册 {album_path} 时出错 - {e}")
    return f"错误：读取相册 {album_name} 时出错。", 500
  # 注意：这里传递给 album.html 的 images 列表没有变化
  return render_template('album.html', album_name=album_name, images=images)


@app.route('/images/<album_name>/<filename>')
def get_image(album_name, filename):
  album_path_check = os.path.join(PHOTO_DIR, album_name)
  if not os.path.isdir(album_path_check) or \
     not os.path.abspath(album_path_check).startswith(os.path.abspath(PHOTO_DIR)):
       print(f"警告：尝试从无效或不存在的相册路径获取图片 {album_path_check}")
       abort(404)
  try:
      return send_from_directory(album_path_check, filename)
  except FileNotFoundError:
      print(f"警告：在相册 {album_name} 中未找到文件 {filename}")
      abort(404)

def run_app(host=None, port=None, debug=None):
    """运行Flask应用"""
    host = host or app_config.get("flask_host", "127.0.0.1")
    port = port or app_config.get("flask_port", 5000)
    debug = debug if debug is not None else app_config.get("flask_debug", False)

    print(f"启动Web服务器: http://{host}:{port}")
    print(f"图片目录: {PHOTO_DIR}")
    print(f"模板目录: {template_dir}")

    app.run(debug=debug, host=host, port=port, use_reloader=False)

if __name__ == '__main__':
    run_app()
