# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装项目依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 运行项目
CMD ["python", "main.py"]
