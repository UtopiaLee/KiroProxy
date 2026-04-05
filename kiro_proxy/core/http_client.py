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
import threading

import httpx


_HTTP_EXECUTOR_LOCK = threading.Lock()
_HTTP_EXECUTOR: Optional[ThreadPoolExecutor] = None


def _create_executor() -> ThreadPoolExecutor:
    return ThreadPoolExecutor(max_workers=8, thread_name_prefix="kiro-http")


def _get_executor() -> ThreadPoolExecutor:
    global _HTTP_EXECUTOR
    with _HTTP_EXECUTOR_LOCK:
        if _HTTP_EXECUTOR is None or getattr(_HTTP_EXECUTOR, "_shutdown", False):
            _HTTP_EXECUTOR = _create_executor()
        return _HTTP_EXECUTOR


def shutdown_http_executor(wait: bool = False):
    """显式关闭 HTTP 线程池。"""
    global _HTTP_EXECUTOR
    with _HTTP_EXECUTOR_LOCK:
        executor = _HTTP_EXECUTOR
        _HTTP_EXECUTOR = None

    if executor and not getattr(executor, "_shutdown", False):
        executor.shutdown(wait=wait, cancel_futures=True)


def _reset_executor(closed_executor: ThreadPoolExecutor):
    """在线程池意外关闭时重建 executor。"""
    global _HTTP_EXECUTOR
    with _HTTP_EXECUTOR_LOCK:
        if _HTTP_EXECUTOR is closed_executor or _HTTP_EXECUTOR is None:
            _HTTP_EXECUTOR = _create_executor()


@dataclass
class HttpResult:
    status_code: int
    text: str
    content: bytes
    headers: Dict[str, Any]
    elapsed_ms: float = 0.0


async def run_blocking(func):
    """在独立线程池中执行阻塞函数。

    某些 Linux/systemd 运行环境下，线程池可能被意外 shutdown，
    这里在检测到该异常时自动重建并重试一次。
    """
    loop = asyncio.get_running_loop()
    for attempt in range(2):
        executor = _get_executor()
        try:
            future = executor.submit(func)
            return await asyncio.wrap_future(future, loop=loop)
        except RuntimeError as e:
            if "cannot schedule new futures after shutdown" not in str(e) or attempt == 1:
                raise
            _reset_executor(executor)


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