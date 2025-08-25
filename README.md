# pyInstallerTool
This is a Python-based packaging tool capable of packaging specified folders into an exe installer.
# 智能安装/更新器

## 简介

这是一个智能安装/更新器解决方案，它允许您轻松分发和更新应用程序文件。用户只需运行一个可执行文件，程序会自动检测是首次安装还是后续更新，并执行相应的操作。

### 主要功能

- **首次安装**：用户选择安装路径，程序安装所有文件
- **后续更新**：自动检测已有安装，询问用户是否更新
- **智能更新**：通过文件哈希比较，只更新有变化的文件
- **自动清理**：安装/更新完成后自动删除安装器
- **路径记忆**：记住上次安装路径，简化更新流程

## 项目结构

```
MyApp/
├── source_files/         # 需要安装/更新的文件
│   ├── app1.exe
│   ├── app2.exe
│   ├── config.ini
│   └── data.txt
├── installer.py           # 安装器程序
├── build.py               # 构建脚本
└── README.md              # 说明文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install pyinstaller
```

### 2. 准备文件

将需要安装/更新的文件放入 `source_files` 目录

### 3. 构建安装器

```bash
python build.py
```

构建完成后，在 `dist` 目录中会生成 `installer.exe`

### 4. 分发安装器

将 `dist/installer.exe` 发送给用户

## 用户使用指南

### 首次安装

1. 运行 `installer.exe`
2. 选择安装路径
3. 程序自动安装所有文件
4. 完成后安装器自动删除

### 后续更新

1. 运行新的 `installer.exe`
2. 程序检测到已有安装，询问是否更新
3. 确认后自动更新有变化的文件
4. 完成后安装器自动删除

## 开发者指南

### 添加新文件

1. 将新文件放入 `source_files` 目录
2. 运行 `python build.py` 重新构建
3. 将新的 `installer.exe` 发送给用户

### 更新文件

1. 修改 `source_files` 目录中的文件
2. 运行 `python build.py` 重新构建
3. 将新的 `installer.exe` 发送给用户

## 构建脚本说明

`build.py` 脚本会自动：

1. 扫描 `source_files` 目录中的所有文件
2. 计算每个文件的 MD5 哈希值
3. 创建文件清单 `file_manifest.json`
4. 构建安装器 `installer.exe`

## 注意事项

1. 确保 `source_files` 目录中的所有文件都是最新版本
2. 每次更新文件后都需要重新运行 `build.py`
3. 安装器会自动删除自身，无需用户手动清理

---

# Smart Installer/Updater

## Introduction

This is a smart installer/updater solution that allows you to easily distribute and update application files. Users only need to run a single executable file, and the program will automatically detect whether it's the first installation or an update, and perform the appropriate actions.

### Key Features

- **First Installation**: User selects installation path, program installs all files
- **Subsequent Updates**: Automatically detects existing installation and asks if user wants to update
- **Smart Update**: Updates only changed files by comparing file hashes
- **Auto Cleanup**: Automatically deletes installer after installation/update
- **Path Memory**: Remembers last installation path to simplify update process

## Project Structure

```
MyApp/
├── source_files/         # Files to be installed/updated
│   ├── app1.exe
│   ├── app2.exe
│   ├── config.ini
│   └── data.txt
├── installer.py           # Installer program
├── build.py               # Build script
└── README.md              # Documentation
```

## Quick Start

### 1. Install Dependencies

```bash
pip install pyinstaller
```

### 2. Prepare Files

Place files to be installed/updated in the `source_files` directory

### 3. Build Installer

```bash
python build.py
```

After building, `installer.exe` will be generated in the `dist` directory

### 4. Distribute Installer

Send `dist/installer.exe` to users

## User Guide

### First Installation

1. Run `installer.exe`
2. Select installation path
3. Program automatically installs all files
4. Installer deletes itself after completion

### Subsequent Updates

1. Run the new `installer.exe`
2. Program detects existing installation and asks if you want to update
3. Confirm to automatically update changed files
4. Installer deletes itself after completion

## Developer Guide

### Adding New Files

1. Place new files in the `source_files` directory
2. Run `python build.py` to rebuild
3. Send the new `installer.exe` to users

### Updating Files

1. Modify files in the `source_files` directory
2. Run `python build.py` to rebuild
3. Send the new `installer.exe` to users

## Build Script Explanation

The `build.py` script automatically:

1. Scans all files in the `source_files` directory
2. Calculates MD5 hash for each file
3. Creates file manifest `file_manifest.json`
4. Builds the installer `installer.exe`

## Notes

1. Ensure all files in the `source_files` directory are up-to-date
2. You need to rerun `build.py` after each file update
3. The installer automatically deletes itself, no manual cleanup needed
