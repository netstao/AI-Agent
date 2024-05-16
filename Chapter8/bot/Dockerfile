# 使用官方的Python基础镜像
FROM python:3.12.0

# 设置工作目录
WORKDIR /aiserver

# 安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 拷贝你的代码到容器中
COPY . .

# 设置启动命令
CMD ["python", "server.py"]