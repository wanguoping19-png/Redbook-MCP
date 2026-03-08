from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import json
from driver_tools import enable_xhr_interception,get_xhr_logs_as_dict

# 指定ChromeDriver路径
chrome_driver_path = r"./static/driver/chromedriver"
# 创建 ChromeOptions
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
# 或
options.add_argument('--width=1920')
options.add_argument('--height=1080')
# 浏览器状态持久化
options.add_argument("--user-data-dir=./chrome_profile")

# 🔥 关键：启用无头模式（不显示浏览器窗口）
options.add_argument('--headless')
# 无头模式配置
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# 启用 CDP
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
# 或者使用新方式（Selenium 4+ 推荐）：
options.add_argument("--enable-logging")
options.add_argument("--log-level=0")

# 使用 Service 类来指定驱动路径
service = Service(executable_path=chrome_driver_path)


def get_login_status():
    # 初始化 WebDriver
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://www.xiaohongshu.com/explore')
    time.sleep(10)
    resp_messages = {
        "code":200,
        "message":""
    }
    # 启用网络监听
    enable_xhr_interception(driver)
    try:
        # 点击头像元素
        img_element = driver.find_element(By.XPATH, "(//li[contains(@class,'user')]/div/a[@title='我'])[1]")
        img_element.click()

        # 等待请求完成（实际项目中可用 WebDriverWait 等更健壮的方式）
        driver.implicitly_wait(10)

        # 获取 XHR 数据
        xhr_dict = get_xhr_logs_as_dict(driver)

        # 打印结果
        for url, data in xhr_dict.items():
            if url == "https://edith.xiaohongshu.com/api/sns/web/v2/user/me":
                print(f"\n{'=' * 60}")
                print(f"URL: {url}")
                print(f"Request Method: {data['request']['method']}")
                print(f"Response Status: {data['response']['status']}")
                print(f"Response Body Preview: {str(json.loads(data['response']['body'])['data'])[:200]}...")
                time.sleep(15)
                driver.quit()
                resp_messages['message'] = json.loads(data['response']['body'])['data']
                return resp_messages
    except NoSuchElementException:
        resp_messages["code"] = 401
        resp_messages["message"] = "未检查到用户登陆信息"
        time.sleep(5)
        driver.quit()
        return resp_messages

if __name__ == '__main__':
    # resp_messages = get_login_status()
    # print(resp_messages)
    pass


