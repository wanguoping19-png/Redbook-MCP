import asyncio
import re
from playwright_stealth import Stealth
from xhs_tools import *
async def get_xhs_search_keywords(words,item_type,sort_type,counts) -> dict[int, list,str]:
    resp_messages = {
        "code":200,
        "data":[],
        "message":"",
    }
    playwright, context = await get_custom_context()
    # 进行防反爬
    stealth = Stealth()

    page = await context.new_page()

    await stealth.apply_stealth_async(page)
    # 访问小红书探索页
    await page.goto("https://www.xiaohongshu.com/explore", wait_until="domcontentloaded")

    # 开启网络监听
    # ✅✅✅ 关键：在 goto 之前就注册监听器！
    intercepted_response = None

    def handle_response(response):
        nonlocal intercepted_response
        if response.url.startswith("https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"):
            print(f"🔍 捕获到目标请求: {response.url}")
            intercepted_response = response
    page.on("response", handle_response)  # 👈 提前注册！

    # 输出关键词
    await page.locator('id=search-input').fill(words,)
    # 点击查询按钮
    await page.locator('.search-icon').click()
    await page.wait_for_timeout(2000)
    # 刷新网页
    await page.reload(wait_until="load")
    await page.wait_for_timeout(5000)
    if item_type or sort_type:
        # 点击筛选按钮
        await page.locator(".filter").hover()
        await page.wait_for_timeout(5000)
        # 等待筛选面板可见（防止还没展开就点击）
        await page.locator(".filter-panel").wait_for(state="visible")

    # 排序依据
    if sort_type:
        if sort_type == "最新":
            await page.locator(".filter-panel").get_by_text(sort_type).click()
        elif sort_type == "点赞":
            await page.locator(".filter-panel").get_by_text(sort_type).click()
        elif sort_type == "评论":
            await page.locator(".filter-panel").get_by_text(sort_type).click()
        elif sort_type == "收藏":
            await page.locator(".filter-panel").get_by_text(sort_type).click()
        else:
            await page.locator(".filter-panel").get_by_text("综合").click()
    await page.wait_for_timeout(5000)
    if item_type:
        if item_type == "图文":
            await page.locator(".filter-panel").get_by_text(item_type).click()
        elif item_type == "视频":
            await page.locator(".filter-panel").get_by_text(item_type).click()
        else:
            await page.locator(".filter-panel").get_by_text("不限").click()
    await page.wait_for_timeout(5000)
    await page.locator('.search-icon').hover()
    # 滚动鼠标向下30次
    for _ in range(int(counts/22)+2):  # 30 * 0.5s = 15s

        if intercepted_response:
            print("获取值第{}".format(_))
            # 解析响应
            body = await intercepted_response.json()
            resp_messages["data"].extend(body["data"]["items"])
            await page.mouse.wheel(0, 500)
            await page.wait_for_timeout(3000)
        else:
            resp_messages["code"] = 401
            resp_messages["message"] = "超时：未捕获到 v2/note 接口"
            return resp_messages
    resp_messages["message"] = "获取数据成功"
    return resp_messages

async def get_article_info(id,xsec_token)->dict:
    global chinese_only
    base_url = "https://www.xiaohongshu.com/explore/{}?xsec_token={}&xsec_source=pc_search".format(id,xsec_token)

    resp_messages = {
        "code": 200,
        "text": "",
        "message": "",
    }
    playwright, context = await get_custom_context()
    # 进行防反爬
    stealth = Stealth()

    page = await context.new_page()

    await stealth.apply_stealth_async(page)
    # 访问小红书探索页
    await page.goto("https://www.xiaohongshu.com/explore", wait_until="domcontentloaded")
    # 新开一个标签页
    page2 = await context.new_page()
    await page2.goto(base_url, wait_until="domcontentloaded")

    # 等待页面加载完成（确保 note-text 已渲染）
    await page2.wait_for_selector('.note-text', state='attached', timeout=10000)

    # 提取所有 .note-text 的文本
    note_texts = await page2.eval_on_selector_all(
        '.note-text',
        'elements => elements.map(el => el.innerText.trim())'
    )
    if note_texts:
        for text in note_texts:
            # 可选：只保留中文
            chinese_only = ''.join(re.findall(r'[\u4e00-\u9fa5]', text))
            print("原文本:", text)
            print("仅中文:", chinese_only)
            print("-" * 40)
        resp_messages["text"] = note_texts
    return resp_messages




