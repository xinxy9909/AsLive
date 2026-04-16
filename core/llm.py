"""LLM wrapper — Labillion AI-Native 后端（SSE 流式）。"""

import base64
import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone, timedelta

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 配置：通过环境变量设置
# ---------------------------------------------------------------------------
BASE_URL = os.getenv("LABILLION_BASE_URL", "https://staging.automation.labillion.cn")
PLATFORM_ID = os.getenv("LABILLION_PLATFORM_ID", "")
USERNAME = os.getenv("LABILLION_USERNAME", "")
PASSWORD = os.getenv("LABILLION_PASSWORD", "")
TENANT_ID_RAW = os.getenv("LABILLION_TENANT_ID", "")
TENANT_ID = int("".join(c for c in TENANT_ID_RAW if c.isdigit())) if TENANT_ID_RAW else 0


# ---------------------------------------------------------------------------
# Token 管理器
# ---------------------------------------------------------------------------
class TokenManager:
    """SAAS 登录 Token 管理器：自动获取、缓存、刷新。"""

    EXPIRY_BUFFER_SECONDS = 300  # 提前 5 分钟刷新

    def __init__(self) -> None:
        self.access_token: str | None = None
        self.expires_at: float = 0.0

    def get_token(self) -> str:
        """获取有效 token，过期时自动重新登录。"""
        if self.access_token and time.time() < self.expires_at:
            return self.access_token
        self.do_login()
        return self.access_token  # type: ignore[return-value]

    def do_login(self) -> None:
        """调用 SAAS 登录接口获取 token。"""
        url = f"{BASE_URL}/api/identity/v1/auth/login"
        payload = {
            "tenantId": TENANT_ID,
            "userName": USERNAME,
            "password": PASSWORD,
        }
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        token = result.get("data")
        if not token:
            raise RuntimeError(f"Labillion 登录失败: {result.get('message', '未知错误')}")
        self.access_token = token
        self.expires_at = self.parse_expiry(token)
        logger.info("Labillion 登录成功，token 已更新")

    def parse_expiry(self, token: str) -> float:
        """从 JWT payload 解析 exp，返回带缓冲的过期时间戳。"""
        try:
            payload_b64 = token.split(".")[1]
            payload_b64 += "=" * (4 - len(payload_b64) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
            return payload.get("exp", 0) - self.EXPIRY_BUFFER_SECONDS
        except Exception:
            return time.time() + 3600 - self.EXPIRY_BUFFER_SECONDS


token_manager = TokenManager()


# ---------------------------------------------------------------------------
# 请求头工具
# ---------------------------------------------------------------------------
def base_headers() -> dict[str, str]:
    """构造公共请求头。"""
    token = token_manager.get_token()
    return {
        "accept-language": "zh-CN",
        "content-type": "application/json",
        "autobio-auth": token,
        "authorization": token,
        "platform": PLATFORM_ID,
    }


# ---------------------------------------------------------------------------
# AI-Native API 调用
# ---------------------------------------------------------------------------
def create_thread(thread_id: str, query: str) -> None:
    """创建对话线程。"""
    url = f"{BASE_URL}/api/ai-native-backend/v1/thread/create"
    headers = {**base_headers(), "accept": "application/json, text/plain, */*"}
    requests.post(url, headers=headers, json={"query": query, "thread_id": thread_id}, timeout=30).raise_for_status()


def stream_generate(thread_id: str, messages: list[dict]) -> requests.Response:
    """发起聊天请求，返回 SSE 流式响应。"""
    url = f"{BASE_URL}/api/ai-native-backend/v1/generate"
    headers = {
        **base_headers(),
        "accept": "text/event-stream, text/event-stream",
        "access-control-allow-origin": "*",
        "cache-control": "no-transform",
        "x-accel-buffering": "no",
    }
    payload = {
        "thread_id": thread_id,
        "messages": messages,
        "retry_to": 0,
        "files": [],
    }
    resp = requests.post(url, headers=headers, json=payload, stream=True, timeout=60)
    resp.raise_for_status()
    return resp


def parse_sse(response: requests.Response):
    """解析 SSE 响应流，逐块 yield 文本内容。"""
    for raw_line in response.iter_lines(decode_unicode=True):
        if not raw_line or not raw_line.startswith("data:"):
            continue
        data_str = raw_line[len("data:"):].strip()
        if data_str == "[DONE]":
            break
        try:
            event = json.loads(data_str)
            content = (
                event.get("content")
                or (event.get("delta") or {}).get("content")
                or ((event.get("choices") or [{}])[0].get("delta") or {}).get("content")
                or ""
            )
            if content:
                yield content
        except json.JSONDecodeError:
            if data_str:
                yield data_str


def make_messages(role_content_pairs: list[dict]) -> list[dict]:
    """将 {role, content} 列表转换为 AI-Native 消息格式。"""
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    return [
        {
            "id": str(uuid.uuid4()),
            "role": msg["role"],
            "content": msg["content"],
            "creationTime": now,
            "files": [],
            "retryTo": 0,
        }
        for msg in role_content_pairs
    ]


# ---------------------------------------------------------------------------
# LLMWrapper 公共接口
# ---------------------------------------------------------------------------
class LLMWrapper:
    def __init__(self):
        print("正在初始化LLM (Labillion AI-Native)...")
        print("LLM初始化完成！")

    def inference(self, text, max_new_tokens=500) -> str:
        return "".join(self.inference_stream(text, max_new_tokens))

    def inference_stream(self, text, max_new_tokens=500):
        thread_id = str(uuid.uuid4())
        messages = make_messages([{"role": "user", "content": text}])
        create_thread(thread_id, text)
        resp = stream_generate(thread_id, messages)
        try:
            yield from parse_sse(resp)
        finally:
            resp.close()

    def inference_stream_chat(self, messages: list, max_new_tokens=500):
        thread_id = str(uuid.uuid4())
        built = make_messages(messages)
        user_msgs = [m for m in messages if m.get("role") == "user"]
        query = user_msgs[-1]["content"] if user_msgs else ""
        create_thread(thread_id, query)
        resp = stream_generate(thread_id, built)
        try:
            yield from parse_sse(resp)
        finally:
            resp.close()
