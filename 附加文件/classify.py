from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import datetime
import shutil
import os


proxies = {'http': None, 'https': None}
output_file = os.path.join(os.getcwd(), '数据文件/uid.txt')
keywords_url = 'https://raw.kkgithub.com/ayyayyayy2002/BiliBiliVideoAutoReport/main/附加文件/云端文件/keyword.txt'
keywords_filename = '数据文件/keyword.txt'
cloud_whitelist_filename = '云端文件/whitelist.txt'
blacklist_url = 'https://raw.kkgithub.com/ayyayyayy2002/BiliBiliVideoAutoReport/main/附加文件/云端文件/blacklist.txt'
blacklist_filename = '数据文件/blacklist.txt'
base_dir = os.path.dirname(os.path.abspath(__file__))
user_data_dir = os.path.join(base_dir,  'User Data')
chrome_binary_path = os.path.join(base_dir,  'chrome-win', 'chrome.exe')
chrome_driver_path = os.path.join(base_dir, '数据文件','chromedriver.exe')
script_clear = os.path.join(base_dir, '页面脚本', '清空列表（纯JS代码）.js')
log_directory = os.path.join(base_dir,  '运行记录')
os.makedirs(log_directory, exist_ok=True)
if os.path.exists(output_file):
    os.remove(output_file)
else:
    print(f"文件 {output_file} 不存在，无需删除。")


def sort_file_contents(file_path):
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 去除每行末尾的换行符，并将内容转换为整数，仅处理非空行
    numbers = []
    for line in lines:
        stripped_line = line.strip()
        if stripped_line:  # 确保不是空行
            try:
                numbers.append(int(stripped_line))
            except ValueError:
                print(f"警告: '{stripped_line}' 不是有效的整数，已跳过。")

    # 排序
    sorted_numbers = sorted(numbers)

    # 将排序后的结果写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        for number in sorted_numbers:
            file.write(f"{number}\n")


# 使用示例



def fetch_keywords():  # 定义获取关键词的函数

    try:
        response = requests.get(keywords_url, proxies=proxies, timeout=(5, 10))
        if response.status_code == 200:
            with open(keywords_filename, 'wb') as f_out:
                f_out.write(response.content)
            print(f"成功下载关键词文件并保存为keyword")
        else:
            print(f"无法访问URL，状态码：{response.status_code}")
            return load_local_keywords(keywords_filename)  # 返回本地关键词
    except requests.exceptions.RequestException as e:
        print(f"下载关键词文件时发生请求异常：{e}")
        return load_local_keywords(keywords_filename)  # 返回本地关键词

    return load_local_keywords(keywords_filename)


def get_watchlater(): #将“稍后再看”里面的UID加入举报列表
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f'--user-data-dir={user_data_dir}')  # 设置用户数据目录
    options.binary_location = chrome_binary_path  # 指定 Chrome 浏览器的可执行文件路径
    options.add_argument('--proxy-server="direct://"')
    options.add_argument('--proxy-bypass-list=*')
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-sync")
    options.add_argument("disable-cache")  # 禁用缓存
    options.add_argument("--headless")
    options.add_argument('log-level=3')
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)  # 启动 Chrome 浏览器
    # driver.set_window_size(1000, 700)  # 设置浏览器窗口大小（宽度, 高度）
    # driver.set_window_position(-850, 775)  # 设置浏览器窗口位置（x, y）
    # driver.set_window_position(-850, 1355)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    url = f"https://www.bilibili.com/watchlater/?spm_id_from=333.1007.0.0#/list"
    driver.get(url)
    elements = driver.find_elements(By.XPATH, "//a[@class='user']")
    watchlaters = []
    for element in elements:
        href = element.get_attribute("href")  # 获取 href 属性
        watchlater = href.split("/")[-1]  # 从链接中提取 UID
        watchlaters.append(watchlater)
    with open(script_clear, "r", encoding="utf-8") as file:
        clear = file.read()
    driver.execute_script(clear)
    with open(cloud_whitelist_filename, 'a') as file:  # 以追加方式打开文件
        for watchlater in watchlaters:
            print(watchlater)
            file.write(f"\n{watchlater}")
    unique_uids.update(watchlaters)

    driver.quit()



def load_local_keywords(filename):  # 定义从本地文件加载关键词的函数
    keywords = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith('#'):  # 排除空行和以“#”开头的行
                    keywords.append(stripped_line)
    else:
        print(f"本地关键词文件不存在。")

    return keywords


def search_and_extract_uid(keyword):  # 定义搜索函数
    base_url = 'https://search.bilibili.com/video?'
    search_params_list = [
        {
            'keyword': keyword,
            'from_source': 'video_tag',
        },
        {
            'keyword': keyword,
            'from_source': 'video_tag',
            'page': '2',
            'o': '30'
        },
        {
            'keyword': keyword,
            'from_source': 'video_tag',
            'order': 'pubdate'
        }
    ]

    for search_params in search_params_list:
        search_url = base_url + urlencode(search_params)
        print(search_url)

        try:
            # 添加头部信息
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/91.0.4472.124 Safari/537.36',
            }
            response = requests.get(search_url, headers=headers, proxies=proxies, timeout=(5, 10))
            response.raise_for_status()  # 检查请求是否成功
            soup = BeautifulSoup(response.text, 'html.parser')
            uid_list = []
            count = 0  # 计数器，用于限制获取的UID数量
            for link in soup.select('.bili-video-card .bili-video-card__info--owner'):
                if count >= 30:
                    break
                href = link['href']
                uid = href.split('/')[-1]  # 获取链接中最后的数字部分作为UID
                uid_list.append(uid)
                count += 1
            process_uid_list(keyword, uid_list)
        except requests.exceptions.RequestException as e:
            print(f"关键词 \"{keyword}\" 搜索页面请求失败：", e)


