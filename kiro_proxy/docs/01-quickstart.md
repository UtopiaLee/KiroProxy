# 快速开始

## 安装

### 选项1：下载预编译二进制文件

从[发布页面](https://github.com/petehsu/KiroProxy/releases)下载适合您平台的软件包：

- **Windows**: `kiro-proxy-windows.zip`
- **macOS**: `kiro-proxy-macos.zip`
- **Linux**: `kiro-proxy-linux.tar.gz`

解压后双击运行。

### 选项2：从源代码运行

```bash
# 克隆项目
git clone https://github.com/petehsu/KiroProxy.git
cd KiroProxy

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行（默认端口8080）
python run.py

# 指定端口
python run.py 8081
```

启动后，在浏览器中打开 http://localhost:8080。

---

## 获取Kiro账户

KiroProxy需要Kiro账户令牌才能工作。有两种方式获取：

### 选项1：在线登录（推荐）

1. 打开Web UI，点击"账户"标签页
2. 点击"在线登录"按钮
3. 选择登录方式：
   - **Google** - 使用Google账户
   - **GitHub** - 使用GitHub账户
   - **AWS** - 使用AWS Builder ID
4. 在浏览器弹窗中完成授权
5. 账户自动添加到代理

### 选项2：扫描本地令牌

如果您已经登录过Kiro IDE：

1. 打开Kiro IDE，确保已登录
2. 返回Web UI，点击"扫描令牌"
3. 系统扫描 `~/.aws/sso/cache/` 目录
4. 选择要添加的令牌文件

---

## 配置AI客户端

### Claude Code（VSCode插件）

这是推荐的方法。工具调用已验证可用。

1. 安装Claude Code插件
2. 打开设置，添加自定义提供商：

```
名称: Kiro Proxy
API提供商: Anthropic
API密钥: any（任何值都可以）
基础URL: http://localhost:8080
模型: claude-sonnet-4
```

3. 选择Kiro Proxy作为当前提供商

### Codex CLI

OpenAI官方命令行工具。

```bash
# 安装
npm install -g @openai/codex

# 配置 (~/.codex/config.toml)
model = "gpt-4o"
model_provider = "kiro"

[model_providers.kiro]
name = "Kiro Proxy"
base_url = "http://localhost:8080/v1"
```

### 其他兼容客户端

任何支持OpenAI或Anthropic API的客户端都可以使用：

- **基础URL**: `http://localhost:8080` 或 `http://localhost:8080/v1`
- **API密钥**: 任何值（代理不验证）
- **模型**: 见下表模型映射

---

## 模型映射

| Kiro模型 | 能力 | 可用名称 |
|-----------|------|---------------------|
| `claude-sonnet-4` | ⭐⭐⭐ 推荐 | `gpt-4o`, `gpt-4`, `sonnet` |
| `claude-sonnet-4.5` | ⭐⭐⭐⭐ 更强 | `gemini-1.5-pro` |
| `claude-haiku-4.5` | ⚡ 快速 | `gpt-4o-mini`, `gpt-3.5-turbo`, `haiku` |
| `claude-opus-4.5` | ⭐⭐⭐⭐⭐ 最强 | `o1`, `o1-preview`, `opus` |
| `auto` | 🤖 自动 | `auto` |

> 💡 **提示**: 不确定使用哪个模型？使用 `claude-sonnet-4` 或 `gpt-4o`，性价比最高。
