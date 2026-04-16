# 多阶段构建 - 构建阶段
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.13-slim as builder

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv（更快的 Python 包管理器）
RUN pip install --no-cache-dir uv

# 复制项目文件
COPY . /app

# 使用 uv 安装依赖
RUN uv pip install --system -r <(uv pip compile pyproject.toml)

# 最终阶段
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.13-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制 Python 环境
COPY --from=builder /usr/local /usr/local

# 复制项目代码
COPY . /app

# 创建输出目录
RUN mkdir -p /app/outputs

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# 启动应用
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
