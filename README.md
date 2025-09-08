
# 安装/更新打包器

## 简介

这是一个简单的安装/更新器解决方案，它允许您轻松分发和更新应用程序文件。用户只需运行一个可执行文件，程序会自动检测是首次安装还是后续更新，并执行相应的操作。

### 主要功能

- **首次安装**：用户选择安装路径，程序安装所有文件
- **后续更新**：自动检测已有安装，询问用户是否更新
- **智能更新**：通过文件哈希比较，只更新有变化的文件
- **自动清理**：安装/更新完成后自动删除安装器
- **路径记忆**：记住上次安装路径，简化更新流程
- **文件忽略**：支持两种忽略规则：始终忽略和更新忽略

## 项目结构

```
MyApp/
├── source_files/         # 需要安装/更新的文件
│   ├── app1.exe
│   ├── app2.exe
│   ├── config.ini
│   └── data.txt
├── .installignore        # 忽略文件规则
├── installer.py          # 安装器程序
├── build.py              # 构建脚本
└── README.md             # 说明文档
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

## 文件忽略功能

我们支持两种类型的文件忽略规则：

### 1. 始终忽略 (ALWAYS)
- 安装和更新时都忽略
- 这些文件不会包含在安装包中
- 格式：`ALWAYS: <规则>`

### 2. 更新忽略 (UPDATE)
- 只在更新时忽略
- 安装时会包含这些文件
- 更新时不会覆盖这些文件
- 格式：`UPDATE: <规则>`

### 忽略文件格式 (`.installignore`)

```
# 始终忽略规则
ALWAYS: *.log
ALWAYS: temp/

# 更新忽略规则
UPDATE: user_settings.ini
UPDATE: config.ini

# 没有前缀的行视为始终忽略
*.tmp
backups/
```

### 使用场景

1. **始终忽略**：
   - 临时文件、日志文件等不需要包含在安装包中
   - 开发环境特定的配置文件
   - 示例文件（只提供默认配置）

2. **更新忽略**：
   - 用户配置文件（保留用户自定义设置）
   - 本地缓存文件
   - 用户生成的数据文件

### 构建日志示例

```
加载忽略规则:
  始终忽略: ['*.log', 'temp/', '*.tmp', 'backups/']
  更新忽略: ['user_settings.ini', 'config.ini']
忽略: app.log (始终忽略)
忽略: temp/temp_file.tmp (始终忽略)
✓ 已添加: app.exe (哈希: a1b2c3d4...)
✓ 已添加: config.ini (哈希: e5f6g7h8...)
✓ 已创建文件清单: file_manifest.json
✓ 已保存忽略规则: ignore_rules.json
构建安装器...
...
构建完成! 请查看 dist 目录中的 installer.exe
```

### 更新日志示例

```
检测到已有安装，将进行更新...
目标目录: C:\Program Files\MyApp
操作类型: 更新
处理文件: user_settings.ini
✗ 忽略: user_settings.ini (更新忽略)
处理文件: config.ini
✗ 忽略: config.ini (更新忽略)
处理文件: app.exe
✓ 更新完成: app.exe
操作完成! 安装了 0 个文件, 更新了 1 个文件
安装器将在2秒后自动删除...
```

## 构建脚本说明

`build.py` 脚本会自动：

1. 扫描 `source_files` 目录中的所有文件
2. 应用 `.installignore` 规则过滤文件
3. 计算每个文件的 MD5 哈希值
4. 创建文件清单 `file_manifest.json`
5. 保存忽略规则 `ignore_rules.json`
6. 构建安装器 `installer.exe`

## 注意事项

1. 确保 `source_files` 目录中的所有文件都是最新版本
2. 每次更新文件后都需要重新运行 `build.py`
3. 安装器会自动删除自身，无需用户手动清理
4. 使用 `.installignore` 文件排除不需要的文件
5. 忽略规则支持通配符 `*` 和 `?`，以及目录匹配（以 `/` 结尾）

## 常见问题

### Q: 为什么某些文件没有被包含在安装包中？

A: 检查是否被 `ALWAYS:` 规则或没有前缀的规则忽略

### Q: 为什么更新时某些文件没有被更新？

A: 检查是否被 `UPDATE:` 规则忽略

### Q: 如何忽略整个目录？

A: 在规则末尾添加 `/`：
```
ALWAYS: logs/
```

### Q: 如何强制包含被忽略的文件？

A: 删除对应的忽略规则

### Q: 忽略规则优先级是什么？

A: 规则优先级：
1. 始终忽略规则
2. 更新忽略规则（仅在更新时应用）

### Q: 构建过程中出现错误怎么办？

A: 检查构建日志中的错误信息，确保：
- `source_files` 目录存在且包含文件
- 所有文件路径正确
- 忽略规则格式正确

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
- **File Ignoring**: Supports two ignore types: Always Ignore and Update Ignore

## Project Structure

```
MyApp/
├── source_files/         # Files to be installed/updated
│   ├── app1.exe
│   ├── app2.exe
│   ├── config.ini
│   └── data.txt
├── .installignore        # File ignoring rules
├── installer.py          # Installer program
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

