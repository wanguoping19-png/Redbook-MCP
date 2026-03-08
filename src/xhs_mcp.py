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
import xhs_login
import shutil
import xhs_login_status
import glob
G_DRIVER=[]
# Create an MCP server
mcp = FastMCP("小红书自动化运营", json_response=True,host="0.0.0.0", port=8085)

files = glob.glob("./static/images/登陆二维码*.png")

# Add an addition tool
@mcp.tool()
def get_qr_code() -> dict:
    """进行登陆"""
    if G_DRIVER:
        G_DRIVER[0].quit()
        G_DRIVER.pop(0)
    else:
        result = xhs_login.qrcode_login()
        G_DRIVER.append(result["driver"])
        result.pop("driver")
        files = glob.glob("./static/images/登陆二维码*.png")
        img_path = files[0]
        img = Image.open(img_path)
        buffer = BytesIO()
        img.save(buffer, format=img.format)
        image_bytes = buffer.getvalue()
        data = base64.b64encode(image_bytes).decode('utf-8')
        ImageContent(type="image", data=data, mimeType="image/png")
        return  ImageContent(type="image", data=data, mimeType="image/png")

@mcp.tool()
def get_status() -> dict:
    """检查登陆状态"""
    if G_DRIVER:
        G_DRIVER[0].quit()
        G_DRIVER.pop(0)
    else:
        result = xhs_login_status.get_login_status()
        return result

@mcp.tool()
def delete_status() -> dict:
    """清除缓存,退出登陆"""
    if G_DRIVER:
        G_DRIVER[0].quit()
        G_DRIVER.pop(0)
    shutil.rmtree("./chrome_profile")

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
