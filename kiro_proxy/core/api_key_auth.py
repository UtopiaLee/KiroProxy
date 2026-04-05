"""V1 API Key 鉴权"""
import hashlib
import hmac
import secrets
import time

from fastapi import Request

from .persistence import load_config, save_config


API_KEY_CONFIG_KEY = "api_key_auth"
API_KEY_MIN_LENGTH = 8
API_KEY_HEADER = "x-api-key"
API_KEY_AUTH_PREFIX = "Bearer "


def _get_api_key_config() -> dict:
    """读取 API Key 配置"""
    config = load_config()
    return config.get(API_KEY_CONFIG_KEY, {})


def is_api_key_configured() -> bool:
    """是否已配置 API Key"""
    config = _get_api_key_config()
    return bool(config.get("key_hash") and config.get("salt"))


def _hash_api_key(api_key: str, salt: str) -> str:
    """生成 API Key 哈希"""
    return hashlib.pbkdf2_hmac(
        "sha256",
        api_key.encode("utf-8"),
        salt.encode("utf-8"),
        200000,
    ).hex()


def _build_key_preview(api_key: str) -> str:
    """生成 API Key 预览信息"""
    if len(api_key) <= 8:
        return "*" * len(api_key)
    return f"{api_key[:4]}{'*' * max(4, len(api_key) - 8)}{api_key[-4:]}"


def generate_api_key() -> str:
    """生成随机 API Key"""
    return f"kp_{secrets.token_urlsafe(24)}"


def set_api_key(api_key: str) -> bool:
    """保存 API Key"""
    api_key = (api_key or "").strip()
    if len(api_key) < API_KEY_MIN_LENGTH:
        raise ValueError(f"API Key 长度不能少于 {API_KEY_MIN_LENGTH} 位")

    config = load_config()
    salt = secrets.token_hex(16)
    config[API_KEY_CONFIG_KEY] = {
        "salt": salt,
        "key_hash": _hash_api_key(api_key, salt),
        "key_preview": _build_key_preview(api_key),
        "updated_at": int(time.time()),
    }
    return save_config(config)


def clear_api_key() -> bool:
    """清除 API Key"""
    config = load_config()
    if API_KEY_CONFIG_KEY in config:
        config.pop(API_KEY_CONFIG_KEY, None)
        return save_config(config)
    return True


def get_api_key_status() -> dict:
    """获取 API Key 配置状态"""
    config = _get_api_key_config()
    return {
        "configured": is_api_key_configured(),
        "key_preview": config.get("key_preview"),
        "updated_at": config.get("updated_at"),
        "min_length": API_KEY_MIN_LENGTH,
        "header": API_KEY_HEADER,
    }


def verify_api_key(api_key: str | None) -> bool:
    """校验 API Key"""
    if not api_key:
        return False

    config = _get_api_key_config()
    salt = config.get("salt")
    key_hash = config.get("key_hash")
    if not salt or not key_hash:
        return False

    candidate_hash = _hash_api_key(api_key.strip(), salt)
    return hmac.compare_digest(candidate_hash, key_hash)


def extract_api_key(request: Request) -> str | None:
    """从请求中提取 API Key"""
    x_api_key = request.headers.get(API_KEY_HEADER)
    if x_api_key:
        return x_api_key.strip()

    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith(API_KEY_AUTH_PREFIX):
        return auth_header[len(API_KEY_AUTH_PREFIX):].strip()

    return None
