# 使用ubuntu最新版本作为基础镜像
FROM ubuntu:latest

RUN  cp /etc/apt/sources.list.d/ubuntu.sources /etc/apt/sources.list.d/ubuntu.sources.bak

#更换软件源（更换为中科大源）
RUN sed -i "s@http://archive.ubuntu.com@http://mirrors.aliyun.com@g" /etc/apt/sources.list.d/ubuntu.sources
RUN sed -i "s@http://security.ubuntu.com@http://mirrors.aliyun.com@g" /etc/apt/sources.list.d/ubuntu.sources

RUN apt-get update && apt-get install -y coturn python3 python3-pip redis-server htop && rm -rf /var/lib/apt/lists/*


#升级pip并安装FastAPI 
RUN  pip3 install fastapi uvicorn langchain_core langchain_openai langchain langchain_community openai redis google-search-results --break-system-packages

#设置Coturn的配置文件
COPY turnserver.conf /etc/turnserver.conf

#设置redis
COPY redis.conf /etc/redis/redis.conf

#设置redis的数据目录
VOLUME /data

WORKDIR /app

#复制代码到容器
COPY . /app
COPY start.sh /app
RUN chmod +x /app/start.sh
#设置开放端口
EXPOSE 8000 3478 3478/udp 

#启动服务

CMD ["/app/start.sh"]
