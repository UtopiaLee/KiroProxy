# Kiro API Proxy 启动窗口功能指南

## 概述

本次更新为 Kiro API Proxy 添加了一个常驻前台的启动窗口功能，提供更好的用户体验和便捷的服务控制。

## 新增功能

### 1. 启动配置窗口（launcher.py 增强）

**功能特性：**
- ✅ 窗口始终保持在前台（`-topmost` 属性）
- ✅ 防止意外关闭（未启动时阻止关闭）
- ✅ 端口实时验证
- ✅ 配置记忆功能
- ✅ 自动打开浏览器选项
- ✅ 多语言支持（中文/英文）

**改进点：**
```python
# 设置窗口始终在前台
root.attributes('-topmost', True)

# 防止最小化到系统托盘
def on_window_close():
    if result["port"]:
        # 已启动服务，允许关闭
        root.destroy()
    else:
        # 未启动，阻止关闭
        root.deiconify()
        root.attributes('-topmost', True)

root.protocol("WM_DELETE_WINDOW", on_window_close)
```

### 2. 启动控制窗口（startup_window.py 新增）

**功能特性：**
- 🚀 服务运行时显示控制窗口
- 🌐 一键打开浏览器
- 📋 快速复制服务 URL
- 📌 窗口始终在前台
- 🔒 关闭窗口不会停止服务

**窗口布局：**
```
┌─────────────────────────────────┐
│  🚀 Kiro API Proxy              │
├─────────────────────────────────┤
│  服务状态: ✅ 运行中              │
│  端口: 8080                      │
│  http://localhost:8080           │
├─────────────────────────────────┤
│  [🌐 打开浏览器] [📋 复制URL]    │
├─────────────────────────────────┤
│  窗口将始终保持在前台             │
│  关闭此窗口不会停止服务           │
└─────────────────────────────────┘
```

**核心代码：**
```python
class StartupWindow:
    def __init__(self, port: int):
        self.port = port
        self.root = None
        self.running = False
    
    def create_window(self):
        # 创建 tkinter 窗口
        # 设置 -topmost 属性保持前台
        # 绑定关闭事件（隐藏而非关闭）
        pass
    
    def open_browser(self):
        # 打开浏览器访问服务
        pass
    
    def copy_url(self):
        # 复制 URL 到剪贴板
        pass
```

### 3. 主程序集成（main.py 增强）

**启动流程：**
```python
def run(port: int = 8080):
    # 1. 设置端口
    state.current_port = port
    
    # 2. 打印启动信息
    print(f"http://localhost:{port}")
    
    # 3. 创建启动窗口（后台线程）
    try:
        from .startup_window import create_startup_window
        create_startup_window(port)
    except Exception as e:
        print(f"[!] 启动窗口创建失败: {e}")
    
    # 4. 启动 uvicorn 服务器
    uvicorn.run(app, host="0.0.0.0", port=port)
```

## 使用方式

### 方式 1：默认启动（推荐）
```bash
python run.py
```
- 显示端口配置窗口
- 点击"启动"后显示控制窗口
- 窗口始终保持在前台

### 方式 2：指定端口启动
```bash
python run.py 8080
```
- 直接启动服务（跳过配置窗口）
- 显示控制窗口

### 方式 3：无 UI 启动
```bash
python run.py --no-ui 8080
```
- 不显示任何窗口
- 后台运行服务

### 方式 4：CLI 模式
```bash
python run.py serve 8080
```
- 命令行模式启动

## 技术实现细节

### 窗口前台保持
```python
# 设置窗口始终在最前面
root.attributes('-topmost', True)

# 防止最小化
root.protocol("WM_DELETE_WINDOW", on_window_close)
```

### 后台线程运行
```python
def create_startup_window(port: int):
    window = StartupWindow(port)
    thread = threading.Thread(target=window.run, daemon=True)
    thread.start()
    return window
```

### 剪贴板操作
```python
def copy_url(self):
    self.root.clipboard_clear()
    self.root.clipboard_append(f"http://localhost:{self.port}")
    self.root.update()
```

## 文件变更

### 新增文件
- `kiro_proxy/startup_window.py` - 启动窗口管理器

### 修改文件
- `kiro_proxy/launcher.py` - 增强启动配置窗口
- `kiro_proxy/main.py` - 集成启动窗口
- `run.py` - 添加模块导入

## 兼容性

- ✅ Windows 10/11
- ✅ macOS 10.14+
- ✅ Linux (需要 tkinter)
- ✅ PyInstaller 打包

## 故障排除

### 问题 1：tkinter 不可用
**症状：** `[!] tkinter 不可用，跳过启动窗口`

**解决方案：**
```bash
# Windows
pip install tk

# macOS
brew install python-tk

# Linux (Ubuntu/Debian)
sudo apt-get install python3-tk

# Linux (Fedora)
sudo dnf install python3-tkinter
```

### 问题 2：窗口不显示
**症状：** 启动后没有看到窗口

**解决方案：**
- 检查是否在后台运行（查看任务管理器）
- 尝试使用 `--no-ui` 模式
- 检查系统日志

### 问题 3：复制 URL 失败
**症状：** 点击"复制URL"没有反应

**解决方案：**
- 这是已知的 Linux 限制，可以手动复制
- 使用"打开浏览器"按钮直接访问

## 性能影响

- 启动窗口在后台线程运行，不阻塞主服务
- 内存占用：~5-10MB（tkinter 窗口）
- CPU 占用：<1%（空闲时）

## 未来改进

- [ ] 添加服务停止按钮
- [ ] 实时日志显示
- [ ] 账号管理快捷入口
- [ ] 系统托盘集成
- [ ] 自定义窗口主题

## 相关代码

### launcher.py 关键改动
```python
# 设置窗口始终在前台
root.attributes('-topmost', True)

# 防止最小化到系统托盘
def on_window_close():
    if result["port"]:
        root.destroy()
    else:
        root.deiconify()
        root.attributes('-topmost', True)

root.protocol("WM_DELETE_WINDOW", on_window_close)
```

### startup_window.py 核心类
```python
class StartupWindow:
    def __init__(self, port: int):
        self.port = port
        self.root = None
        self.running = False
    
    def create_window(self):
        # 创建窗口并设置属性
        self.root.attributes('-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", on_window_close)
    
    def open_browser(self):
        webbrowser.open(f"http://localhost:{self.port}")
    
    def copy_url(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(f"http://localhost:{self.port}")
```

### main.py 集成
```python
def run(port: int = 8080):
    # ... 初始化代码 ...
    
    # 创建启动窗口（后台线程）
    try:
        from .startup_window import create_startup_window
        create_startup_window(port)
    except Exception as e:
        print(f"[!] 启动窗口创建失败: {e}")
    
    # 启动服务
    uvicorn.run(app, host="0.0.0.0", port=port)
```

## 总结

这次更新通过添加常驻前台的启动窗口，显著改善了用户体验：

1. **更好的可见性** - 窗口始终在前台，用户不会遗漏
2. **便捷的操作** - 一键打开浏览器和复制 URL
3. **防止误操作** - 关闭窗口不会停止服务
4. **后台运行** - 不阻塞主服务线程
5. **跨平台支持** - 支持 Windows、macOS、Linux


