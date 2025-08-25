import os
import sys
import shutil
import hashlib
import json
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import fnmatch  # 添加这行

def calculate_file_hash(filepath):
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"计算文件哈希时出错 {filepath}: {e}")
        return None

def get_embedded_files():
    """获取嵌入的文件列表及其哈希值"""
    if hasattr(sys, '_MEIPASS'):
        # 如果是打包后的exe，从临时目录读取
        manifest_path = os.path.join(sys._MEIPASS, "file_manifest.json")
    else:
        # 如果是脚本模式，从当前目录读取
        manifest_path = os.path.join(os.path.dirname(__file__), "file_manifest.json")
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载文件清单时出错: {e}")
        return {}

def get_ignore_rules():
    """获取忽略规则"""
    if hasattr(sys, '_MEIPASS'):
        # 如果是打包后的exe，从临时目录读取
        rules_path = os.path.join(sys._MEIPASS, "ignore_rules.json")
    else:
        # 如果是脚本模式，从当前目录读取
        rules_path = os.path.join(os.path.dirname(__file__), "ignore_rules.json")
    
    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            rules = json.load(f)
            # 确保规则列表是列表类型
            if not isinstance(rules.get("always"), list):
                rules["always"] = []
            if not isinstance(rules.get("update"), list):
                rules["update"] = []
            return rules
    except Exception as e:
        print(f"加载忽略规则时出错: {e}")
        return {
            "always": [],
            "update": []
        }

def get_last_install_path():
    """获取上次安装路径"""
    config_path = os.path.join(os.path.expanduser("~"), ".myapp_install_path")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except:
        return None

def save_install_path(path):
    """保存安装路径"""
    config_path = os.path.join(os.path.expanduser("~"), ".myapp_install_path")
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(path)
    except:
        pass

