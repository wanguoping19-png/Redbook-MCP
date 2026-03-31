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
from xhs_push import push_main
from xhs_search import *
from xhs_login import qrcode_login
from xhs_tools import *
from setting import *
import pandas as pd
# === 全局变量初始化 ===
context = None
playwright = None
mcp = FastMCP("小红书自动化运营", json_response=True,host="0.0.0.0", port=8085) # Create an MCP server

@mcp.tool()
async def close_context():
    """
    关闭小红书浏览器
    :return: {"code": 200, "message": "ok"}
    """
    try:
        await context.close()
        await playwright.stop()
        return {"code": 200, "message": "关闭ok"}
    except Exception as e:
        return {"code":200,"message":"未打开浏览器关闭异常"}

@mcp.tool()
async def up_context():
    """
    开启小红书浏览器
    :return:{"code": 200, "message": "开启ok"}
    """
    global context ,playwright
    if context:
        await close_context()
        playwright, context = await get_custom_context()
        return {"code": 200, "message": "开启ok"}
    else:
        playwright,context = await get_custom_context()
        return {"code": 200, "message": "开启ok"}

@mcp.tool()
async def get_qr_code():
    """
    小红书二维码登陆
    """
    try:
        # 2. 获取二维码
        await qrcode_login(context)
        png_files = glob.glob(os.path.join(QR_IMAGES, "*.png"))
        if not png_files:
            raise FileNotFoundError("指定目录中没有找到任何 PNG 图片。")
        # 找出最新修改的文件
        latest_file = max(png_files, key=os.path.getmtime)
        img = Image.open(latest_file)
        buffer = BytesIO()
        img.save(buffer, format=img.format)
        image_bytes = buffer.getvalue()
        data = base64.b64encode(image_bytes).decode('utf-8')
        return ImageContent(type="image", data=data, mimeType="image/png")
    except Exception as error:
        raise error


@mcp.tool()
async def get_status() -> dict:
    """检查登陆状态"""
    result:dict = await get_login_status(context)
    return result


@mcp.tool()
async def delete_status() -> dict:
    """清除缓存,退出登陆"""
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
        result:dict = await push_main(context=context,image_paths=paths, title=title, content=content, tags=tags)
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
     小红书关键词搜索文章
    :param words: 关键词
    :param item_type: 笔记类型 值为图文or者视频
    :param sort_type: 按照综合， 点赞，评论，收藏筛选只能选其中一个
    :param count: 请求数据量
    :return:  {
        "code":200,
        "data":[],
        "message":"",
    }
    """
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
    result = await get_xhs_search_keywords(context,words, item_type, sort_type,count)
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
    :return:{
        "code": 200,
        "text": "",
        "message": "",
    }
    """
    resp = await get_article_info(id=id,xsec_token=xsec_token)
    return resp



# Run with streamable HTTP transport
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
