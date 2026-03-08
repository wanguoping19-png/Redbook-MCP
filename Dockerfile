FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# 安装 Chrome 所需的基础依赖（确保 dpkg 能正常运行）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        ca-certificates \
        fonts-liberation \
        libappindicator3-1 \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libatspi2.0-0 \
        libcups2 \
        libdbus-1-3 \
        libdrm2 \
        libgbm1 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libu2f-udev \
        libvulkan1 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        libxtst6 \
        xdg-utils \
        xvfb \
    && rm -rf /var/lib/apt/lists/*

# 1. 下载最新的 Google Chrome .deb 包
# 2. 安装 .deb 包
# 3. 自动修复依赖问题
# 4. 清理临时文件
RUN wget -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i /tmp/chrome.deb || apt-get -f -y install && \
    rm -rf /tmp/chrome.deb && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src src
COPY static static

EXPOSE 8085

CMD ["python", "src/xhs_mcp.py"]