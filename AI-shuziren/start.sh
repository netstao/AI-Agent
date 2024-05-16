#!/bin/bash

echo "start up  redis..." && 
redis-server /etc/redis/redis.conf --protected-mode no & 
echo "start up  server:app..." &&
uvicorn server:app --host 0.0.0.0 --port 8000 & 
echo "start up  turnserver..." && 
turnserver -c /etc/turnserver.conf --listening-ip=0.0.0.0 --listening-port=3478 
echo "start up done..."