import requests
from bs4 import BeautifulSoup
import os
import re
import time
from urllib.parse import urljoin
import concurrent.futures
from functools import partial

# 清理非法文件名
def clean_filename(text):
    return re.sub(r'[\\/*?:"<>|]', '_', text).strip()

# 获取所有符合条件的链接
def get_target_links(start_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': ''
    }
    
    try:
        print(f"正在请求: {start_url}")
        response = requests.get(start_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        target_links = []
        for a_tag in soup.select('a.thumbnail-link'):
            # 检查父级div的完整class名称
            parent_div = a_tag.find_parent('div', class_='post_thumb post_thumb_top')
            if parent_div:
                print(f"跳过顶部简略图: {a_tag.get('href', '')}")
                continue
                
            img_tag = a_tag.find('img')
            if img_tag:
                # 检查图片的特定属性组合
                if (img_tag.get('post-id') and 
                    img_tag.get('fifu-featured') == '1' and
                    img_tag.get('width') == '360' and 
                    img_tag.get('height') == '540'):
                    print(f"跳过特定参数图片: {a_tag.get('href', '')}")
                    continue
                    
                href = a_tag.get('href')
                title = img_tag.get('title', '未命名')
                if href:
                    target_links.append({
                        'url': urljoin(start_url, href),
                        'title': title
                    })
        
        print(f"共找到 {len(target_links)} 个有效链接")
        return target_links
    except Exception as e:
        print(f"获取链接失败: {str(e)}")
        return []

# 下载图片
def download_image(url, headers, folder_name, save_dir, retry=5):  # 增加重试次数
    for attempt in range(retry):
        try:
            # 添加SSL验证禁用和更长的超时时间
            response = requests.get(url, headers=headers, timeout=30, verify=False)
            if response.status_code == 200:
                img_data = response.content
                filename = os.path.join(save_dir, folder_name, f'{folder_name}_{url.split("/")[-1]}')
                with open(filename, 'wb') as f:
                    f.write(img_data)
                print(f"[{folder_name}] 下载成功: {url}")
                return True
            else:
                print(f"[{folder_name}] 服务器响应错误 {response.status_code}: {url}")
        except requests.exceptions.SSLError as e:
            print(f"[{folder_name}] SSL错误 (尝试 {attempt + 1}/{retry}): {url}")
            if attempt == retry - 1:
                print(f"[{folder_name}] SSL错误，下载失败: {url}")
                return False
        except Exception as e:
            print(f"[{folder_name}] 下载出错 (尝试 {attempt + 1}/{retry}): {str(e)}")
            if attempt == retry - 1:
                print(f"[{folder_name}] 下载失败: {url}")
                return False
        time.sleep(2 + attempt)  # 递增等待时间

def download_images(page_info, save_dir='downloaded'):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': page_info['url'],
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }
    
    folder_name = clean_filename(page_info['title'])
    folder_path = os.path.join(save_dir, folder_name)
    
    # 检查文件夹是否已存在
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        print(f"文件夹已存在，跳过: {folder_name}")
        return
    
    os.makedirs(folder_path, exist_ok=True)
    
    try:
        # 添加SSL验证禁用
        requests.packages.urllib3.disable_warnings()
        response = requests.get(page_info['url'], headers=headers, timeout=30, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        image_urls = []
        skipped_urls = []
        
        # 第一次遍历：收集所有图片URL
        for img in soup.select('img[src*="/wp-content/uploads/"]'):
            src = img.get('src') or img.get('data-src')
            if src:
                filename = src.split('/')[-1].lower()
                
                # 跳过特定格式的文件名
                if (filename.startswith('0') or  # 跳过以0开头的文件
                    '_0.' in filename or        # 跳过包含_0.的文件
                    filename.endswith('0.jpg') or 
                    filename.endswith('0.jpeg')):
                    print(f"跳过不需要的文件: {filename}")
                    continue
                
                # 只接受类似 NAME_NUMBER.jpg 格式的文件
                if not re.match(r'^[a-zA-Z0-9]+_[1-9]\d*\.(jpg|jpeg|png)$', filename):
                    print(f"跳过格式不匹配的文件: {filename}")
                    continue
                
                image_urls.append({'url': src, 'filename': filename})
                print(f"添加到下载列表: {filename}")
        
        # 提取最终的URL列表
        final_urls = list(set(item['url'] for item in image_urls))
        
        # 使用线程池并行下载
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:  # 增加到5个线程
                download_func = partial(download_image, headers=headers, 
                                     folder_name=folder_name, save_dir=save_dir)
                futures = []
                for url in final_urls:
                    futures.append(executor.submit(download_func, url))
                    time.sleep(0.5)  # 减少下载间隔以提高效率
                
                # 等待所有任务完成
                concurrent.futures.wait(futures)
                
        except KeyboardInterrupt:
            print("\n检测到用户中断，正在安全退出...")
            executor.shutdown(wait=False)
            return
        except Exception as e:
            print(f"下载过程出错: {str(e)}")
            
    except requests.exceptions.SSLError:
        print(f"SSL错误，尝试不验证SSL: {page_info['url']}")
        # 可以在这里添加重试逻辑
    except Exception as e:
        print(f"处理页面失败 {page_info['url']}: {str(e)}")

# 获取下一页
def get_next_page(soup, base_url):
    next_link = soup.select_one('a.next.page-numbers')
    return urljoin(base_url, next_link['href']) if next_link else None

def process_category(base_url, max_pages=200):
    current_url = base_url
    page_count = 0
    
    while current_url and page_count < max_pages:
        print(f"\n正在处理第 {page_count + 1} 页: {current_url}")
        target_pages = get_target_links(current_url)
        
        if not target_pages:
            print("没有找到目标页面，跳过此页")
            break
            
        for page in target_pages:
            print(f"处理: {page['title']} - {page['url']}")
            download_images(page)
            time.sleep(1)
            
        # 获取下一页
        try:
            response = requests.get(current_url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            current_url = get_next_page(soup, current_url)
        except Exception as e:
            print(f"获取下一页失败: {str(e)}")
            break
            
        page_count += 1
        time.sleep(2)

if __name__ == '__main__':
    # 使用字典存储每个分类及其对应的最大页数
    categories = {

        '/gravure/': 287,
        '/japan/' : 274,
        '/korea/': 175,
        '/chinese/': 256,
        '/cosplay/': 115,
    }
    
    for category_url, max_pages in categories.items():
        print(f"\n开始处理分类: {category_url}")
        try:
            process_category(category_url, max_pages)
        except Exception as e:
            print(f"处理分类 {category_url} 时出错: {str(e)}")
