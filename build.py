#!/usr/bin/env python3
"""
编译脚本 - 使用PyInstaller编译数位分析器

使用方法：
python build.py
"""

import sys
import subprocess
import platform

def check_python():
    """检查Python是否安装"""
    print("正在检查Python版本...")
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True, check=True)
        print(f"Python版本: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"Python检查失败: {e}")
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        # 使用完整路径的pip安装pyinstaller
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("PyInstaller安装成功!")
        return True
    except Exception as e:
        print(f"PyInstaller安装失败: {e}")
        return False

def is_pyinstaller_available():
    """检查PyInstaller是否可用"""
    try:
        result = subprocess.run([sys.executable, "-m", "pyinstaller", "--version"], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"检查PyInstaller可用性失败: {e}")
        return False

def compile_app():
    """编译应用程序"""
    print("正在编译应用程序...")
    
    # 先检查PyInstaller是否可用
    if not is_pyinstaller_available():
        print("PyInstaller不可用，尝试重新安装...")
        if not install_pyinstaller():
            return False
    
    try:
        # 使用app.spec文件编译
        subprocess.run([sys.executable, "-m", "pyinstaller", "app.spec"], check=True)
        print("应用程序编译成功!")
        print("可执行文件已生成在 dist 目录下")
        return True
    except Exception as e:
        print(f"应用程序编译失败: {e}")
        
        # 尝试直接使用pyinstaller命令（不通过-m选项）
        print("尝试使用直接调用pyinstaller命令...")
        try:
            subprocess.run(["pyinstaller", "app.spec"], check=True)
            print("应用程序编译成功!")
            print("可执行文件已生成在 dist 目录下")
            return True
        except Exception as e2:
            print(f"直接调用pyinstaller也失败: {e2}")
            return False

def main():
    """主函数"""
    print("=== 数位分析器编译脚本 ===")
    print(f"当前Python解释器: {sys.executable}")
    print(f"当前系统: {platform.platform()}")
    print()
    
    # 检查Python
    if not check_python():
        print("请先安装Python 3.8或更高版本")
        return False
    
    # 安装PyInstaller
    if not install_pyinstaller():
        return False
    
    # 编译应用
    if not compile_app():
        return False
    
    print()
    print("=== 编译完成 ===")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    input("按Enter键退出...")
