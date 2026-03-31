import asyncio
from playwright_stealth import Stealth
from xhs_tools import *
TARGET_API_URL = "https://edith.xiaohongshu.com/api/sns/web/v2/user/me"
async def get_login_status(context:BrowserContext) -> dict[str, str | int] | None:
    resp_messages = {"code": 200, "message": ""}
    # 进行防反爬
    stealth = Stealth()
    page = await context.new_page()
    await stealth.apply_stealth_async(page)


    # ✅✅✅ 关键：在 goto 之前就注册监听器！
    intercepted_response = None

    def handle_response(response):
        nonlocal intercepted_response
        if response.url.startswith("https://edith.xiaohongshu.com/api/sns/web/v2/user/me"):
            print(f"🔍 捕获到目标请求: {response.url}")
            intercepted_response = response

    page.on("response", handle_response)  # 👈 提前注册！

    try:
        # 1. 进入探索页
        await page.goto("https://www.xiaohongshu.com/explore", wait_until="domcontentloaded")
        await asyncio.sleep(4)
        # 2. 等待并点击「我」
        me_button = page.locator("(//li[contains(@class,'user')]/div/a[@title='我'])[1]")
        await me_button.wait_for(state="visible", timeout=60000)
        await me_button.click()
        print("✅ 已点击「我」按钮")

        # 3. 等待接口响应（最多 15 秒）
        for _ in range(30):  # 30 * 0.5s = 15s
            if intercepted_response:
                break
            await asyncio.sleep(0.5)
        else:
            resp_messages["code"] = 401
            resp_messages["message"] = "超时：未捕获到 user/me 接口"
            return resp_messages

        # 4. 解析响应
        body = await intercepted_response.json()
        resp_messages["message"] = body.get("data", {})
        print("✅ 成功获取用户信息")
        return resp_messages
    except Exception as e:
        resp_messages["code"] = 401
        resp_messages["message"] = "用户为未登陆"
        resp_messages["error"] = str(e)
        return resp_messages


