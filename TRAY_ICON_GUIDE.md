# 系统托盘快捷键功能指南

## 概述

KiroProxy 现已支持系统托盘集成，在 Windows、macOS 和 Linux 上都能显示快捷键。这使得用户可以更方便地访问服务功能。

## 功能特性

### 系统托盘图标
- **Windows 任务栏**：在系统托盘区域显示 KiroProxy 图标
- **macOS Dock**：在 Dock 栏显示应用图标
- **Linux 系统托盘**：在系统托盘显示图标

### 托盘菜单选项
右键点击托盘图标可以访问以下功能：

1. **显示窗口** - 恢复主窗口
2. **打开浏览器** - 直接打开 Web UI
3. **复制URL** - 复制服务地址到剪贴板
4. **启动服务** - 启动 API 服务
5. **停止服务** - 停止 API 服务
6. **退出** - 完全退出应用

### 窗口最小化
- 点击窗口的最小化按钮会将窗口收起到托盘
- 点击托盘图标的"显示窗口"选项可以恢复窗口
- 关闭窗口按钮现在会最小化到托盘而不是退出应用

## 安装依赖

系统托盘功能需要以下依赖：

```bash
pip install pystray>=0.19.0 Pillow>=9.0.0
```

这些依赖已经添加到 `requirements.txt` 中。

## 使用方式

### 开发环境
```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python run.py
```

### 打包应用
```bash
# 使用 PyInstaller 打包
pyinstaller KiroProxy.spec
```

打包配置已在 `KiroProxy.spec` 中更新，包含了 `pystray` 和 `Pillow` 的隐藏导入。

## 平台特定说明

### Windows
- 托盘图标显示在系统托盘区域（右下角）
- 右键点击图标显示菜单
- 左键点击图标可以显示/隐藏窗口

### macOS
- 托盘图标显示在菜单栏（右上角）
- 点击图标显示菜单
- 支持 Dock 集成

### Linux
- 托盘图标显示在系统托盘（取决于桌面环境）
- 右键点击图标显示菜单
- 需要系统托盘支持（大多数现代桌面环境都支持）

## 故障排除

### 托盘图标不显示
1. 确保已安装 `pystray` 和 `Pillow`
2. 检查系统托盘是否启用
3. 查看控制台输出中的错误信息

### 菜单选项不工作
1. 确保服务正在运行
2. 检查端口是否正确
3. 查看网络连接

### 窗口无法恢复
- 使用托盘菜单中的"显示窗口"选项
- 或右键点击托盘图标选择"显示窗口"

## 技术实现

### 核心类：StartupWindow
位置：`kiro_proxy/startup_window.py`

主要方法：
- `create_tray_icon()` - 创建系统托盘图标
- `create_icon_image()` - 生成托盘图标图像
- `show_from_tray()` - 从托盘显示窗口
- `hide()` - 隐藏窗口到托盘

### 图标设计
- 蓝色圆形背景（RGB: 52, 152, 219）
- 白色 K 字母（代表 Kiro）
- 64x64 像素分辨率

## 更新日志

### v1.7.17
- ✨ 添加系统托盘集成
- ✨ 支持 Windows、macOS 和 Linux
- ✨ 托盘菜单快捷功能
- 🔧 改进窗口最小化行为
- 📦 更新依赖：pystray、Pillow

## 相关文件

- `kiro_proxy/startup_window.py` - 启动窗口和托盘实现
- `requirements.txt` - 项目依赖
- `KiroProxy.spec` - PyInstaller 打包配置
