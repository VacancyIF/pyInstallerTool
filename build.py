import os
import shutil
import json
import hashlib
import fnmatch
import PyInstaller.__main__
from pathlib import Path

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

def load_ignore_patterns():
    """加载忽略规则"""
    ignore_file = ".installignore"
    always_ignore = []
    update_ignore = []
    
    if os.path.exists(ignore_file):
        with open(ignore_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # 忽略空行和注释
                if not line or line.startswith("#"):
                    continue
                
                # 处理特殊前缀
                if line.startswith("ALWAYS:"):
                    always_ignore.append(line.replace("ALWAYS:", "").strip())
                elif line.startswith("UPDATE:"):
                    update_ignore.append(line.replace("UPDATE:", "").strip())
                else:
                    # 没有前缀的行视为始终忽略
                    always_ignore.append(line)
    
    # 添加默认忽略规则
    default_ignore = [
        ".DS_Store",  # macOS
        "Thumbs.db",  # Windows
        "desktop.ini" # Windows
    ]
    
    return {
        "always": always_ignore + default_ignore,
        "update": update_ignore
    }

def should_ignore(path, patterns):
    """检查文件是否应该被忽略"""
    # 检查是否匹配任何忽略模式
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
        # 检查目录是否匹配
        if pattern.endswith('/') and path.startswith(pattern.rstrip('/')):
            return True
    return False

def prepare_source_files():
    """准备源文件并创建清单"""
    # 源文件目录
    source_dir = "source_files"
    
    # 检查源文件目录是否存在
    if not os.path.exists(source_dir) or not os.path.isdir(source_dir):
        print(f"错误: 源文件目录 '{source_dir}' 不存在")
        return False
    
    # 加载忽略规则
    ignore_patterns = load_ignore_patterns()
    print(f"加载忽略规则:")
    print(f"  始终忽略: {ignore_patterns['always']}")
    print(f"  更新忽略: {ignore_patterns['update']}")
    
    # 获取所有源文件
    all_files = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            file_path = os.path.join(root, file)
            # 计算相对路径
            rel_path = os.path.relpath(file_path, source_dir)
            
            # 检查是否应该忽略
            if should_ignore(rel_path, ignore_patterns["always"]):
                print(f"忽略: {rel_path} (始终忽略)")
                continue
            
            all_files.append(rel_path)
    
    if not all_files:
        print("错误: 源文件目录中没有文件")
        return False
    
    # 文件清单
    file_manifest = {}
    
    # 计算文件哈希值并创建清单
    for rel_path in all_files:
        src_path = os.path.join(source_dir, rel_path)
        
        # 计算文件哈希值
        file_hash = calculate_file_hash(src_path)
        if not file_hash:
            print(f"警告: 跳过文件 {rel_path}，无法计算哈希值")
            continue
        
        # 添加到文件清单
        file_manifest[rel_path] = file_hash
        print(f"✓ 已添加: {rel_path} (哈希: {file_hash[:8]}...)")
    
    # 保存文件清单
    manifest_path = "file_manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(file_manifest, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 已创建文件清单: {manifest_path}")
    
    # 保存忽略规则
    ignore_path = "ignore_rules.json"
    with open(ignore_path, 'w', encoding='utf-8') as f:
        json.dump(ignore_patterns, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 已保存忽略规则: {ignore_path}")
    
    # 确保所有文件都存在
    for rel_path in all_files:
        if not os.path.exists(os.path.join(source_dir, rel_path)):
            print(f"错误: 文件 {rel_path} 在源文件目录中不存在")
            return False
    
    return True

def build_installer():
    """构建安装器"""
    print("构建安装器...")
    try:
        # 构建参数
        build_args = [
            'installer.py',
            '--onefile',
            '--name=installer',
            '--windowed',  # 使用窗口模式，不显示控制台
            '--add-data=source_files;source_files',
            '--add-data=file_manifest.json;.',
            '--add-data=ignore_rules.json;.',
            '--hidden-import=tkinter',
            '--hidden-import=tkinter.filedialog',
            '--hidden-import=tkinter.messagebox'
        ]
        
        PyInstaller.__main__.run(build_args)
    except Exception as e:
        print(f"构建安装器时出错: {e}")
        return False
    
    return True

def cleanup():
    """清理临时文件"""
    for file_name in ["file_manifest.json", "ignore_rules.json"]:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"清理: {file_name}")

def main():
    print("=" * 50)
    print("智能安装器构建工具")
    print("=" * 50)
    
    # 准备源文件
    if not prepare_source_files():
        print("准备源文件失败，构建中止")
        cleanup()
        return
    
    # 构建安装器
    success = build_installer()
    
    # 清理临时文件
    cleanup()
    
    if success:
        print("=" * 50)
        print("构建完成! 请查看 dist 目录中的 installer.exe")
        print("将此文件发送给用户进行安装或更新")
        print("=" * 50)
        print("功能说明:")
        print("- 首次运行: 安装所有文件")
        print("- 后续运行: 只更新有变化的文件")
        print("- 完成后自动删除安装器")
        print("- 用户可以选择安装路径")
        print("- 也可以选择在当前目录安装")
        print("- 更新时会自动检测已有安装")
        print("- 使用 .installignore 文件控制文件忽略行为")
    else:
        print("构建失败")

if __name__ == "__main__":
    main()