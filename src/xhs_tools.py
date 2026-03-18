import json
import os
import requests
from setting import *
from datetime import datetime
from playwright.async_api import async_playwright, Playwright, BrowserContext
def upload_image(file_name):
     # 将“基础域名”替换为实际的域名
    url = BASE_URL+"/api/v3/upload"
    headers = {
        'Authorization': 'Bearer {}'.format(IMAGE_TOKEN),  # 替换为实际的token
    }
    file_path = f'{QR_IMAGES}/{file_name}'  # 替换为实际文件路径

    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(url, headers=headers, files=files)
    # 输出响应内容和状态码
    print("图片上传:",response.status_code)
    print(response.text)
    return response.json()


def enable_xhr_interception(driver):
    """启用 CDP 网络监听，并设置缓冲区大小以支持 response body"""
    driver.execute_cdp_cmd('Network.enable', {
        'maxTotalBufferSize': 100 * 1024 * 1024,
        'maxResourceBufferSize': 10 * 1024 * 1024,
        'maxPostDataSize': 10 * 1024 * 1024
    })


def get_xhr_logs_as_dict(driver):
    """
    获取自上次调用以来的所有 XHR/Fetch 请求日志，并组织成字典。
    返回格式：
    {
        "https://api.example.com/data": {
            "request": {
                "method": "GET",
                "headers": { ... },
                "postData": "..."  # 如果有
            },
            "response": {
                "status": 200,
                "headers": { ... },
                "body": "{...}"  # str 或 base64（如为二进制）
            }
        },
        ...
    }
    """
    raw_logs = driver.get_log("performance")
    xhr_data = {}

    # 第一步：收集所有 request 和 response 的事件，按 requestId 关联
    request_map = {}
    response_map = {}
    body_map = {}

    for entry in raw_logs:
        try:
            message = json.loads(entry["message"])["message"]
            method = message["method"]

            if method == "Network.requestWillBeSent":
                params = message["params"]
                # 判断是否为 XHR 或 Fetch
                if params.get("type") == "XHR" or params.get("initiator", {}).get("type") == "script":
                    request_id = params["requestId"]
                    request_map[request_id] = {
                        "url": params["request"]["url"],
                        "method": params["request"]["method"],
                        "headers": params["request"].get("headers", {}),
                        "postData": params["request"].get("postData", None)
                    }

            elif method == "Network.responseReceived":
                params = message["params"]
                request_id = params["requestId"]
                if request_id in request_map:  # 只处理我们关心的 XHR
                    response_map[request_id] = {
                        "status": params["response"]["status"],
                        "headers": params["response"].get("headers", {})
                    }

            elif method == "Network.loadingFinished":
                # 尝试获取响应体（必须在 loadingFinished 之后）
                request_id = message["params"]["requestId"]
                if request_id in request_map:
                    try:
                        body_info = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                        body_map[request_id] = body_info["body"] if not body_info["base64Encoded"] else body_info["body"]
                    except Exception as e:
                        # 某些响应（如重定向）可能无法获取 body
                        body_map[request_id] = "[Body not available: " + str(e) + "]"

        except Exception as e:
            # 日志解析出错，跳过
            continue

    # 第二步：合并 request + response + body
    for rid in request_map:
        req = request_map[rid]
        url = req["url"]
        resp = response_map.get(rid, {})
        body = body_map.get(rid, "[No response body captured]")

        xhr_data[url] = {
            "request": {
                "method": req["method"],
                "headers": req["headers"],
                "postData": req["postData"]
            },
            "response": {
                "status": resp.get("status", None),
                "headers": resp.get("headers", {}),
                "body": body
            }
        }

    return xhr_data


def save_url_to_path(url):
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=header, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return None
    # 确保目录存在
    os.makedirs(PUSH_PATH, exist_ok=True)
    filename = f"{int(datetime.now().timestamp() * 1000)}.png"
    filepath = os.path.join(PUSH_PATH, filename)

    with open(filepath, "wb") as f:
        f.write(resp.content)

    print(f"✅ 文件已保存: {filepath}")
    return filepath


def generate_project_structure(path, indent=0):
    """递归生成目录结构图"""
    if not os.path.exists(path):
        print(f"路径 '{path}' 不存在")
        return
    exclude = {'.git', '__pycache__', '.venv', '.idea','.DS_Store','.gitignore','.python-version'}
    items = os.listdir(path)
    items.sort()
    for item in items:
        if item not in exclude:
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                print("│   " * indent + f"├── {item}/")
                generate_project_structure(full_path, indent + 1)
            else:
                print("│   " * indent + f"├── {item}")



async def get_custom_context() -> tuple[Playwright, BrowserContext]:
    # 启动 playwright 驱动
    playwright = await async_playwright().start()

    try:
        # 启动 Chromium，启用持久化用户数据目录
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=CHROME_PROFILE,
            headless=HEADLESS,
            viewport=None,
            channel="chrome",  # ← 关键：自动定位 Chrome
            # 建议：如果只是为了防检测，可以移除硬编码的 UA，
            # Playwright 会自动生成匹配当前版本的 UA。
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",  # 移除自动化标记
            ],
            ignore_https_errors=True,
        )
        return playwright, context
    except Exception as e:
        await playwright.stop()  # 发生异常时务必关闭驱动防止进程残留
        raise e



