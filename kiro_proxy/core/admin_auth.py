"""后台管理登录鉴权"""
import hashlib
import hmac
import ipaddress
import secrets
import time

from fastapi import Request

from .persistence import load_config, save_config


ADMIN_AUTH_CONFIG_KEY = "admin_auth"
SESSION_COOKIE_NAME = "kiro_proxy_admin_session"
SESSION_TTL_SECONDS = 60 * 60 * 12  # 12 小时
MIN_PASSWORD_LENGTH = 6
LOGIN_FAILURE_WINDOW_SECONDS = 60 * 10  # 10 分钟
LOGIN_MAX_FAILURES = 5
LOGIN_LOCKOUT_BASE_SECONDS = 60 * 30  # 30 分钟
LOGIN_LOCKOUT_MAX_SECONDS = 60 * 60 * 24  # 24 小时
LOGIN_LOCKOUT_REPEAT_WINDOW_SECONDS = 60 * 60 * 24  # 24 小时内递增惩罚

_sessions: dict[str, float] = {}
_login_attempts: dict[str, dict] = {}


def _cleanup_sessions():
    """清理过期会话"""
    now = time.time()
    expired = [session_id for session_id, expires_at in _sessions.items() if expires_at <= now]
    for session_id in expired:
        _sessions.pop(session_id, None)


def _default_login_attempt_record() -> dict:
    """默认登录失败记录。"""
    return {
        "failures": [],
        "lock_until": 0.0,
        "lock_level": 0,
        "last_lock_at": 0.0,
    }


def _cleanup_login_attempts():
    """清理过期的登录失败记录。"""
    now = time.time()
    stale_ips = []
    for client_ip, record in _login_attempts.items():
        record["failures"] = [
            ts for ts in record.get("failures", [])
            if now - ts <= LOGIN_FAILURE_WINDOW_SECONDS
        ]

        if record.get("lock_until", 0) <= now:
            record["lock_until"] = 0.0

        if record.get("last_lock_at", 0) and now - record["last_lock_at"] > LOGIN_LOCKOUT_REPEAT_WINDOW_SECONDS:
            record["lock_level"] = 0
            record["last_lock_at"] = 0.0

        if (
            not record.get("failures")
            and record.get("lock_until", 0) <= now
            and record.get("last_lock_at", 0) == 0
        ):
            stale_ips.append(client_ip)

    for client_ip in stale_ips:
        _login_attempts.pop(client_ip, None)


def _get_client_ip(request: Request) -> str:
    """获取客户端 IP。

    仅在请求来源是本机回环地址时信任反向代理头，避免直接暴露服务时被伪造。
    """
    client_host = (request.client.host if request.client else "") or "unknown"

    try:
        parsed_ip = ipaddress.ip_address(client_host)
        is_loopback = parsed_ip.is_loopback
    except ValueError:
        is_loopback = client_host in {"localhost", "unknown"}

    if is_loopback:
        real_ip = request.headers.get("x-real-ip", "").strip()
        if real_ip:
            return real_ip

        forwarded_for = request.headers.get("x-forwarded-for", "").strip()
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

    return client_host


def _build_lockout_duration(lock_level: int) -> int:
    """根据锁定等级计算锁定时长。"""
    if lock_level <= 0:
        return 0
    return min(LOGIN_LOCKOUT_BASE_SECONDS * (2 ** (lock_level - 1)), LOGIN_LOCKOUT_MAX_SECONDS)


def _get_or_create_attempt_record(client_ip: str) -> dict:
    """获取或创建某个 IP 的登录失败记录。"""
    record = _login_attempts.get(client_ip)
    if not record:
        record = _default_login_attempt_record()
        _login_attempts[client_ip] = record
    return record


