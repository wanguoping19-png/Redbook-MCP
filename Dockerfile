# 使用官方 Python 3.11+ slim 镜像（轻量）
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（包括 Google Chrome 所需的库 + 字体、libnss3 等）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        fonts-liberation \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libatspi2.0-0 \
        libc6 \
        libcairo2 \
        libcups2 \
        libdbus-1-3 \
        libdrm2 \
        libgbm1 \
        libglib2.0-0 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libpango-1.0-0 \
        libx11-6 \
        libxcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxrandr2 \
        libxshmfence1 \
        wget \
        gnupg \
        unzip \
        xvfb \
        && rm -rf /var/lib/apt/lists/*

# 添加 Google Chrome APT 仓库并安装 Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# 安装 uv（官方推荐方式）
RUN pip install --no-cache-dir uv

# 复制依赖声明文件（关键：先只复制 pyproject.toml 和 uv.lock）
COPY pyproject.toml uv.lock ./

# 使用 uv 安装依赖（含锁定版本）
# --system 表示安装到系统环境（容器内无需虚拟环境）
RUN uv pip install --system --no-cache-dir .

# 创建非 root 用户（安全最佳实践）
RUN useradd --create-home --shell /bin/bash appuser
USER appuser
ENV HOME=/home/appuser
WORKDIR /home/appuser/app

# 复制源码和静态资源
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser static/ ./static/


# 暴露端口（如果 MCP 服务监听端口，比如 8000）
EXPOSE 8085

# 启动命令（根据你的主入口调整）
CMD ["python", "src/xhs_mcp.py"]