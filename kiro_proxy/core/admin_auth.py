"""后台管理登录鉴权"""
import hashlib
import hmac
import secrets
import time

from fastapi import Request

from .persistence import load_config, save_config


ADMIN_AUTH_CONFIG_KEY = "admin_auth"
SESSION_COOKIE_NAME = "kiro_proxy_admin_session"
SESSION_TTL_SECONDS = 60 * 60 * 12  # 12 小时
MIN_PASSWORD_LENGTH = 6

_sessions: dict[str, float] = {}


def _cleanup_sessions():
    """清理过期会话"""
    now = time.time()
    expired = [session_id for session_id, expires_at in _sessions.items() if expires_at <= now]
    for session_id in expired:
        _sessions.pop(session_id, None)


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