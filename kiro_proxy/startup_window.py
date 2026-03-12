"""
Kiro Proxy 启动窗口 - 服务运行时的控制窗口
提供启动/停止按钮、系统托盘快捷键、服务状态显示
支持 Windows、macOS 和 Linux
"""
import sys
import threading
import time
import subprocess
import requests
import os
import webbrowser
import platform
from pathlib import Path
from io import BytesIO


class StartupWindow:
    """启动窗口管理器"""
    
    def __init__(self, port: int, service_process=None):
        self.port = port
        self.root = None
        self.running = False
        self.service_process = service_process
        self.service_running = True
        self.start_btn = None
        self.stop_btn = None
        self.status_var = None
        self.tray_icon = None
        self.tray_thread = None
        
    def create_window(self):
        """创建启动窗口"""
        try:
            import tkinter as tk
            from tkinter import ttk
        except ImportError:
            print("[!] tkinter 不可用，跳过启动窗口")
            return False
        
        self.root = tk.Tk()
        self.root.title("Kiro API Proxy - 启动控制")
        self.root.resizable(True, True)
        self.root.minsize(300, 200)

        
        # 设置窗口大小
        window_width = 400
        window_height = 280
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置样式
        style = ttk.Style()
        if sys.platform == "win32":
            style.theme_use("vista")
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame,
            text="🚀 Kiro API Proxy",
            font=("Segoe UI", 16, "bold") if sys.platform == "win32" else ("SF Pro", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # 状态信息
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill="x", pady=10)
        
        ttk.Label(status_frame, text="服务状态:", font=("Segoe UI", 10)).pack(side="left")
        self.status_var = tk.StringVar(value="✅ 运行中")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, foreground="green", font=("Segoe UI", 10, "bold"))
        status_label.pack(side="left", padx=10)
        
        # 端口信息
        port_frame = ttk.Frame(main_frame)
        port_frame.pack(fill="x", pady=5)
        
        ttk.Label(port_frame, text=f"端口: {self.port}", font=("Segoe UI", 10)).pack(side="left")
        ttk.Label(port_frame, text=f"http://localhost:{self.port}", foreground="blue", font=("Segoe UI", 9)).pack(side="left", padx=10)
        
        # 功能按钮框架
        func_button_frame = ttk.Frame(main_frame)
        func_button_frame.pack(pady=15)
        
        # 打开浏览器按钮
        open_btn = ttk.Button(func_button_frame, text="🌐 打开浏览器", command=self.open_browser, width=15)
        open_btn.pack(side="left", padx=5)
        
        # 复制URL按钮
        copy_btn = ttk.Button(func_button_frame, text="📋 复制URL", command=self.copy_url, width=12)
        copy_btn.pack(side="left", padx=5)
        
        # 服务控制按钮框架
        control_button_frame = ttk.Frame(main_frame)
        control_button_frame.pack(pady=15)
        
        # 启动按钮 - 根据服务状态设置初始状态
        start_state = "disabled" if self.service_running else "normal"
        self.start_btn = ttk.Button(control_button_frame, text="▶ 启动服务", command=self.start_service, width=15, state=start_state)
        self.start_btn.pack(side="left", padx=5)
        
        # 停止按钮 - 根据服务状态设置初始状态
        stop_state = "normal" if self.service_running else "disabled"
        self.stop_btn = ttk.Button(control_button_frame, text="⏹ 停止服务", command=self.stop_service, width=15, state=stop_state)
        self.stop_btn.pack(side="left", padx=5)
        
        # 提示信息
        hint_label = ttk.Label(
            main_frame,
            text="点击最小化按钮可收起到任务栏\n点击任务栏图标可恢复窗口",
            foreground="gray",
            font=("Segoe UI", 8)
        )
        hint_label.pack(pady=10)
        
        # 设置窗口始终在前台
        self.root.attributes('-topmost', True)
        
        # 处理窗口关闭事件
        def on_window_close():
            """处理窗口关闭事件 - 最小化到托盘而不是退出"""
            self.hide()
        
        # 绑定窗口关闭协议
        self.root.protocol("WM_DELETE_WINDOW", on_window_close)
        
        # 创建系统托盘图标
        self.create_tray_icon()
        
        self.running = True
        return True
    
    def create_tray_icon(self):
        """创建系统托盘图标"""
        try:
            import pystray
            from PIL import Image, ImageDraw
            
            # 创建托盘图标（简单的蓝色圆形）
            icon_image = self.create_icon_image()
            
            # 创建菜单
            menu_items = [
                pystray.MenuItem("显示窗口", self.show_from_tray),
                pystray.MenuItem("打开浏览器", self.open_browser),
                pystray.MenuItem("复制URL", self.copy_url),
                pystray.MenuItem("-", None),
                pystray.MenuItem("启动服务", self.start_service),
                pystray.MenuItem("停止服务", self.stop_service),
                pystray.MenuItem("-", None),
                pystray.MenuItem("退出", self.exit_app),
            ]
            
            # 创建托盘图标
            self.tray_icon = pystray.Icon(
                "KiroProxy",
                icon_image,
                "Kiro API Proxy",
                menu=pystray.Menu(*menu_items)
            )
            
            # 在后台线程中运行托盘图标
            self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            self.tray_thread.start()
            
            print("[✓] 系统托盘图标已创建")
        except ImportError:
            print("[!] pystray 不可用，跳过系统托盘功能")
        except Exception as e:
            print(f"[!] 创建系统托盘图标失败: {e}")
    
    def create_icon_image(self):
        """创建托盘图标图像"""
        try:
            from PIL import Image, ImageDraw
            
            # 创建一个简单的图标（蓝色圆形，中间有白色的 K）
            size = 64
            image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # 绘制蓝色圆形背景
            draw.ellipse([0, 0, size-1, size-1], fill=(52, 152, 219, 255))
            
            # 绘制白色的 K 字母
            # 简单的 K 字形状
            line_width = 3
            margin = 12
            
            # 竖线
            draw.rectangle(
                [margin, margin, margin + line_width, size - margin],
                fill=(255, 255, 255, 255)
            )
            
            # 上斜线
            draw.line(
                [(margin + line_width, margin + 8), (size - margin, margin + 20)],
                fill=(255, 255, 255, 255),
                width=line_width
            )
            
            # 下斜线
            draw.line(
                [(margin + line_width, size // 2), (size - margin, size - margin)],
                fill=(255, 255, 255, 255),
                width=line_width
            )
            
            return image
        except ImportError:
            # 如果 PIL 不可用，返回一个简单的图像
            from PIL import Image
            return Image.new('RGB', (64, 64), color=(52, 152, 219))
    
    def show_from_tray(self, icon=None, item=None):
        """从托盘显示窗口"""
        self.show()
    
    def open_browser(self):
        """打开浏览器 - 支持多平台"""
        try:
            url = f"http://localhost:{self.port}"
            
            # 检查服务是否运行
            if not self.check_service_health():
                if self.status_var:
                    self.status_var.set("❌ 服务未运行，请先启动服务")
                    self.root.after(3000, lambda: self.status_var.set("✅ 运行中" if self.service_running else "⏹ 服务已停止"))
                return
            
            # 多平台支持
            if sys.platform == "win32":
                os.startfile(url)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", url])
            else:
                subprocess.Popen(["xdg-open", url])
            
            if self.status_var:
                self.status_var.set("✅ 浏览器已打开")
                self.root.after(2000, lambda: self.status_var.set("✅ 运行中" if self.service_running else "⏹ 服务已停止"))
        except Exception as e:
            print(f"[!] 打开浏览器失败: {e}")
            if self.status_var:
                self.status_var.set(f"❌ 打开失败: {str(e)[:15]}")
                self.root.after(3000, lambda: self.status_var.set("✅ 运行中" if self.service_running else "⏹ 服务已停止"))
    
    def copy_url(self):
        """复制URL到剪贴板 - 支持多平台"""
        try:
            url = f"http://localhost:{self.port}"
            
            # 尝试多种方式复制到剪贴板
            success = False
            
            # 方法1: Tkinter 剪贴板
            try:
                if self.root:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(url)
                    self.root.update()
                    success = True
            except:
                pass
            
            # 方法2: Windows 剪贴板
            if not success and sys.platform == "win32":
                try:
                    import ctypes
                    ctypes.windll.user32.OpenClipboard()
                    ctypes.windll.user32.EmptyClipboard()
                    ctypes.windll.user32.CloseClipboard()
                    
                    import subprocess
                    process = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
                    process.communicate(url.encode('utf-8'))
                    success = True
                except:
                    pass
            
            # 方法3: xclip (Linux)
            if not success and sys.platform.startswith("linux"):
                try:
                    process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
                    process.communicate(url.encode('utf-8'))
                    success = True
                except:
                    pass
            
            # 方法4: pbcopy (macOS)
            if not success and sys.platform == "darwin":
                try:
                    process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                    process.communicate(url.encode('utf-8'))
                    success = True
                except:
                    pass
            
            if success:
                if self.status_var:
                    original_text = self.status_var.get()
                    self.status_var.set("✅ 已复制到剪贴板")
                    self.root.after(2000, lambda: self.status_var.set(original_text))
            else:
                if self.status_var:
                    self.status_var.set("❌ 复制失败")
                    self.root.after(2000, lambda: self.status_var.set("✅ 运行中" if self.service_running else "⏹ 服务已停止"))
        except Exception as e:
            print(f"[!] 复制失败: {e}")
            if self.status_var:
                self.status_var.set("❌ 复制失败")
                self.root.after(2000, lambda: self.status_var.set("✅ 运行中" if self.service_running else "⏹ 服务已停止"))
    
    def check_service_health(self):
        """检查服务是否运行"""
        try:
            response = requests.get(f"http://localhost:{self.port}/api/status", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def start_service(self):
        """启动服务 - 支持多平台"""
        try:
            # 检查服务是否已运行
            if self.check_service_health():
                if self.status_var:
                    self.status_var.set("✅ 服务已运行")
                self.service_running = True
                if self.start_btn:
                    self.start_btn.config(state="disabled")
                if self.stop_btn:
                    self.stop_btn.config(state="normal")
                return
            
            if self.status_var:
                self.status_var.set("⏳ 正在启动服务...")
                self.root.update()
            
            # 启动新的服务进程
            try:
                if sys.platform == "win32":
                    # Windows 上使用 CREATE_NEW_PROCESS_GROUP 避免继承父进程的控制台
                    self.service_process = subprocess.Popen(
                        [sys.executable, "-m", "kiro_proxy.main", str(self.port)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                    )
                else:
                    self.service_process = subprocess.Popen(
                        [sys.executable, "-m", "kiro_proxy.main", str(self.port)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        preexec_fn=os.setsid if hasattr(os, 'setsid') else None
                    )
            except Exception as e:
                print(f"[!] 启动进程失败: {e}")
                if self.status_var:
                    self.status_var.set(f"❌ 启动失败")
                    self.root.after(2000, lambda: self.status_var.set("⏹ 服务已停止"))
                return
            
            # 等待服务启动（最多等待5秒）
            for i in range(5):
                time.sleep(1)
                if self.check_service_health():
                    if self.status_var:
                        self.status_var.set("✅ 服务已启动")
                    self.service_running = True
                    if self.start_btn:
                        self.start_btn.config(state="disabled")
                    if self.stop_btn:
                        self.stop_btn.config(state="normal")
                    return
            
            # 启动超时
            if self.status_var:
                self.status_var.set("❌ 启动超时")
                self.service_running = False
                self.root.after(2000, lambda: self.status_var.set("⏹ 服务已停止"))
        except Exception as e:
            print(f"[!] 启动服务失败: {e}")
            if self.status_var:
                self.status_var.set(f"❌ 启动失败")
                self.root.after(2000, lambda: self.status_var.set("⏹ 服务已停止"))
    
    def stop_service(self):
        """停止服务 - 支持多平台"""
        try:
            if self.status_var:
                self.status_var.set("⏳ 正在停止服务...")
                self.root.update()
            
            if self.service_process and self.service_process.poll() is None:
                try:
                    if sys.platform == "win32":
                        # Windows 上使用进程组停止
                        try:
                            os.kill(self.service_process.pid, 9)
                        except:
                            self.service_process.kill()
                    else:
                        # Unix/Linux/macOS 上使用 terminate
                        try:
                            if hasattr(os, 'killpg'):
                                os.killpg(os.getpgid(self.service_process.pid), 9)
                            else:
                                self.service_process.terminate()
                                self.service_process.wait(timeout=3)
                        except:
                            self.service_process.kill()
                except Exception as e:
                    print(f"[!] 杀死进程失败: {e}")
            
            # 等待服务完全停止
            time.sleep(1)
            
            if self.status_var:
                self.status_var.set("⏹ 服务已停止")
            self.service_running = False
            if self.start_btn:
                self.start_btn.config(state="normal")
            if self.stop_btn:
                self.stop_btn.config(state="disabled")
        except Exception as e:
            print(f"[!] 停止服务失败: {e}")
            if self.status_var:
                self.status_var.set("⏹ 服务已停止")
            self.service_running = False
            if self.start_btn:
                self.start_btn.config(state="normal")
            if self.stop_btn:
                self.stop_btn.config(state="disabled")
    
    def exit_app(self, icon=None, item=None):
        """退出应用"""
        try:
            if self.service_running:
                self.stop_service()
            self.running = False
            if self.tray_icon:
                try:
                    self.tray_icon.stop()
                except:
                    pass
            if self.root:
                try:
                    self.root.quit()
                except:
                    pass
                try:
                    self.root.destroy()
                except:
                    pass
        except Exception as e:
            print(f"[!] 退出失败: {e}")

    
    def run(self):
        """运行窗口主循环"""
        if not self.create_window():
            return
        
        try:
            # 运行 Tkinter 主循环
            self.root.mainloop()
        except Exception as e:
            print(f"[!] 启动窗口错误: {e}")
    
    def show(self):
        """显示窗口"""
        if self.root:
            self.root.deiconify()
            self.root.attributes('-topmost', True)
            self.root.lift()
            self.root.focus()
    
    def hide(self):
        """隐藏窗口到托盘"""
        if self.root:
            self.root.withdraw()


def create_startup_window(port: int, service_process=None):
    """创建并运行启动窗口（在后台线程中）"""
    window = StartupWindow(port, service_process)
    thread = threading.Thread(target=window.run, daemon=True)
    thread.start()
    return window
