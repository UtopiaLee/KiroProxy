# API参考

## 代理端点

### OpenAI协议

#### POST /v1/chat/completions

聊天完成API，OpenAI兼容。

**请求示例:**

```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "user", "content": "你好！"}
  ],
  "stream": true
}
```

**模型映射:**

| 请求模型 | 实际模型 |
|----------|----------|
| gpt-4o, gpt-4 | claude-sonnet-4 |
| gpt-4o-mini, gpt-3.5-turbo | claude-haiku-4.5 |
| o1, o1-preview | claude-opus-4.5 |

#### GET /v1/models

获取可用模型列表。

---

### Anthropic协议

#### POST /v1/messages

消息API，Anthropic兼容。

**请求示例:**

```json
{
  "model": "claude-sonnet-4",
  "max_tokens": 4096,
  "messages": [
    {"role": "user", "content": "你好！"}
  ]
}
```

#### POST /v1/messages/count_tokens

计算消息令牌数。

---

### Gemini协议

#### POST /v1/models/{model}:generateContent

生成内容API，Gemini兼容。

---

## 管理API

### 状态和统计

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/status` | GET | 服务状态 |
| `/api/stats` | GET | 基本统计 |
| `/api/stats/detailed` | GET | 详细统计 |
| `/api/quota` | GET | 配额状态 |
| `/api/logs` | GET | 请求日志 |

### 账户管理

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/accounts` | GET | 账户列表 |
| `/api/accounts` | POST | 添加账户 |
| `/api/accounts/{id}` | GET | 账户详情 |
| `/api/accounts/{id}` | DELETE | 删除账户 |
| `/api/accounts/{id}/toggle` | POST | 启用/禁用 |
| `/api/accounts/{id}/refresh` | POST | 刷新令牌 |
| `/api/accounts/{id}/restore` | POST | 恢复账户 |
| `/api/accounts/{id}/usage` | GET | 使用情况查询 |
| `/api/accounts/refresh-all` | POST | 刷新所有 |

### 令牌操作

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/token/scan` | GET | 扫描本地令牌 |
| `/api/token/add-from-scan` | POST | 从扫描添加 |
| `/api/token/refresh-check` | POST | 检查令牌状态 |

### 登录

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/kiro/login/start` | POST | 开始AWS登录 |
| `/api/kiro/login/poll` | GET | 轮询登录状态 |
| `/api/kiro/login/cancel` | POST | 取消登录 |
| `/api/kiro/social/start` | POST | 开始社交登录 |
| `/api/kiro/social/exchange` | POST | 交换令牌 |

### 流监控

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/flows` | GET | 查询流 |
| `/api/flows/stats` | GET | 流统计 |
| `/api/flows/{id}` | GET | 流详情 |
| `/api/flows/{id}/bookmark` | POST | 书签流 |
| `/api/flows/export` | POST | 导出流 |

---

## 配置

### 配置文件位置

- 账户配置: `~/.kiro-proxy/config.json`
- 令牌缓存: `~/.aws/sso/cache/`

### 配置导入/导出

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/config/export` | GET | 导出配置 |
| `/api/config/import` | POST | 导入配置 |
