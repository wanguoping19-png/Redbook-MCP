import asyncio
from playwright_stealth import Stealth
from playwright.async_api import BrowserContext
from xhs_tools import *

# 图文发布
async def push_pictures_content(context: BrowserContext,image_paths: list[str],title:str,content:str,tags:list[str]) -> dict:
    resp_messages = {"code": 200, "message": ""}
    stealth = Stealth()

    page = await context.new_page()

    await stealth.apply_stealth_async(page)

    await page.goto(
        "https://creator.xiaohongshu.com/publish/publish?source=official&from=menu&target=image",
        wait_until="domcontentloaded"
    )
    await page.wait_for_timeout(5000)  # 等待页面基本加载
    try:
        # 等待隐藏的 file input 出现在 DOM 中（不要求 visible）
        file_input = await page.wait_for_selector('input[type="file"]', state="attached", timeout=30000)
        # 直接上传文件
        await file_input.set_input_files(image_paths)
        print(f"✅ 已成功上传图片: {image_paths}")
        await page.locator('input[placeholder="填写标题会有更多赞哦"]').fill(title)

        # 定位 Tiptap 编辑器
        editor = page.locator('div.tiptap.ProseMirror[contenteditable="true"]')

        # 等待元素可见并聚焦
        await editor.wait_for(state="visible")
        await  editor.click()  # 聚焦，确保光标在编辑器内
        # 输入内容（逐字符模拟）
        await editor.type(content)
        await editor.press("Enter")  # 回车，创建新段落

        # 等待光标定位完成
        await page.wait_for_timeout(200)
        for tag in tags:
            await editor.type("#{}".format(tag))
            await page.wait_for_timeout(3000)  # 等待插件处理
            await editor.press("Enter")  # 回车，创建新段落

        publish_btn = page.locator("div.d-button-content").get_by_text("发布")

        # ✅✅✅ 关键：在 goto 之前就注册监听器！
        intercepted_response = None

        def handle_response(response):
            nonlocal intercepted_response
            if response.url.startswith("https://edith.xiaohongshu.com/web_api/sns/v2/note"):
                print(f"🔍 捕获到目标请求: {response.url}")
                intercepted_response = response

        page.on("response", handle_response)  # 👈 提前注册！

        # 确保按钮可见且可点击
        await publish_btn.wait_for(state="visible")
        await publish_btn.scroll_into_view_if_needed()  # 滚动到可视区域
        # 点击
        await publish_btn.click()
        # 3. 等待接口响应（最多 15 秒）
        for _ in range(30):  # 30 * 0.5s = 15s
            if intercepted_response:
                break
            await asyncio.sleep(0.5)
        else:
            resp_messages["code"] = 401
            resp_messages["message"] = "超时：未捕获到 v2/note 接口"
            return resp_messages

        # 4. 解析响应
        body = await intercepted_response.json()
        resp_messages["message"] = body
        # 等待30小时（用于调试，生产环境应替换为真实逻辑
        await page.wait_for_timeout(30000)
        return resp_messages
    except Exception as e:
        print(f"操作失败: {e}")
        resp_messages["code"] = 500
        resp_messages["message"] = str(e)
        return resp_messages

async def push_main(image_paths: list[str],title: str,content: str,tags: list[str]) -> dict:
    playwright, context = await get_custom_context()
    try:

        result:dict = await push_pictures_content(context,image_paths,title,content,tags)
        return result
    except Exception as e:
        result:dict = {"code": 501, "message": str(e)}
        return result
    finally:
        await context.close()
        await playwright.stop()

#
# def run_main():
#     asyncio.run(main())
#
#
# if __name__ == '__main__':
#     run_main()