def select_install_path(default_path=None):
    """让用户选择安装路径（仅用于首次安装）"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 如果没有默认路径，使用当前目录
    if not default_path:
        default_path = os.getcwd()
    
    # 创建自定义对话框
    class InstallDialog(tk.Toplevel):
        def __init__(self, parent, default_path):
            super().__init__(parent)
            self.title("选择安装位置")
            self.geometry("500x300")
            self.resizable(False, False)
            self.parent = parent
            self.result = None
            
            # 创建UI元素
            self.create_widgets(default_path)
            
        def create_widgets(self, default_path):
            # 标题
            tk.Label(self, text="请选择安装位置", font=("Arial", 14)).pack(pady=10)
            
            # 当前路径显示
            self.path_var = tk.StringVar(value=default_path)
            tk.Label(self, text="安装路径:").pack(anchor="w", padx=20, pady=(10, 0))
            
            path_frame = tk.Frame(self)
            path_frame.pack(fill="x", padx=20, pady=5)
            
            self.path_entry = tk.Entry(path_frame, textvariable=self.path_var, width=50)
            self.path_entry.pack(side="left", fill="x", expand=True)
            
            browse_btn = tk.Button(path_frame, text="浏览...", command=self.browse_path)
            browse_btn.pack(side="right", padx=(5, 0))
            
            # 安装按钮
            btn_frame = tk.Frame(self)
            btn_frame.pack(fill="x", padx=20, pady=20)
            
            install_btn = tk.Button(btn_frame, text="安装", command=self.install, width=12)
            install_btn.pack(side="right", padx=5)
            
            cancel_btn = tk.Button(btn_frame, text="取消", command=self.cancel, width=10)
            cancel_btn.pack(side="right", padx=5)
            
            # 默认在当前目录安装
            default_btn = tk.Button(self, text="在当前目录安装", command=self.install_current)
            default_btn.pack(side="bottom", pady=10)
            
        def browse_path(self):
            """打开文件夹选择对话框"""
            path = filedialog.askdirectory(title="选择安装位置")
            if path:
                # 更新路径变量和文本框
                self.path_var.set(path)
                self.path_entry.delete(0, tk.END)
                self.path_entry.insert(0, path)
                
        def install_current(self):
            """在当前目录安装"""
            current_path = os.getcwd()
            self.path_var.set(current_path)
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, current_path)
            self.install()
            
        def install(self):
            """开始安装"""
            path = self.path_var.get().strip()
            if not path:
                messagebox.showerror("错误", "请选择安装路径")
                return
                
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except Exception as e:
                    messagebox.showerror("错误", f"无法创建目录: {e}")
                    return
                    
            self.result = path
            self.destroy()
            
        def cancel(self):
            """取消安装"""
            self.result = None
            self.destroy()
    
    # 显示对话框
    dialog = InstallDialog(root, default_path)
    root.wait_window(dialog)
    
    return dialog.result

def should_ignore(path, patterns):
    """检查文件是否应该被忽略"""
    # 检查是否匹配任何忽略模式
    for pattern in patterns:
        # 标准化路径和模式
        normalized_path = path.replace("\\", "/")
        normalized_pattern = pattern.replace("\\", "/")
        
        # 检查通配符匹配
        if fnmatch.fnmatch(normalized_path, normalized_pattern):
            return True
            
        # 检查目录匹配
        if normalized_pattern.endswith('/'):
            # 移除模式末尾的斜杠
            dir_pattern = normalized_pattern.rstrip('/')
            # 检查路径是否以该模式开头
            if normalized_path.startswith(dir_pattern):
                return True
                
        # 检查精确匹配
        if normalized_path == normalized_pattern:
            return True
    return False

def install_or_update_files(install_dir, is_update=False):
    """在指定目录安装或更新文件"""
    # 获取嵌入的文件清单
    embedded_files = get_embedded_files()
    if not embedded_files:
        print("错误: 无法获取文件清单")
        return 0, 0
    
    # 获取忽略规则
    ignore_rules = get_ignore_rules()
    
    # 打印忽略规则用于调试
    print(f"忽略规则: 始终忽略={ignore_rules['always']}, 更新忽略={ignore_rules['update']}")
    
    installed_count = 0
    updated_count = 0
    
    print("=" * 50)
    print(f"目标目录: {install_dir}")
    print(f"操作类型: {'更新' if is_update else '安装'}")
    
    # 处理所有文件
    for file_path, embedded_hash in embedded_files.items():
        # 获取文件的完整路径
        dest_path = os.path.join(install_dir, file_path)
        
        # 打印文件路径用于调试
        print(f"处理文件: {file_path}")

        # 检查是否应该忽略
        if should_ignore(file_path, ignore_rules["always"]):
            print(f"✗ 忽略: {file_path} (始终忽略)")
            continue
            
        if is_update and should_ignore(file_path, ignore_rules["update"]):
            print(f"✗ 忽略: {file_path} (更新忽略)")
            continue

        # 确保目标目录存在
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        # 检查目标文件是否存在
        file_exists = os.path.exists(dest_path)
        
        # 如果文件存在，检查是否需要更新
        if file_exists:
            # 计算目标文件的哈希值
            target_hash = calculate_file_hash(dest_path)
            
            # 如果哈希值相同，跳过更新
            if target_hash and target_hash == embedded_hash:
                print(f"✓ {file_path} 已是最新版本")
                continue
            
            # 需要更新
            action = "更新"
            updated_count += 1
        else:
            # 需要安装
            action = "安装"
            installed_count += 1
        
        # 从安装器中读取嵌入的文件内容
        try:
            # 尝试打开嵌入的文件
            if hasattr(sys, '_MEIPASS'):
                # 如果是打包后的exe，从临时目录读取
                embedded_path = os.path.join(sys._MEIPASS, "source_files", file_path)
            else:
                # 如果是脚本模式，从当前目录读取
                embedded_path = os.path.join(os.path.dirname(__file__), "source_files", file_path)
            
            if os.path.exists(embedded_path):
                # 确保目标目录存在
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # 复制文件
                shutil.copy2(embedded_path, dest_path)
                print(f"✓ {action}完成: {file_path}")
            else:
                print(f"✗ 找不到嵌入的文件: {file_path}，路径: {embedded_path}")
        except Exception as e:
            print(f"✗ {action}文件时出错 {file_path}: {e}")
    
    print("=" * 50)
    return installed_count, updated_count

def create_self_delete_script(install_dir):
    """创建自删除脚本"""
    try:
        if getattr(sys, 'frozen', False):
            # 创建批处理文件来删除安装器自身
            bat_path = os.path.join(install_dir, "delete_installer.bat")
            with open(bat_path, "w", encoding='utf-8') as bat_file:
                bat_file.write("@echo off\n")
                bat_file.write("chcp 65001 >nul\n")  # 设置UTF-8编码
                bat_file.write("echo 正在清理安装文件...\n")
                bat_file.write("timeout /t 2 /nobreak >nul\n")
                bat_file.write(f'del "{sys.executable}"\n')
                bat_file.write("del \"%~f0\"\n")
                bat_file.write("echo 清理完成!\n")
            
            return bat_path
    except Exception as e:
        print(f"创建自删除脚本时出错: {e}")
    
    return None

def main():
    # 隐藏主Tk窗口
    root = tk.Tk()
    root.withdraw()
    
    # 获取上次安装路径
    last_install_path = get_last_install_path()
    print(f"上次安装路径: {last_install_path}")
    
    # 检查是否是更新
    is_update = False
    if last_install_path and os.path.exists(last_install_path):
        # 检查安装目录中是否有文件
        embedded_files = get_embedded_files()
        for file_path in embedded_files.keys():
            if os.path.exists(os.path.join(last_install_path, file_path)):
                is_update = True
                break
    
    # 处理更新流程
    if is_update:
        print("检测到已有安装，将进行更新...")
        
        # 询问用户是否要更新
        response = messagebox.askyesno("更新", f"检测到已安装在: {last_install_path}\n是否要更新应用程序？")
        if not response:
            print("用户取消更新")
            return
        
        # 使用上次安装路径
        install_dir = last_install_path
    else:
        # 如果是首次安装，让用户选择路径
        print("检测到首次安装...")
        install_dir = select_install_path()
        if not install_dir:
            print("安装已取消")
            return
    
    # 保存安装路径
    save_install_path(install_dir)
    
    print(f"目标目录: {install_dir}")
    
    # 安装或更新文件
    installed_count, updated_count = install_or_update_files(install_dir, is_update)
    
    # 显示结果
    if installed_count > 0 or updated_count > 0:
        print(f"操作完成! 安装了 {installed_count} 个文件, 更新了 {updated_count} 个文件")
        
        # 创建自删除脚本并执行
        bat_path = create_self_delete_script(install_dir)
        if bat_path:
            print("安装器将在2秒后自动删除...")
            subprocess.Popen([bat_path], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            print("请手动删除安装器文件")
    else:
        print("没有需要安装或更新的文件")
    
    # 显示完成消息
    messagebox.showinfo("完成", f"操作完成!\n安装了 {installed_count} 个文件\n更新了 {updated_count} 个文件")
    
    # 打开安装目录
    try:
        os.startfile(install_dir)
    except:
        pass

if __name__ == "__main__":
    main()