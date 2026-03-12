# KPI v1.7.16 发布说明

## 发布概述

KPI（Kiro API Proxy）v1.7.16 是一个功能完整的API反向代理服务器，支持多个主流AI服务提供商。本版本包含完整的中文文档和多平台可执行文件。

## 新增内容

### 文档
- ✅ 完整的中文文档翻译
  - 快速开始指南 (01-quickstart.md)
  - 功能特性说明 (02-features.md)
  - 常见问题解答 (03-faq.md)
  - API参考文档 (04-api.md)
  - 服务器部署指南 (05-server-deploy.md)
  - 捕获指南 (CAPTURE_GUIDE_CN.md)
  - 使用指南 (USAGE_CN.md)

### 可执行文件
- ✅ Windows x86_64 (.exe 和 .zip)
- ✅ macOS x86_64 (二进制和 .zip)
- ✅ Linux x86_64 (二进制、.tar.gz、.deb、.rpm)

## 下载

所有文件可从 [GitHub Release 页面](https://github.com/UtopiaLee/KiroProxy/releases/tag/v1.7.16) 下载。

### 文件列表

| 平台 | 文件名 | 类型 | 说明 |
|------|--------|------|------|
| **Windows** | `KPI-1.7.16-windows-x86_64.exe` | 可执行文件 | 独立可执行文件，无需依赖 |
| | `KPI-1.7.16-windows-x86_64.zip` | 压缩包 | 包含可执行文件 |
| **macOS** | `KPI-1.7.16-macos-x86_64` | 可执行文件 | 独立二进制文件 |
| | `KPI-1.7.16-macos-x86_64.zip` | 压缩包 | 包含可执行文件 |
| **Linux** | `KPI-1.7.16-linux-x86_64` | 可执行文件 | 独立二进制文件 |
| | `KPI-1.7.16-linux-x86_64.tar.gz` | 压缩包 | 包含可执行文件 |
| | `kpi_1.7.16_amd64.deb` | Debian包 | 适用于 Ubuntu/Debian |
| | `kpi-1.7.16-1.x86_64.rpm` | RPM包 | 适用于 Fedora/RHEL/CentOS |

## 快速开始

### Windows
```bash
# 下载 KPI-1.7.16-windows-x86_64.exe
# 直接双击运行或在命令行执行
KPI-1.7.16-windows-x86_64.exe
```

### macOS
```bash
# 下载并解压
unzip KPI-1.7.16-macos-x86_64.zip

# 赋予执行权限
chmod +x KPI-1.7.16-macos-x86_64

# 运行
./KPI-1.7.16-macos-x86_64
```

### Linux - 二进制方式
```bash
# 下载
wget https://github.com/UtopiaLee/KiroProxy/releases/download/v1.7.16/KPI-1.7.16-linux-x86_64

# 赋予执行权限
chmod +x KPI-1.7.16-linux-x86_64

# 运行
./KPI-1.7.16-linux-x86_64
```

### Linux - 包管理器方式

**Debian/Ubuntu:**
```bash
wget https://github.com/UtopiaLee/KiroProxy/releases/download/v1.7.16/kpi_1.7.16_amd64.deb
sudo dpkg -i kpi_1.7.16_amd64.deb
kpi
```

**Fedora/RHEL/CentOS:**
```bash
wget https://github.com/UtopiaLee/KiroProxy/releases/download/v1.7.16/kpi-1.7.16-1.x86_64.rpm
sudo rpm -i kpi-1.7.16-1.x86_64.rpm
kpi
```

## 主要功能

### 多协议支持
- OpenAI API (GPT-4, GPT-3.5 等)
- Anthropic Claude API
- Google Gemini API

### 高级特性
- 完整的工具调用支持
- 多账户轮换机制
- 自动令牌刷新
- 请求缓存
- 速率限制管理

### 管理界面
- Web UI 仪表板
- 实时请求监控
- 日志查看
- 配置管理
- 性能统计

### 多语言支持
- 中文 (简体)
- English

## 系统要求

- **Windows**: Windows 7 或更高版本
- **macOS**: macOS 10.13 或更高版本
- **Linux**: 任何现代 Linux 发行版

## 配置

首次运行时，KPI 会在以下位置创建配置文件：

- **Windows**: `%APPDATA%\KPI\config.json`
- **macOS**: `~/.kpi/config.json`
- **Linux**: `~/.kpi/config.json`

配置示例：
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
    }
  }
}
```

## 文档

- 📖 [快速开始](https://github.com/UtopiaLee/KiroProxy/blob/main/kiro_proxy/docs/01-quickstart.md)
- 📖 [功能特性](https://github.com/UtopiaLee/KiroProxy/blob/main/kiro_proxy/docs/02-features.md)
- 📖 [常见问题](https://github.com/UtopiaLee/KiroProxy/blob/main/kiro_proxy/docs/03-faq.md)
- 📖 [API参考](https://github.com/UtopiaLee/KiroProxy/blob/main/kiro_proxy/docs/04-api.md)
- 📖 [部署指南](https://github.com/UtopiaLee/KiroProxy/blob/main/kiro_proxy/docs/05-server-deploy.md)
- 📖 [使用指南](https://github.com/UtopiaLee/KiroProxy/blob/main/USAGE_CN.md)

## 已知问题

无已知问题。

## 更新日志

### v1.7.16
- ✨ 添加完整的中文文档
- ✨ 发布多平台可执行文件 (KPI)
- 🐛 修复若干小问题
- 📚 改进文档和示例

## 支持

- 🐛 [报告问题](https://github.com/UtopiaLee/KiroProxy/issues)
- 💬 [讨论](https://github.com/UtopiaLee/KiroProxy/discussions)
- 📧 联系开发者

## 许可证

MIT License - 详见 [LICENSE](https://github.com/UtopiaLee/KiroProxy/blob/main/LICENSE)

## 致谢

感谢所有贡献者和用户的支持！

---

**发布日期**: 2026年3月12日  
**版本**: v1.7.16  
**项目**: [KiroProxy](https://github.com/UtopiaLee/KiroProxy)
