# 小红书自动化 MCP 工具

这是一个基于 **Python-MCP** 与 **Playwright** 的小红书（Xiaohongshu / Redbook）自动化工具，支持登录、图文发布、关键词搜索等核心功能。

- **python-mcp**: [https://github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)  
- **playwright**: [https://playwright.dev/docs/intro](https://playwright.dev/docs/intro)

---

## ✅ 当前已实现功能

1. **登录功能**
2. **图文发布功能**
3. **搜索词查询功能**

---

## 📁 项目目录结构

```text
项目目录结构
├── Dockerfile                 # Docker 镜像打包配置
├── README.md
├── pyproject.toml
├── src/
│   ├── setting.py             # 固定参数的配置
│   ├── xhs_login.py           # 登录功能逻辑
│   ├── xhs_login_status.py    # 登录状态查询逻辑
│   ├── xhs_mcp.py             # 服务启动入口
│   ├── xhs_push.py            # 图文推送逻辑
│   ├── xhs_search.py          # 搜索词查询逻辑
│   ├── xhs_tools.py           # 通用工具函数
├── static/
│   ├── images/                # 登录二维码存放目录
│   │   └── 登陆二维码_20260320_015248.png
│   ├── mp4_content/           # 视频内容（预留）
│   └── pic_content/           # 上传图片存放目录
├── uv.lock
```

---

## 🚀 快速开始

### 使用 Docker 方式部署

#### 1. 构建镜像

```bash
docker build -t redbook-mcp .
```

#### 2. 启动容器

将镜像运行后，即可通过 MCP 客户端进行测试：

```bash
docker run -d \
  --name xhs-mcp \
  -p 8085:8085 \
  -v ./share_data:/app/data \
  --restart unless-stopped \
  --network n8n-network \
  redbook-mcp:latest
```

> **说明**：
> - `8085` 端口为 MCP 服务暴露端口
> - `./share_data` 用于持久化数据（如 cookies、截图等）
> - `--network n8n-network` 可选，用于与 n8n 等编排工具集成

#### 3. 使用 MCP 客户端测试

推荐使用官方 **MCP Inspector** 进行调试：

```bash
npx -y @modelcontextprotocol/inspector
```

在 Inspector UI 中连接地址：`http://localhost:8085/mcp`

> **图片占位**：Inspector 连接成功界面截图

---

## 🎥 功能演示

### 1. 登录功能

#### 1.1 登录状态查询  
<video src="https://www.douyin.com/jingxuan?modal_id=7622979898851773730" controls></video>
#### 1.2 二维码登录  
📸 *视频占位：展示生成二维码、用户扫码、自动完成登录流程*

### 2. 搜索词功能  
🔍 *视频占位：输入关键词（如“春日穿搭”），返回相关笔记列表或热度数据*

### 3. 图文发布功能  
🖼️ *视频占位：上传多张图片 + 文案，自动发布到小红书账号*

---

> 💡 本工具适用于自动化内容运营、竞品监控、批量发布等场景，**请遵守小红书平台规则，避免高频操作导致封号**。

