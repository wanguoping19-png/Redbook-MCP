from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import base64
from datetime import datetime
from setting import CHROME_PROFILE,DRIVER_PATH,QR_IMAGES
# 指定ChromeDriver路径
chrome_driver_path = r"{}".format(DRIVER_PATH)
# 创建 ChromeOptions
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
# 或
options.add_argument('--width=1920')
options.add_argument('--height=1080')
# 浏览器状态持久化
options.add_argument(f"--user-data-dir={CHROME_PROFILE}")
# 🔥 关键：启用无头模式（不显示浏览器窗口）
options.add_argument('--headless')
# 在无头模式下给浏览器加请求头
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
# 使用 Service 类来指定驱动路径
service = Service(executable_path=chrome_driver_path)

def qrcode_login():
    driver = webdriver.Chrome(service=service,options=options)
    # 初始化 WebDriver
    driver.get('https://www.xiaohongshu.com/explore')
    time.sleep(3)
    resp_messages = {
        "code":200,
        "image_url":"",
        "message":""
    }
    try:
        img_element = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH, "//div/img[@class='qrcode-img']")))
        # 定位 img 元素（你可以根据 class、tag、xpath 等方式定位）
        img_element = driver.find_element(By.XPATH, "//div/img[@class='qrcode-img']")

        # 获取 src 属性
        src = img_element.get_attribute("src")

        # 检查是否是 data URL
        if src.startswith("data:image"):
            # 分离出 Base64 部分（假设格式为 data:image/xxx;base64,<data>）
            header, encoded = src.split(",", 1)

            # 解码 Base64 数据
            image_data = base64.b64decode(encoded)
            image_name = f"登陆二维码{datetime.now()}.png"
            # 保存为文件
            with open(f"{QR_IMAGES}/{image_name}", "wb") as f:
                f.write(image_data)
            print("图片已保存为{}".format(image_name))
            # 将图片上传到在线图床
            # url_data = up_image.upload_image(image_name)
            # resp_messages["image_url"] = url_data["data"]["url"]
            resp_messages["message"] = "登陆二维码上传成功"
            resp_messages["driver"] = driver
            # 启动后台线程关闭浏览器，不阻塞return
            return resp_messages
        else:
            resp_messages["code"] = 201
            resp_messages["message"] = "获取二维码格式有问题"
            resp_messages["driver"] = driver
            return resp_messages
    except Exception as e:
        resp_messages["code"] = 400
        resp_messages["message"] = "二维码获取失败或已经登陆,{}".format(e)
        resp_messages["driver"] = driver
        return resp_messages

if __name__ == '__main__':
    # resp_messages = qrcode_login()
    # print(resp_messages)
    pass
