# 目的

在llm.py的接入类器官Agent，通过POST连接到类器官Agent服务中，解析返回的SSE请求。

# 实现思路
1. 请求创建对话接口，创建对话。
3. 请求聊天流接口，开始聊天。

# 接口文档

## 创建对话

```
curl --location --request POST 'http://192.168.1.97:2026/api/chat/submit' \
--header 'User-Agent: Apifox/1.0.0 (https://apifox.com)' \
--header 'Content-Type: application/json' \
--header 'Accept: */*' \
--header 'Host: 192.168.1.97:2026' \
--header 'Connection: keep-alive' \
--data-raw '{
    "thread_id": <THREAD_ID>,
    "messages": [
      {
        "role": "user",
        "content": <CHAT_CONTENT>
      }
    ],
    "model": "qwen-plus",
    "thinking_enabled": true,
    "plan_mode": false,
    "config_name": "mega_agent"
  }'
```

## 拉取聊天流

注意offset表示，拉取聊天流的偏移。
当你需要拉取全部历史消息时，offset=0，每次消息回答完毕后服务端都会返回一个最新的offset，当你使用其给定的offset时，仅拉取最新的消息
```
curl --location --request GET 'http://192.168.1.97:2026/api/chat/resume/<THREAD_ID>?offset=0' \
--header 'User-Agent: Apifox/1.0.0 (https://apifox.com)' \
--header 'Accept: */*' \
--header 'Host: 192.168.1.97:2026' \
--header 'Connection: keep-alive'
```

