# KPI 使用指南

KPI（Kiro API Proxy）是一个功能强大的API反向代理服务器，支持多个AI服务提供商。

## 下载和安装

### Windows

1. 从 [GitHub Release](https://github.com/UtopiaLee/KiroProxy/releases) 下载最新版本
2. 选择 `KPI-x.x.x-windows-x86_64.exe` 或 `KPI-x.x.x-windows-x86_64.zip`
3. 直接运行 `.exe` 文件或解压 `.zip` 后运行

### macOS

1. 从 [GitHub Release](https://github.com/UtopiaLee/KiroProxy/releases) 下载最新版本
2. 选择 `KPI-x.x.x-macos-x86_64` 或 `KPI-x.x.x-macos-x86_64.zip`
3. 解压文件：`unzip KPI-x.x.x-macos-x86_64.zip`
4. 赋予执行权限：`chmod +x KPI`
5. 运行：`./KPI`

### Linux

#### 方式1：直接运行二进制文件
```bash
# 下载
wget https://github.com/UtopiaLee/KiroProxy/releases/download/vx.x.x/KPI-x.x.x-linux-x86_64

# 赋予执行权限
chmod +x KPI-x.x.x-linux-x86_64

# 运行
./KPI-x.x.x-linux-x86_64
```

#### 方式2：使用包管理器

**Debian/Ubuntu:**
```bash
wget https://github.com/UtopiaLee/KiroProxy/releases/download/vx.x.x/kpi_x.x.x_amd64.deb
sudo dpkg -i kpi_x.x.x_amd64.deb
kpi
```

**Fedora/RHEL/CentOS:**
```bash
wget https://github.com/UtopiaLee/KiroProxy/releases/download/vx.x.x/kpi-x.x.x-1.x86_64.rpm
sudo rpm -i kpi-x.x.x-1.x86_64.rpm
kpi
```

## 快速开始

### 1. 启动服务

```bash
./KPI
```

默认情况下，服务会在 `http://localhost:8000` 启动。

### 2. 访问Web UI

打开浏览器访问：`http://localhost:8000`

### 3. 配置API密钥

在Web UI中配置您的API密钥：
- OpenAI API Key
- Anthropic API Key
- Google Gemini API Key

### 4. 使用代理

将您的应用程序指向 `http://localhost:8000`，KPI会自动转发请求到相应的AI服务。

## 配置文件

KPI使用 `config.json` 文件进行配置。默认位置：

- **Windows**: `%APPDATA%\KPI\config.json`
- **macOS**: `~/.kpi/config.json`
- **Linux**: `~/.kpi/config.json`

### 配置示例

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": false
  },
  "providers": {
    "openai": {
      "enabled": true,
      "api_key": "sk-..."
    },
    "anthropic": {
      "enabled": true,
      "api_key": "sk-ant-..."
    },
    "gemini": {
      "enabled": true,
      "api_key": "..."
    }
  }
}
```

## 主要功能

### 多协议支持
- OpenAI API
- Anthropic Claude API
- Google Gemini API

### 工具调用
完整支持AI模型的工具调用功能，包括：
- 函数定义
- 工具执行
- 结果回调

### 多账户轮换
支持配置多个账户，自动轮换使用，避免单个账户限流。

### 自动令牌刷新
自动管理API令牌的刷新，无需手动干预。

### Web管理界面
- 实时监控请求
- 查看日志
- 管理配置
- 性能统计

### 多语言支持
- 中文
- English

## 常见问题

### Q: 如何修改监听端口？

A: 编辑 `config.json` 文件，修改 `server.port` 值：

```json
{
  "server": {
    "port": 9000
  }
}
```

### Q: 如何启用调试模式？

A: 编辑 `config.json` 文件，设置 `server.debug` 为 `true`：

```json
{
  "server": {
    "debug": true
  }
}
```

### Q: 支持HTTPS吗？

A: 支持。在 `config.json` 中配置SSL证书：

```json
{
  "server": {
    "ssl": {
      "enabled": true,
      "cert_file": "/path/to/cert.pem",
      "key_file": "/path/to/key.pem"
    }
  }
}
```

### Q: 如何查看日志？

A: 日志文件位置：
- **Windows**: `%APPDATA%\KPI\logs\`
- **macOS**: `~/.kpi/logs/`
- **Linux**: `~/.kpi/logs/`

### Q: 如何在后台运行？

**Windows:**
```bash
start /B KPI.exe
```

**macOS/Linux:**
```bash
nohup ./KPI > kpi.log 2>&1 &
```

或使用 `screen`/`tmux`：
```bash
screen -S kpi
./KPI
# 按 Ctrl+A 然后 D 来分离会话
```

## 性能优化

### 1. 调整工作进程数

```json
{
  "server": {
    "workers": 4
  }
}
```

### 2. 启用缓存

```json
{
  "cache": {
    "enabled": true,
    "ttl": 3600
  }
}
```

### 3. 配置连接池

```json
{
  "connection_pool": {
    "max_size": 100,
    "timeout": 30
  }
}
```

## 安全建议

1. **使用强密码**: 为Web UI设置强密码
2. **启用HTTPS**: 在生产环境中使用SSL/TLS
3. **限制访问**: 配置防火墙规则，只允许信任的IP访问
4. **定期更新**: 及时更新到最新版本
5. **保护密钥**: 不要在代码中硬编码API密钥，使用环境变量

## 更新

### 检查版本

```bash
./KPI --version
```

### 更新到最新版本

1. 从 [GitHub Release](https://github.com/UtopiaLee/KiroProxy/releases) 下载最新版本
2. 备份现有配置文件
3. 替换可执行文件
4. 重启服务

## 获取帮助

- 📖 [完整文档](https://github.com/UtopiaLee/KiroProxy/tree/main/kiro_proxy/docs)
- 🐛 [报告问题](https://github.com/UtopiaLee/KiroProxy/issues)
- 💬 [讨论](https://github.com/UtopiaLee/KiroProxy/discussions)

## 许可证

MIT License - 详见 [LICENSE](https://github.com/UtopiaLee/KiroProxy/blob/main/LICENSE)
