"""
FastMCP quickstart example.

Run from the repository root:
    uv run examples/snippets/servers/fastmcp_quickstart.py
"""
import base64
from io import BytesIO
from PIL import Image
from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent
import shutil
from xhs_login_status import get_login_status
import glob
from xhs_push import push_main
from playwright.async_api import async_playwright, BrowserContext
from xhs_login import qrcode_login
from xhs_tools import *
from setting import *
# Create an MCP server
mcp = FastMCP("小红书自动化运营", json_response=True,host="0.0.0.0", port=8085)
# 启动 Playwright
# Add an addition tool
playwright = None
context = None
@mcp.tool()
async def get_qr_code():
    """
    小红书二维码登陆
    :return:
    """
    global playwright, context  # 👈 关键：声明使用全局变量
    playwright = await async_playwright().start()
    # 启动 Chromium，启用持久化用户数据目录
    context = await playwright.chromium.launch_persistent_context(
        user_data_dir=CHROME_PROFILE,
        headless=HEADLESS,  # 无头模式
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
        ],
        ignore_https_errors=True,
    )  # type: BrowserContext
    try:
        # 2. 获取二维码
        result = await qrcode_login(context)
        print(result)
        files = glob.glob("../static/images/登陆二维码*.png")
        img_path = files[0]
        img = Image.open(img_path)
        buffer = BytesIO()
        img.save(buffer, format=img.format)
        image_bytes = buffer.getvalue()
        data = base64.b64encode(image_bytes).decode('utf-8')
        ImageContent(type="image", data=data, mimeType="image/png")
        return  ImageContent(type="image", data=data, mimeType="image/png")
    except Exception as error:
        raise error


@mcp.tool()
async def get_status() -> dict:
    """检查登陆状态"""
    if context:
        await context.close()
    if playwright:
        await playwright.stop()
    result:dict = await get_login_status()
    return result


@mcp.tool()
async def delete_status() -> dict:
    """清除缓存,退出登陆"""
    if context:
        await context.close()
    if playwright:
        await playwright.stop()
    shutil.rmtree(CHROME_PROFILE)
    return {
        "code": 200,
        "message": "清除成功",
    }


@mcp.tool()
async def push_image_text(image_paths: list[str],title: str,content: str,tags: list[str]) -> dict:
    """
     小红书图文发布
    :param image_paths: 图片路径列表
    :param title: 图文标题
    :param content: 图文内容
    :param tags: 图文标签
    :return:{"code": 200, "message": {
                "data": {
                    "id": "69b4210c000000001a03761f",
                    "score": 10
                },
                "share_link": "https://www.xiaohongshu.com/discovery/item/69b4210c000000001a03761f",
                "business_bind_results": [],
                "result": 0,
                "success": true,
                "msg": ""
            }}
    """
    if context:
        await context.close()
    if playwright:
        await playwright.stop()
    try:
        paths = []
        try:
            for image_path in image_paths:
                if image_path.startswith("http"):
                    temp_path = save_url_to_path(image_path)
                    paths.append(temp_path)
                else:
                    paths.append(image_path)
        except Exception as e:
            result = {
                "code": 501,
                "message": "图片路径格式错误"
            }
            return result
        if len(title)>18:
            return {
                "code": 200,
                "message": "标题字数超过20字"
            }
        if len(content)>900:
            return {
                "code": 200,
                "message": "内容超过900字"
            }
        result:dict = await push_main(image_paths=paths, title=title, content=content, tags=tags)
        return result
    except Exception as e:
        return {
            "code": 510,
            "message": "发布失败",
            "error": str(e)
        }


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# Add a prompt
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."


# Run with streamable HTTP transport
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
