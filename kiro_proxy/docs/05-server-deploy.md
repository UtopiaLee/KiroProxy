# 服务器部署指南

本指南涵盖在各种服务器环境上部署Kiro Proxy。

## 目录

- [选项1：预编译二进制文件（推荐）](#选项1预编译二进制文件推荐)
- [选项2：从源代码运行](#选项2从源代码运行)
- [选项3：Docker部署](#选项3docker部署)
- [账户配置](#账户配置)
- [开机自启](#开机自启)
- [反向代理设置](#反向代理设置)

---

## 选项1：预编译二进制文件（推荐）

最简单的方法，无需依赖。

### Linux (x86_64)

```bash
# 下载最新版本
wget https://github.com/petehsu/KiroProxy/releases/latest/download/KiroProxy-1.7.1-linux-x86_64

# 添加执行权限
chmod +x KiroProxy-1.7.1-linux-x86_64

# 运行
./KiroProxy-1.7.1-linux-x86_64

# 指定端口
./KiroProxy-1.7.1-linux-x86_64 8081
```

### macOS

```bash
# Intel Mac
curl -LO https://github.com/petehsu/KiroProxy/releases/latest/download/KiroProxy-1.7.1-macos-x86_64
chmod +x KiroProxy-1.7.1-macos-x86_64
./KiroProxy-1.7.1-macos-x86_64

# 如果提示未验证的开发者：
xattr -d com.apple.quarantine KiroProxy-1.7.1-macos-x86_64
```

### Windows

```powershell
# PowerShell下载
Invoke-WebRequest -Uri "https://github.com/petehsu/KiroProxy/releases/latest/download/KiroProxy-1.7.1-windows-x86_64.exe" -OutFile "KiroProxy.exe"

# 运行
.\KiroProxy.exe
```

---

## 选项2：从源代码运行

需要Python 3.9+和Git。

```bash
# 克隆项目
git clone https://github.com/petehsu/KiroProxy.git
cd KiroProxy

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行
python run.py

# 指定端口
python run.py 8081
```

### 更新到最新版本

```bash
cd KiroProxy
git pull origin main
pip install -r requirements.txt
```

---

## 选项3：Docker部署

### 使用Dockerfile

创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

VOLUME ["/root/.config/kiro-proxy"]

CMD ["python", "run.py"]
```

构建并运行：

```bash
docker build -t kiro-proxy .
docker run -d -p 8080:8080 -v kiro-data:/root/.config/kiro-proxy --name kiro-proxy kiro-proxy
```

---

## 账户配置

服务器通常没有浏览器。有几种方式添加账户：

### 选项1：远程登录链接（推荐）

1. 在服务器上启动KiroProxy
2. 在本地浏览器中打开 `http://server-ip:8080`
3. 点击"远程登录链接"按钮
4. 复制生成的链接，在本地浏览器中打开
5. 完成Google/GitHub授权
6. 账户自动添加到服务器

### 选项2：导入/导出

**在本地计算机上：**
```bash
# 运行KiroProxy并登录
python run.py

# 导出账户
python run.py accounts export -o accounts.json
```

**在服务器上：**
```bash
# 上传accounts.json然后导入
python run.py accounts import accounts.json
```

### 选项3：手动添加令牌

1. 在本地Kiro IDE中登录
2. 在 `~/.aws/sso/cache/` 目录中找到JSON文件
3. 复制 `accessToken` 和 `refreshToken`

**在服务器上：**
```bash
# 交互式添加
python run.py accounts add
```

---

## 开机自启

### Linux (systemd)

创建 `/etc/systemd/system/kiro-proxy.service`：

```ini
[Unit]
Description=Kiro API Proxy
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/kiro-proxy
ExecStart=/opt/kiro-proxy/KiroProxy
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 启用并启动
sudo systemctl daemon-reload
sudo systemctl enable kiro-proxy
sudo systemctl start kiro-proxy

# 检查状态
sudo systemctl status kiro-proxy

# 查看日志
sudo journalctl -u kiro-proxy -f
```

### Linux (screen/tmux)

```bash
# 使用screen
screen -S kiro
./KiroProxy
# 按Ctrl+A D分离

# 重新连接
screen -r kiro
```

### Windows (任务计划程序)

```powershell
# 创建计划任务（开机自启）
$action = New-ScheduledTaskAction -Execute "C:\KiroProxy\KiroProxy.exe"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount
Register-ScheduledTask -TaskName "KiroProxy" -Action $action -Trigger $trigger -Principal $principal

# 立即启动
Start-ScheduledTask -TaskName "KiroProxy"
```

---

## 反向代理设置

### Nginx

```nginx
server {
    listen 80;
    server_name kiro.example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # SSE支持
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400;
    }
}
```

**启用HTTPS（使用Certbot）：**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d kiro.example.com
```

### Caddy

```caddyfile
kiro.example.com {
    reverse_proxy localhost:8080
}
```

Caddy自动管理HTTPS证书。

---

## 常见问题

### 端口被占用

```bash
# 检查端口使用情况
lsof -i :8080  # Linux/macOS
netstat -ano | findstr :8080  # Windows

# 使用不同端口
./KiroProxy 8081
```

### 防火墙配置

**Ubuntu/Debian (ufw):**
```bash
sudo ufw allow 8080/tcp
```

**CentOS/RHEL (firewalld):**
```bash
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

**Windows:**
```powershell
New-NetFirewallRule -DisplayName "KiroProxy" -Direction Inbound -Port 8080 -Protocol TCP -Action Allow
```

### 查看日志

```bash
# systemd
sudo journalctl -u kiro-proxy -f

# 直接运行
./KiroProxy 2>&1 | tee kiro.log
```
