import os
import time
import json
import logging
import asyncio
from dataclasses import dataclass
from typing import Optional

import httpx
import requests  # <-- добавлено

logger = logging.getLogger(__name__)

@dataclass
class AIResult:
    text: str
    meta: dict
    duration_ms: int
    error: Optional[str] = None


class AIClient:
    def __init__(self):
        self.base_url = (os.getenv("OPENAI_BASE_URL") or "https://api.openai.com").rstrip("/")
        self.api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.timeout = float(os.getenv("AI_TIMEOUT", "15"))
        self.max_tokens = int(os.getenv("AI_MAX_TOKENS", "256"))
        self.temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))
        self.stub_mode = not bool(self.api_key)

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def _build_payload(self, system: str, developer: str, user: str, context: dict) -> dict:
        messages = [
            {"role": "system", "content": system},
            {"role": "system", "content": developer},
            {"role": "system", "content": f"Context: {json.dumps(context, ensure_ascii=False)[:1200]}"},
            {"role": "user", "content": user},
        ]
        return {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

    async def _async_generate(self, system: str, developer: str, user: str, context: dict) -> AIResult:
        start = time.time()
        logger.info("🧠 AIClient.generate()")
        logger.debug(f"System Prompt:\n{system}")
        logger.debug(f"Developer Prompt:\n{developer}")
        logger.debug(f"User Text:\n{user}")
        logger.debug(f"Context:\n{json.dumps(context, ensure_ascii=False)[:1200]}")

        if self.stub_mode:
            text = f"Заглушка ИИ: ключ не задан. Эхо: {user[:120]}"
            dur_ms = int((time.time() - start) * 1000)
            logger.warning("⚠️ AIClient: STUB MODE — ключ не задан")
            return AIResult(text=text, meta={"stub": True}, duration_ms=dur_ms, error="NO_API_KEY")

        payload = self._build_payload(system, developer, user, context)
        url = f"{self.base_url}/v1/chat/completions"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, headers=self._headers(), json=payload)

            dur_ms = int((time.time() - start) * 1000)
            if resp.status_code != 200:
                logger.error(f"❌ AIClient: HTTP {resp.status_code} — {resp.text[:300]}")
                return AIResult(
                    text="",
                    meta={"status": resp.status_code, "body": resp.text[:500]},
                    duration_ms=dur_ms,
                    error=f"HTTP_{resp.status_code}",
                )

            data = resp.json()
            text = (data.get("choices", [{}])[0].get("message", {}) or {}).get("content", "") or ""
            logger.debug(f"✅ AIClient response: {text[:300]}")
            return AIResult(text=text.strip(), meta={"model": self.model}, duration_ms=dur_ms)
        except Exception as e:
            dur_ms = int((time.time() - start) * 1000)
            logger.exception("❌ AIClient: Exception during request")
            return AIResult(text="", meta={}, duration_ms=dur_ms, error=str(e))

    def _sync_generate(self, system: str, developer: str, user: str, context: dict) -> AIResult:
        start = time.time()
        logger.info("🧠 AIClient.generate() [sync]")
        logger.debug(f"System Prompt:\n{system}")
        logger.debug(f"Developer Prompt:\n{developer}")
        logger.debug(f"User Text:\n{user}")
        logger.debug(f"Context:\n{json.dumps(context, ensure_ascii=False)[:1200]}")

        if self.stub_mode:
            text = f"Заглушка ИИ: ключ не задан. Эхо: {user[:120]}"
            dur_ms = int((time.time() - start) * 1000)
            logger.warning("⚠️ AIClient: STUB MODE — ключ не задан")
            return AIResult(text=text, meta={"stub": True}, duration_ms=dur_ms, error="NO_API_KEY")

        payload = self._build_payload(system, developer, user, context)
        url = f"{self.base_url}/v1/chat/completions"
        try:
            resp = requests.post(url, headers=self._headers(), json=payload, timeout=self.timeout)
            dur_ms = int((time.time() - start) * 1000)

            if resp.status_code != 200:
                body = resp.text if hasattr(resp, "text") else str(resp.content)[:500]
                logger.error(f"❌ AIClient: HTTP {resp.status_code} — {body[:300]}")
                return AIResult(
                    text="",
                    meta={"status": resp.status_code, "body": body[:500]},
                    duration_ms=dur_ms,
                    error=f"HTTP_{resp.status_code}",
                )

            data = resp.json()
            text = (data.get("choices", [{}])[0].get("message", {}) or {}).get("content", "") or ""
            logger.debug(f"✅ AIClient response: {text[:300]}")
            return AIResult(text=text.strip(), meta={"model": self.model}, duration_ms=dur_ms)
        except Exception as e:
            dur_ms = int((time.time() - start) * 1000)
            logger.exception("❌ AIClient: Exception during request (sync)")
            return AIResult(text="", meta={}, duration_ms=dur_ms, error=str(e))

    def generate(self, system: str, developer: str, user: str, context: dict) -> AIResult:
        """Синхронная обёртка для совместимости"""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Запущено в async‑контексте
            return asyncio.run_coroutine_threadsafe(
                self._async_generate(system, developer, user, context), loop
            ).result()
        else:
            # Синхронный путь — важно для unit‑тестов, которые мокают requests.post
            return self._sync_generate(system, developer, user, context)