def process_uid_list(keyword, uid_list):  # 定义处理UID列表的函数（追加写入同一文件）
    print(f" \"{keyword}\" UID：\n", uid_list)

    # 将UID列表追加写入文件
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(f" \"{keyword}\" UID：\n")
        for uid in uid_list:
            f.write(uid + '\n')
        f.write('\n')  # 添加空行分隔每个关键词的UID列表


while True:
    unique_uids = set()  # 使用集合存储唯一的 UID
    keywords = fetch_keywords()  # 使用fetch_keywords函数替代原有的keywords定义

    for keyword in keywords:  # 遍历关键词列表，进行搜索和处理
        search_and_extract_uid(keyword)
    print('读取当前文件中所有的 UID，并添加到集合中去重')
    with open(output_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            uid = line.strip()
            if uid.isdigit():  # 假设 UID 是数字格式
                unique_uids.add(uid)

    try:
        # 获取当前时间并格式化
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = os.path.join(log_directory, f'{timestamp}.txt')

        shutil.copy(output_file, backup_filename)
        print(f"成功保存备份：{backup_filename}")
    except IOError as e:
        print(f"复制保存备份时发生错误：{e}")





    get_watchlater()

    sort_file_contents(cloud_whitelist_filename)



    try:
        response = requests.get(blacklist_url, proxies=proxies, timeout=(5, 10))
        if response.status_code == 200:
            with open(blacklist_filename, 'wb') as f_out:
                f_out.write(response.content)
            print(f"成功下载文件并保存为blacklist")
        else:
            print(f"无法访问URL，状态码：{response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"下载文件时发生请求异常：{e}")
    except IOError as e:
        print(f"文件操作发生错误：{e}")
    except Exception as e:
        print(f"发生未知错误：{e}")
    print('继续执行其他操作，不受文件下载错误的影响')
    exclude_uids = set()

    with open(blacklist_filename, 'r', encoding='utf-8') as exclude_file:
        exclude_lines = exclude_file.readlines()
        for line in exclude_lines:
            exclude_uid = line.strip()
            if exclude_uid.isdigit():  # 假设 UID 是数字格式
                exclude_uids.add(exclude_uid)
    print('从 unique_uids 中移除在 exclude_uids 中存在的 UID')
    unique_uids -= exclude_uids
    print('将唯一的 UID 列表按格式写入文件')

    with open(output_file, 'w', encoding='utf-8') as f:
        for uid in unique_uids:
            f.write(uid + '\n')
    print('关键词搜索和UID全部处理完成')
    break





proxies = {'http': None, 'https': None}
categories = {
    "色情游戏": {
        "关键词": ["SLG", "ACT", "RPG", "黄油","ADV", "GAL","动态","汉化","步兵","无码"],
        "权重": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    },
    "色情同人": {
        "关键词": ["AKT", "同人", "大佬", "vicineko", "新作"],
        "权重": [1, 1, 1, 1, 1]
    },

}

base_dir = os.path.dirname(os.path.abspath(__file__))
uid_path = os.path.join(base_dir, '数据文件','uid.txt')

with open(uid_path, 'r', encoding='utf-8') as f:
    uids = f.readlines()

for uid in uids:
    uid = uid.strip()  # 去掉换行符和空格
    if uid:  # 确保 uid 非空
        search_url = f'https://api.bilibili.com/x/series/recArchivesByKeywords?mid={uid}&keywords=&ps=100'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        try:
            response = requests.get(search_url, headers=headers, proxies=proxies, timeout=(5, 10))
            response.raise_for_status()
            data = response.json()

            if data['code'] == 0 and 'data' in data and 'archives' in data['data']:
                titles = [archive['title'] for archive in data['data']['archives']]
                titles_str = ', '.join(titles)
                n = len(titles)


                # 调用标记函数

                titles = titles_str.split('|||')  # 这里使用 '|||' 作为分隔符
                if len(titles) > n:
                    titles = titles[:n]  # 只取前n个标题

                scores = {category: 0 for category in categories}

                # 统计每个类别的得分
                total_score = 0

                for title in titles:
                    for category, info in categories.items():
                        keywords = info["关键词"]
                        points = info["权重"]

                        for keyword, point in zip(keywords, points):
                            count = title.count(keyword)
                            if count > 0:
                                category_score = count * point
                                scores[category] += category_score
                                total_score += category_score

                # 对账号进行分类

                labels = []
                for category, score in scores.items():
                    if total_score > 0 and (score / n) > 0.75:
                        labels.append(category)
                        print(f'{uid}:{labels}')
                        with open(cloud_whitelist_filename, 'a', encoding='utf-8') as f:
                            f.write(f"\n{uid}")






        except Exception as e:
            print(f"Error processing UID {uid}: {e}")

        # 在处理全部 uid 后

with open(cloud_whitelist_filename, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 去除每行末尾的换行符，并将内容转换为整数，仅处理非空行
numbers = []
for line in lines:
    stripped_line = line.strip()
    if stripped_line:  # 确保不是空行
        try:
            numbers.append(int(stripped_line))
        except ValueError:
            print(f"警告: '{stripped_line}' 不是有效的整数，已跳过。")

# 排序
sorted_numbers = sorted(numbers)

# 将排序后的结果写回文件
with open(cloud_whitelist_filename, 'w', encoding='utf-8') as file:
    for number in sorted_numbers:
        file.write(f"{number}\n")

