def get_login_attempt_status(request: Request) -> dict:
    """获取当前客户端的登录防爆破状态。"""
    _cleanup_login_attempts()
    client_ip = _get_client_ip(request)
    record = _login_attempts.get(client_ip, _default_login_attempt_record())
    now = time.time()
    retry_after_seconds = max(0, int(record.get("lock_until", 0) - now))
    failures = len(record.get("failures", []))

    return {
        "enabled": True,
        "client_ip": client_ip,
        "locked": retry_after_seconds > 0,
        "retry_after_seconds": retry_after_seconds,
        "failure_window_seconds": LOGIN_FAILURE_WINDOW_SECONDS,
        "max_failures": LOGIN_MAX_FAILURES,
        "remaining_attempts": max(0, LOGIN_MAX_FAILURES - failures),
        "lockout_base_seconds": LOGIN_LOCKOUT_BASE_SECONDS,
        "lockout_max_seconds": LOGIN_LOCKOUT_MAX_SECONDS,
        "lockout_repeat_window_seconds": LOGIN_LOCKOUT_REPEAT_WINDOW_SECONDS,
        "current_lock_level": int(record.get("lock_level", 0)),
        "current_lockout_seconds": _build_lockout_duration(int(record.get("lock_level", 0))),
    }


def register_failed_login_attempt(request: Request) -> dict:
    """记录一次失败登录，并在超限时触发锁定。"""
    _cleanup_login_attempts()
    now = time.time()
    client_ip = _get_client_ip(request)
    record = _get_or_create_attempt_record(client_ip)

    record["failures"] = [
        ts for ts in record.get("failures", [])
        if now - ts <= LOGIN_FAILURE_WINDOW_SECONDS
    ]
    record["failures"].append(now)

    if len(record["failures"]) >= LOGIN_MAX_FAILURES:
        last_lock_at = float(record.get("last_lock_at", 0) or 0)
        previous_level = int(record.get("lock_level", 0) or 0)

        if last_lock_at and now - last_lock_at <= LOGIN_LOCKOUT_REPEAT_WINDOW_SECONDS:
            lock_level = previous_level + 1
        else:
            lock_level = 1

        lockout_seconds = _build_lockout_duration(lock_level)
        record["lock_level"] = lock_level
        record["last_lock_at"] = now
        record["lock_until"] = now + lockout_seconds
        record["failures"] = []

    return get_login_attempt_status(request)


def reset_login_attempts(request: Request):
    """登录成功后重置当前 IP 的失败计数。"""
    _cleanup_login_attempts()
    client_ip = _get_client_ip(request)
    record = _login_attempts.get(client_ip)
    if record:
        record["failures"] = []


def _get_auth_config() -> dict:
    """读取后台鉴权配置"""
    config = load_config()
    return config.get(ADMIN_AUTH_CONFIG_KEY, {})


def is_password_configured() -> bool:
    """是否已设置后台密码"""
    config = _get_auth_config()
    return bool(config.get("password_hash") and config.get("salt"))


def _hash_password(password: str, salt: str) -> str:
    """生成密码哈希"""
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200000,
    ).hex()


def set_admin_password(password: str) -> bool:
    """设置后台密码"""
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"密码长度不能少于 {MIN_PASSWORD_LENGTH} 位")

    config = load_config()
    salt = secrets.token_hex(16)
    config[ADMIN_AUTH_CONFIG_KEY] = {
        "salt": salt,
        "password_hash": _hash_password(password, salt),
        "updated_at": int(time.time()),
    }

    _sessions.clear()
    return save_config(config)


def verify_admin_password(password: str) -> bool:
    """校验后台密码"""
    config = _get_auth_config()
    salt = config.get("salt")
    password_hash = config.get("password_hash")
    if not salt or not password_hash:
        return False

    candidate_hash = _hash_password(password, salt)
    return hmac.compare_digest(candidate_hash, password_hash)


def create_session() -> str:
    """创建登录会话"""
    _cleanup_sessions()
    session_id = secrets.token_urlsafe(32)
    _sessions[session_id] = time.time() + SESSION_TTL_SECONDS
    return session_id


def invalidate_session(session_id: str | None):
    """销毁登录会话"""
    if session_id:
        _sessions.pop(session_id, None)


def get_session_id(request: Request) -> str | None:
    """从请求中读取会话 ID"""
    return request.cookies.get(SESSION_COOKIE_NAME)


def is_authenticated(request: Request) -> bool:
    """判断请求是否已登录后台"""
    _cleanup_sessions()
    session_id = get_session_id(request)
    if not session_id:
        return False

    expires_at = _sessions.get(session_id)
    if not expires_at:
        return False

    if expires_at <= time.time():
        _sessions.pop(session_id, None)
        return False

    # 滑动续期
    _sessions[session_id] = time.time() + SESSION_TTL_SECONDS
    return True