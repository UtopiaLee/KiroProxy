"""
Kiro Proxy 启动器 - 端口配置 UI
使用 tkinter 创建启动配置界面
"""
import sys
import socket
import json
import webbrowser
import threading
import time
import atexit
from pathlib import Path


# 全局服务器线程引用
_server_thread = None
_server_running = True


def get_config_path() -> Path:
    """获取配置文件路径"""
    if sys.platform == "win32":
        config_dir = Path.home() / "AppData" / "Local" / "KiroProxy"
    else:
        config_dir = Path.home() / ".config" / "kiro-proxy"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "launcher.json"


def load_config() -> dict:
    """加载启动器配置"""
    config_path = get_config_path()
    if config_path.exists():
        try:
            return json.loads(config_path.read_text(encoding="utf-8"))
        except:
            pass
    return {"port": 8080, "remember_port": True, "auto_open_browser": True, "language": "zh"}


def save_config(config: dict):
    """保存启动器配置"""
    config_path = get_config_path()
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")


def check_port_available(port: int) -> bool:
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.bind(("0.0.0.0", port))
            return True
    except OSError:
        return False


def cleanup_server():
    """清理服务器线程"""
    global _server_running
    _server_running = False


def launch_with_ui():
    """显示端口配置 UI 并启动服务器"""
    global _server_thread, _server_running
    
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError:
        print("[!] tkinter 不可用，使用默认端口 8080")
        from kiro_proxy.main import run
        run(8080)
        return
    
    config = load_config()
    port = config.get("port", 8080)
    language = config.get("language", "zh")
    
    # 加载选定的语言
    try:
        from kiro_proxy.web.i18n import load_language
        load_language(language)
    except:
        pass
    
    # 创建端口选择窗口
    root = tk.Tk()
    root.title("Kiro API Proxy - 启动配置")
    root.resizable(False, False)
    
    # 设置窗口大小和位置
    window_width = 450
    window_height = 320

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # 设置样式
    style = ttk.Style()
    if sys.platform == "win32":
        style.theme_use("vista")
    
    # 主框架
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)
    
    # 标题
    title_label = ttk.Label(
        main_frame,
        text="🚀 Kiro API Proxy",
        font=("Segoe UI", 16, "bold") if sys.platform == "win32" else ("SF Pro", 16, "bold")
    )
    title_label.pack(pady=(0, 20))
    
    # 端口配置框架
    port_frame = ttk.LabelFrame(main_frame, text="服务配置", padding=10)
    port_frame.pack(fill="x", pady=10)
    
    # 端口标签和输入框
    ttk.Label(port_frame, text="端口号:", font=("Segoe UI", 10)).pack(side="left", padx=5)
    port_var = tk.StringVar(value=str(port))
    port_entry = ttk.Entry(port_frame, textvariable=port_var, width=10, font=("Segoe UI", 10))
    port_entry.pack(side="left", padx=5)
    
    # 自动打开浏览器复选框
    auto_open_var = tk.BooleanVar(value=config.get("auto_open_browser", True))
    auto_open_check = ttk.Checkbutton(main_frame, text="启动时自动打开浏览器", variable=auto_open_var)
    auto_open_check.pack(pady=10)
    
    # 记住端口复选框
    remember_var = tk.BooleanVar(value=config.get("remember_port", True))
    remember_check = ttk.Checkbutton(main_frame, text="记住端口设置", variable=remember_var)
    remember_check.pack(pady=5)
    
    # 按钮框架
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=20)
    
    def on_start():
        """启动服务"""
        try:
            selected_port = int(port_var.get())
            if selected_port < 1 or selected_port > 65535:
                raise ValueError("端口号必须在 1-65535 之间")
        except ValueError as e:
            print(f"[!] 无效的端口号: {e}")
            return
        
        # 保存配置
        new_config = {
            "port": selected_port,
            "remember_port": remember_var.get(),
            "auto_open_browser": auto_open_var.get(),
            "language": language
        }
        save_config(new_config)
        
        # 关闭配置窗口
        root.destroy()
        
        # 启动服务
        from kiro_proxy.main import run
        run(selected_port)
    
    def on_cancel():
        """取消启动"""
        root.destroy()
        sys.exit(0)
    
    start_btn = ttk.Button(button_frame, text="启动服务", command=on_start, width=15)
    start_btn.pack(side="left", padx=5)
    
    cancel_btn = ttk.Button(button_frame, text="取消", command=on_cancel, width=15)
    cancel_btn.pack(side="left", padx=5)
    
    # 设置窗口始终在前台
    root.attributes('-topmost', True)
    
    # 运行窗口
    root.mainloop()



if __name__ == "__main__":
    launch_with_ui()
