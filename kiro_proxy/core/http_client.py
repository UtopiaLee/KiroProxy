"""稳定的 HTTP 请求辅助工具。

目标：避免在某些运行环境里，直接使用 httpx.AsyncClient 时触发
`cannot schedule new futures after shutdown`。

这里统一把低频/非流式的外部请求放到独立线程池里，通过同步 httpx.Client
执行，避免依赖 asyncio 默认 executor。
"""
import asyncio
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
from concurrent.futures import ThreadPoolExecutor

import httpx


_HTTP_EXECUTOR = ThreadPoolExecutor(max_workers=8, thread_name_prefix="kiro-http")


@dataclass
class HttpResult:
    status_code: int
    text: str
    content: bytes
    headers: Dict[str, Any]
    elapsed_ms: float = 0.0


async def run_blocking(func):
    """在独立线程池中执行阻塞函数。"""
    loop = asyncio.get_running_loop()
    future = _HTTP_EXECUTOR.submit(func)
    return await asyncio.wrap_future(future, loop=loop)


async def http_post(url: str, *, json: Any = None, headers: Optional[dict] = None, timeout: float = 30, verify: bool = False) -> HttpResult:
    """在线程池里执行同步 POST。"""

    def _do_post() -> HttpResult:
        start = time.time()
        with httpx.Client(timeout=timeout, verify=verify) as client:
            resp = client.post(url, json=json, headers=headers)
            return HttpResult(
                status_code=resp.status_code,
                text=resp.text,
                content=resp.content,
                headers=dict(resp.headers),
                elapsed_ms=(time.time() - start) * 1000,
            )

    return await run_blocking(_do_post)


async def http_get(url: str, *, headers: Optional[dict] = None, params: Optional[dict] = None, timeout: float = 30, verify: bool = False) -> HttpResult:
    """在线程池里执行同步 GET。"""

    def _do_get() -> HttpResult:
        start = time.time()
        with httpx.Client(timeout=timeout, verify=verify) as client:
            resp = client.get(url, headers=headers, params=params)
            return HttpResult(
                status_code=resp.status_code,
                text=resp.text,
                content=resp.content,
                headers=dict(resp.headers),
                elapsed_ms=(time.time() - start) * 1000,
            )

    return await run_blocking(_do_get)