"""
姿勢檢測系統打包腳本
使用PyInstaller創建Windows可執行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """檢查是否已安裝PyInstaller"""
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], 
                      check=True, capture_output=True)
        print("✓ PyInstaller已安裝")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ PyInstaller未安裝")
        return False

def install_pyinstaller():
    """安裝PyInstaller"""
    print("正在安裝PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                      check=True)
        print("✓ PyInstaller安裝成功")
        return True
    except subprocess.CalledProcessError:
        print("✗ PyInstaller安裝失敗")
        return False

def build_executable():
    """構建可執行文件"""
    # 獲取當前目錄
    current_dir = Path.cwd()
    main_script = current_dir / "main.py"
    
    if not main_script.exists():
        print(f"錯誤: 找不到主腳本 {main_script}")
        return False
    
    # 構建PyInstaller命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # 單一文件
        "--windowed",          # 無控制台窗口
        "--name", "姿勢檢測系統",     # 應用名稱
        "--icon=NONE",         # 不使用圖標
        "--add-data", f"sounds;sounds",  # 包含音頻文件
        "--hidden-import", "cv2",       # 隱藏導入
        "--hidden-import", "mediapipe", 
        "--hidden-import", "numpy",
        "--hidden-import", "pygame",
        "--hidden-import", "gtts",
        "--hidden-import", "PIL",
        str(main_script)
    ]
    
    print("正在構建可執行文件...")
    print("命令:", " ".join(cmd))
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ 構建成功完成")
        print("可執行文件位置: dist/姿勢檢測系統.exe")
        return True
    except subprocess.CalledProcessError as e:
        print("✗ 構建失敗")
        print("錯誤信息:", e.stderr)
        return False

def copy_additional_files():
    """複製額外的文件到dist目錄"""
    dist_dir = Path("dist")
    if not dist_dir.exists():
        dist_dir.mkdir()
    
    # 複製README和安裝指南
    files_to_copy = ["README.md", "INSTALLATION_GUIDE.md", "requirements.txt"]
    for file_name in files_to_copy:
        file_path = Path(file_name)
        if file_path.exists():
            shutil.copy2(file_path, dist_dir)
            print(f"✓ 已複製 {file_name}")
    
    print("✓ 額外文件複製完成")

def create_distribution_package():
    """創建分發包"""
    dist_dir = Path("dist")
    package_name = "姿勢檢測系統_分發包"
    package_dir = Path(package_name)
    
    # 如果包目錄已存在，先刪除
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    # 創建包目錄
    package_dir.mkdir()
    
    # 複製所有分發文件
    if dist_dir.exists():
        for item in dist_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, package_dir)
                print(f"✓ 已複製 {item.name}")
    
    print(f"✓ 分發包創建完成: {package_name}")

def main():
    """主函數"""
    print("=== 姿勢檢測系統打包工具 ===")
    print()
    
    # 檢查並安裝PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            return False
    
    # 構建可執行文件
    if not build_executable():
        return False
    
    # 複製額外文件
    copy_additional_files()
    
    # 創建分發包
    create_distribution_package()
    
    print()
    print("=== 打包完成 ===")
    print("可執行文件: dist/姿勢檢測系統.exe")
    print("分發包: 姿勢檢測系統_分發包/")
    print()
    print("分發包包含:")
    print("- 姿勢檢測系統.exe (主程序)")
    print("- README.md (使用說明)")
    print("- INSTALLATION_GUIDE.md (安裝指南)")
    print("- requirements.txt (依賴列表)")

if __name__ == "__main__":
    main()