## File Ignoring Feature

We support two types of file ignoring rules:

### 1. Always Ignore (ALWAYS)
- Ignored during both installation and update
- These files are not included in the installation package
- Format: `ALWAYS: <pattern>`

### 2. Update Ignore (UPDATE)
- Ignored only during updates
- Included during first installation
- Not overwritten during updates
- Format: `UPDATE: <pattern>`

### Ignore File Format (`.installignore`)

```
# Always ignore rules
ALWAYS: *.log
ALWAYS: temp/

# Update ignore rules
UPDATE: user_settings.ini
UPDATE: config.ini

# Lines without prefix are treated as always ignore
*.tmp
backups/
```

### Usage Scenarios

1. **Always Ignore**:
   - Temporary files, log files that shouldn't be included
   - Development-specific configuration files
   - Example files (only provide default configuration)

2. **Update Ignore**:
   - User configuration files (preserve user customizations)
   - Local cache files
   - User-generated data files

### Build Log Example

```
Loading ignore patterns:
  Always ignore: ['*.log', 'temp/', '*.tmp', 'backups/']
  Update ignore: ['user_settings.ini', 'config.ini']
Ignoring: app.log (Always ignore)
Ignoring: temp/temp_file.tmp (Always ignore)
✓ Added: app.exe (Hash: a1b2c3d4...)
✓ Added: config.ini (Hash: e5f6g7h8...)
✓ Created file manifest: file_manifest.json
✓ Saved ignore rules: ignore_rules.json
Building installer...
...
Build complete! Check installer.exe in dist directory
```

### Update Log Example

```
Detected existing installation, will perform update...
Target directory: C:\Program Files\MyApp
Operation type: Update
Processing file: user_settings.ini
✗ Ignored: user_settings.ini (Update ignore)
Processing file: config.ini
✗ Ignored: config.ini (Update ignore)
Processing file: app.exe
✓ Updated: app.exe
Operation complete! Installed 0 files, updated 1 file
Installer will self-delete in 2 seconds...
```

## Build Script Explanation

The `build.py` script automatically:

1. Scans all files in the `source_files` directory
2. Applies `.installignore` rules to filter files
3. Calculates MD5 hash for each file
4. Creates file manifest `file_manifest.json`
5. Saves ignore rules `ignore_rules.json`
6. Builds the installer `installer.exe`

## Notes

1. Ensure all files in the `source_files` directory are up-to-date
2. You need to rerun `build.py` after each file update
3. The installer automatically deletes itself, no manual cleanup needed
4. Use `.installignore` file to exclude unnecessary files
5. Ignore rules support wildcards `*` and `?`, and directory matching (ending with `/`)

## FAQ

### Q: Why are some files not included in the installation package?

A: Check if these files are covered by `ALWAYS:` rules or rules without prefix

### Q: Why are some files not updated during update?

A: Check if these files are covered by `UPDATE:` rules

### Q: How to ignore an entire directory?

A: Add `/` at the end of the rule:
```
ALWAYS: logs/
```

### Q: How to force include ignored files?

A: Remove the corresponding ignore rule

### Q: What is the priority of ignore rules?

A: Rule priority:
1. Always ignore rules
2. Update ignore rules (applied only during updates)

### Q: What to do if build fails?

A: Check the error messages in the build log, ensure:
- `source_files` directory exists and contains files
- All file paths are correct
- Ignore rules are properly formatted
