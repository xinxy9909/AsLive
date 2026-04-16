# 目的

替换llm.py的实现，改为通过POST连接到Labillion-AI-Native服务中，解析返回的SSE请求。

# 注意事项
Labillion系统需要鉴权，你需要参考/Users/shawn/PycharmProjects/deer-flow/skills/special/process-operation/process_operation/api.py中的实现，全自动的刷新并获取Token

# 实现思路
1. 获取Token
2. 请求ai-native的创建对话接口，创建对话。
3. 请求ai-native的聊天接口，开始聊天。

# 接口文档

<PLATFORM_ID> 表示平台ID
以上参数需要支持通过环境变量设置

## 创建对话

```
curl 'https://staging.automation.labillion.cn/api/ai-native-backend/v1/thread/create' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN' \
  -H 'autobio-auth: <TOKEN>' \
  -H 'content-type: application/json' \
  -H 'origin: https://staging.automation.labillion.cn' \
  -H 'platform: <PLATFORM_ID>' \
  -H 'priority: u=1, i' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36' \
  --data-raw '{"query":<CHAT_CONTENT>,"thread_id":<THREAD_ID>}'
```

## 开始聊天

```
curl 'https://staging.automation.labillion.cn/api/ai-native-backend/v1/generate' \
  -H 'accept: text/event-stream, text/event-stream' \
  -H 'accept-language: zh-CN' \
  -H 'access-control-allow-origin: *' \
  -H 'authorization: <TOKEN>' \
  -H 'autobio-auth: <TOKEN>' \
  -H 'cache-control: no-transform' \
  -H 'content-type: application/json' \
  -H 'origin: https://staging.automation.labillion.cn' \
  -H 'platform: <PLATFORM_ID>' \
  -H 'priority: u=1, i' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36' \
  -H 'x-accel-buffering: no' \
  --data-raw '{"thread_id":<THREAD_ID>,"messages":[{"id":<MESSAGE_ID>,"role":"user","content":<CHAT_CONTENT>,"creationTime":"2026-04-16T13:45:12+08:00","files":[],"retryTo":0}],"retry_to":0,"files":[]}'
```

