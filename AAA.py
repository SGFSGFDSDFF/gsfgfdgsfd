from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium import webdriver
from src import jy_click
import argparse
import requests
import time
import sys
import os
import re



def get_location(target):
    # 获取元素在屏幕上的位置信息
    location = target.location
    size = target.size
    height = size['height']
    width = size['width']
    left = location['x']
    top = location['y']
    right = left + width
    bottom = top + height
    script = f"return {{'left': {left}, 'top': {top}, 'right': {right}, 'bottom': {bottom}}};"
    rect = driver.execute_script(script)
    left_x = int(rect['left'])
    top_y = int(rect['top'])
    return left_x, top_y
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--username", help="用户名")
parser.add_argument("-p", "--password", help="密码")
args = parser.parse_args()


if args.username and args.password:
    username = args.username
    password = args.password
else:
    username = 'username'
    password = 'password'



proxies = {'http': None, 'https': None}
base_dir = os.path.dirname(os.path.abspath(__file__))
user_data_dir = os.path.join(base_dir, '附加文件', 'User Data')
chrome_binary_path = os.path.join(base_dir, '附加文件', 'chrome-win', 'chrome.exe')
chrome_driver_path = os.path.join(base_dir, '附加文件', '运行数据','chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(f'--user-data-dir={user_data_dir}')  # 设置用户数据目录
options.binary_location = chrome_binary_path  # 指定 Chrome 浏览器的可执行文件路径
options.add_argument('--proxy-server="direct://"')
options.add_argument('--proxy-bypass-list=*')
options.add_argument("--disable-gpu")
if args.password and args.username:
    options.add_argument("--headless")
options.add_argument("--disable-sync")
options.add_argument("disable-cache")#禁用缓存
options.add_argument('log-level=3')
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)  # 启动 Chrome 浏览器
driver.set_window_size(1000, 700)  # 设置浏览器窗口大小（宽度, 高度）
#driver.set_window_position(0, 0)  # 设置浏览器窗口位置（x, y）

url = f"https://space.bilibili.com/"
driver.get(url)
if args.password and args.username:

    input_element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[1]/div[1]/input'))
    )
    input_element.send_keys(username)

    input_element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[1]/div[3]/input'))
    )
    input_element.send_keys(password)

    while True:
        # 点击确认
        WebDriverWait(driver, 20, 1).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[2]/div[2]'))
        ).click()

        # 检查元素是否存在
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@class="geetest_item_wrap"]'))
            )
            print("验证码元素已出现！")
            break  # 如果元素出现则退出循环
        except Exception:
            print("验证码元素未出现，重新点击确认...")

    while True:
        try:
            img = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@class="geetest_item_wrap"]'))
            )
            f = img.get_attribute('style')
            attempt = 0  # 初始化尝试计数
            while ('url("' not in f) and (attempt < 10):
                f = img.get_attribute('style')
                attempt += 1
                time.sleep(0.5)
            print(attempt)
            url = re.search(r'url\("([^"]+?)\?[^"]*"\);', f).group(1)

            content = requests.get(url, proxies=proxies, timeout=(5, 10)).content

            plan = jy_click.JYClick().run(content)

            print(plan)

            a, b = get_location(img)
            lan_x = 306 / 334
            lan_y = 343 / 384

            for crop in plan:
                x1, y1, x2, y2 = crop
                x, y = [(x1 + x2) / 2, (y1 + y2) / 2]
                print(a + x * lan_x, b + y * lan_y, "点击坐标")

                # 执行点击操作
                ActionChains(driver).move_by_offset(a + x * lan_x, b + y * lan_y).click().perform()
                ActionChains(driver).move_by_offset(-(a + x * lan_x),
                                                    -(b + y * lan_y)).perform()  # 恢复鼠标位置
                time.sleep(0.3)

            try:  # 执行点击确认按钮的操作
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_commit_tip'))
                )
                element.click()  # 提交验证码
            except Exception as e:
                print(f"提交验证码时发生错误: {e}")
                refresh_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_refresh'))
                )
                refresh_element.click()  # 点击刷新验证按钮
                print('已点击刷新按钮')

            try:  # 等待 'geetest_item_wrap' 元素消失，表示验证码提交成功
                WebDriverWait(driver, 3).until(
                    EC.invisibility_of_element_located(
                        (By.XPATH, '//*[@class="geetest_item_wrap"]'))
                )
                print("验证码已消失！")
                break




            except Exception as e:
                print(f"验证码验证失败！，错误: {e}")



        except Exception as e:
            print(f"人机验证循环出错，错误: {e}")
            # log_error(f"人机验证循环出错，错误: {e}")
            sys.exit('人机验证循环出错')  # 如果发生异常也退出程序
    driver.quit()

else:
    input("按 Enter 键关闭浏览器...")  # 通过输入来控制浏览器关闭

driver.quit()  # 关闭浏览器

