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
from xhs_search import *
from xhs_login import qrcode_login
from xhs_tools import *
from setting import *
import pandas as pd
# Create an MCP server
mcp = FastMCP("小红书自动化运营", json_response=True,host="0.0.0.0", port=8085)
# 启动 Playwright
# Add an addition tool
playwright = None
context = None
@mcp.tool()
async def get_qr_code()->dict:
    """
    小红书二维码登陆
    :return:
    """
    global playwright, context  # 👈 关键：声明使用全局变量

    playwright , context = await get_custom_context()

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
        return  result
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

@mcp.tool()
async def get_keyword_content(words:str,item_type:str="",sort_type:str="",count:int=10) -> dict:
    """
     小红书关键词搜索
    :param words: 关键词 必须
    :param item_type: 笔记类型 不限为空，图文或者视频
    :param sort_type: 按照综合， 点赞，评论，收藏筛选只能选其中一个
    :param count: 筛选的数据量
    :return:
    """
    if context:
        await context.close()
    if playwright:
        await playwright.stop()
    filter_map = {
        "点赞": "like_count",
        "评论": "comment_count",
        "收藏": "collected_count",
        "图文":"normal",
        "视频":"video",

    }
    if not words:
        return {
            "code": 401,
            "message": "请输入搜索词"
        }
    result = await get_xhs_search_keywords(words, item_type, sort_type,count)
    data = []
    for item in result["data"]:
        if item.get("note_card"):
            data.append({
                "id": item["id"],
                "xsec_token": item["xsec_token"],
                "note_type": item["note_card"]["type"],
                "user": item["note_card"]["user"]["nick_name"],
                "display_title":item['note_card'].get('display_title',""),
                "like_count": eval(item["note_card"]["interact_info"]["liked_count"]),
                "comment_count": eval(item["note_card"]["interact_info"]["comment_count"]),
                "shared_count": eval(item["note_card"]["interact_info"]["shared_count"]),
                "collected_count":eval(item["note_card"]["interact_info"]["collected_count"])
            })
        continue
    df = pd.DataFrame(data)
    # 按条件筛选
    sort_type = filter_map.get(sort_type,"")
    if sort_type:
        # 按条件排序降序
        df = df.sort_values(by=sort_type, ascending=False)
    # 按需取数
    df = df.iloc[:count]
    data = df.to_dict(orient="records")
    result["data"] = data
    return result
@mcp.tool()
async def get_normal_info(id:str,xsec_token:str) -> dict:
    """
    获取图文详情页
    :param id: 图文ID
    :param xsec_token: 图文凭证
    :return:
    """
    if context:
        await context.close()
    if playwright:
        await playwright.stop()
    resp = await get_article_info(id=id,xsec_token=xsec_token)
    return resp
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
