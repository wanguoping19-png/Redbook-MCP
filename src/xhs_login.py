import base64
from playwright_stealth import Stealth
from xhs_tools import *
async def qrcode_login(context:BrowserContext) -> dict:
    """
    使用 Playwright 异步获取小红书登录二维码
    """
    resp_messages = {
        "code": 200,
        "image_url": "",
        "message": "",
        "context": None  # 用于后续操作的 context（可选）
    }

    # 确保 QR_IMAGES 目录存在
    os.makedirs(QR_IMAGES, exist_ok=True)

    # 进行防反爬
    stealth = Stealth()

    page = await context.new_page()

    await stealth.apply_stealth_async(page)


    try:
        # 访问小红书探索页
        await page.goto("https://www.xiaohongshu.com/explore", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)  # 可选：等待页面加载动画

        # 等待二维码图片出现（最多 15 秒）
        img_element = await page.wait_for_selector("img.qrcode-img", timeout=30000)

        # 获取 src 属性
        src = await img_element.get_attribute("src")

        if not src or not src.startswith("data:image"):
            resp_messages["code"] = 201
            resp_messages["message"] = "二维码 src 不是有效的 data URL"
            return resp_messages

        # 分离 Base64 数据
        try:
            header, encoded = src.split(",", 1)
            image_data = base64.b64decode(encoded)
        except Exception as e:
            resp_messages["code"] = 201
            resp_messages["message"] = f"Base64 解码失败: {e}"
            await context.close()
            return resp_messages

        # 生成文件名并保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_name = f"登陆二维码_{timestamp}.png"
        image_path = os.path.join(QR_IMAGES, image_name)

        with open(image_path, "wb") as f:
            f.write(image_data)
        print(f"✅ 二维码已保存: {image_path}")

        # 将图片上传到在线图床
        url_data = upload_image(image_name)
        resp_messages["image_url"] = url_data["data"]["url"]
        resp_messages["message"] = "登陆二维码保存成功"
        # 如果你希望外部能继续使用这个浏览器（比如轮询登录状态），不要关闭
        # 此处不关闭 browser，由调用方决定何时关闭
        return resp_messages

    except Exception as e:
        resp_messages["code"] = 400
        resp_messages["message"] = f"获取二维码失败: {str(e)}"
        await context.close()
        return resp_messages

