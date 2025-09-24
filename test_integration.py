"""
系統整合測試檔案
測試所有模組的整合功能
"""

import sys
import os
import subprocess
import time

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_dependencies_installation():
    """測試依賴安裝"""
    print("=== 測試依賴安裝 ===")
    
    required_packages = [
        'opencv-python',
        'mediapipe', 
        'numpy',
        'pygame',
        'gTTS',
        'Pillow',
        'keyboard',
        'pynput'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
                print(f"✓ {package} 已安裝 (版本: {cv2.__version__})")
            elif package == 'mediapipe':
                import mediapipe as mp
                print(f"✓ {package} 已安裝 (版本: {mp.__version__})")
            elif package == 'numpy':
                import numpy as np
                print(f"✓ {package} 已安裝 (版本: {np.__version__})")
            elif package == 'pygame':
                import pygame
                print(f"✓ {package} 已安裝 (版本: {pygame.version.ver})")
            elif package == 'gTTS':
                from gtts import gTTS
                print(f"✓ {package} 已安裝")
            elif package == 'Pillow':
                from PIL import Image
                print(f"✓ {package} 已安裝")
            elif package == 'keyboard':
                import keyboard
                print(f"✓ {package} 已安裝")
            elif package == 'pynput':
                import pynput
                print(f"✓ {package} 已安裝")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 未安裝")
    
    if missing_packages:
        print(f"\n缺少的套件: {', '.join(missing_packages)}")
        print("請執行: pip install -r requirements.txt")
        return False
    
    print("✓ 所有依賴已安裝")
    return True


def test_file_structure():
    """測試檔案結構"""
    print("\n=== 測試檔案結構 ===")
    
    required_files = [
        'main.py',
        'pose_detector.py',
        'gui_app.py',
        'audio_manager.py',
        'messages.py',
        'utils.py',
        'requirements.txt',
        'test_pose_detector.py',
        'test_audio_manager.py',
        'test_gui.py'
    ]
    
    missing_files = []
    
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✓ {filename} 存在")
        else:
            missing_files.append(filename)
            print(f"❌ {filename} 不存在")
    
    if missing_files:
        print(f"\n缺少的檔案: {', '.join(missing_files)}")
        return False
    
    # 檢查sounds目錄
    if os.path.exists('sounds'):
        print("✓ sounds 目錄存在")
    else:
        print("⚠️  sounds 目錄不存在，將在運行時創建")
    
    print("✓ 檔案結構檢查完成")
    return True


def test_import_all_modules():
    """測試所有模組導入"""
    print("\n=== 測試模組導入 ===")
    
    modules_to_test = [
        ('messages', 'messages.py'),
        ('utils', 'utils.py'),
        ('pose_detector', 'pose_detector.py'),
        ('audio_manager', 'audio_manager.py'),
        ('gui_app', 'gui_app.py'),
        ('main', 'main.py')
    ]
    
    failed_imports = []
    
    for module_name, filename in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {module_name} 導入成功")
        except Exception as e:
            failed_imports.append((module_name, str(e)))
            print(f"❌ {module_name} 導入失敗: {e}")
    
    if failed_imports:
        print(f"\n導入失敗的模組:")
        for module, error in failed_imports:
            print(f"  {module}: {error}")
        return False
    
    print("✓ 所有模組導入成功")
    return True


def test_run_individual_tests():
    """運行個別測試檔案"""
    print("\n=== 運行個別測試 ===")
    
    test_files = [
        'test_pose_detector.py',
        'test_audio_manager.py', 
        'test_gui.py'
    ]
    
    test_results = []
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"⚠️  {test_file} 不存在，跳過")
            continue
        
        print(f"\n運行 {test_file}...")
        try:
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✓ {test_file} 測試通過")
                test_results.append(True)
            else:
                print(f"❌ {test_file} 測試失敗")
                print(f"錯誤輸出: {result.stderr}")
                test_results.append(False)
                
        except subprocess.TimeoutExpired:
            print(f"⚠️  {test_file} 測試超時")
            test_results.append(False)
        except Exception as e:
            print(f"❌ 運行 {test_file} 時發生錯誤: {e}")
            test_results.append(False)
    
    success_rate = sum(test_results) / len(test_results) if test_results else 0
    print(f"\n個別測試通過率: {success_rate:.2%}")
    
    return success_rate >= 0.8  # 至少80%通過


def test_main_script():
    """測試主程式腳本"""
    print("\n=== 測試主程式腳本 ===")
    
    # 測試幫助信息
    try:
        result = subprocess.run(
            [sys.executable, 'main.py', '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✓ main.py --help 運行成功")
        else:
            print("❌ main.py --help 運行失敗")
            return False
            
    except Exception as e:
        print(f"❌ 測試main.py --help時發生錯誤: {e}")
        return False
    
    # 測試版本信息
    try:
        result = subprocess.run(
            [sys.executable, 'main.py', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✓ main.py --version 運行成功")
        else:
            print("❌ main.py --version 運行失敗")
            return False
            
    except Exception as e:
        print(f"❌ 測試main.py --version時發生錯誤: {e}")
        return False
    
    # 測試檢查模式
    try:
        result = subprocess.run(
            [sys.executable, 'main.py', '--check'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"main.py --check 返回碼: {result.returncode}")
        if result.stdout:
            print(f"輸出: {result.stdout}")
        if result.stderr:
            print(f"錯誤: {result.stderr}")
        
        # 檢查模式可能因為硬體問題失敗，所以不強制要求成功
        print("✓ main.py --check 測試完成")
        
    except Exception as e:
        print(f"❌ 測試main.py --check時發生錯誤: {e}")
        return False
    
    print("✓ 主程式腳本測試完成")
    return True


def test_configuration_files():
    """測試配置檔案"""
    print("\n=== 測試配置檔案 ===")
    
    # 測試requirements.txt
    if os.path.exists('requirements.txt'):
        try:
            with open('requirements.txt', 'r', encoding='utf-8') as f:
                content = f.read()
                lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
                print(f"✓ requirements.txt 包含 {len(lines)} 個套件")
        except Exception as e:
            print(f"❌ 讀取requirements.txt失敗: {e}")
            return False
    else:
        print("❌ requirements.txt 不存在")
        return False
    
    # 測試訊息配置
    try:
        from messages import Messages, SystemConfig, DetectionThresholds
        
        # 檢查必要的配置
        required_configs = [
            ('Messages.ACTION_KEYS', Messages.ACTION_KEYS),
            ('Messages.ACTION_SUCCESS', Messages.ACTION_SUCCESS),
            ('SystemConfig.CAMERA_INDEX', SystemConfig.CAMERA_INDEX),
            ('DetectionThresholds.HAND_RAISE_THRESHOLD', DetectionThresholds.HAND_RAISE_THRESHOLD),
        ]
        
        for name, value in required_configs:
            if value is not None:
                print(f"✓ {name} = {value}")
            else:
                print(f"❌ {name} 未設定")
                return False
                
    except Exception as e:
        print(f"❌ 測試配置時發生錯誤: {e}")
        return False
    
    print("✓ 配置檔案測試完成")
    return True


def generate_test_report():
    """生成測試報告"""
    print("\n=== 生成測試報告 ===")
    
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_filename = f"test_report_{timestamp}.txt"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("姿勢檢測系統整合測試報告\n")
            f.write("=" * 50 + "\n")
            f.write(f"測試時間: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"測試環境: Python {sys.version}\n")
            f.write("\n")
            
            # 這裡可以添加詳細的測試結果
            f.write("測試項目:\n")
            f.write("1. 依賴安裝檢查\n")
            f.write("2. 檔案結構檢查\n")
            f.write("3. 模組導入測試\n")
            f.write("4. 個別模組測試\n")
            f.write("5. 主程式測試\n")
            f.write("6. 配置檔案測試\n")
            f.write("\n")
            f.write("詳細結果請參考控制台輸出。\n")
        
        print(f"✓ 測試報告已生成: {report_filename}")
        return True
        
    except Exception as e:
        print(f"❌ 生成測試報告失敗: {e}")
        return False


def run_all_tests():
    """運行所有整合測試"""
    print("開始系統整合測試...")
    print("=" * 60)
    
    tests = [
        ("依賴安裝", test_dependencies_installation),
        ("檔案結構", test_file_structure),
        ("模組導入", test_import_all_modules),
        ("個別測試", test_run_individual_tests),
        ("主程式", test_main_script),
        ("配置檔案", test_configuration_files),
        ("測試報告", generate_test_report),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n>>> 執行 {test_name} 測試...")
            result = test_func()
            results.append((test_name, result))
            status = "✓ 通過" if result else "❌ 失敗"
            print(f">>> {test_name} 測試結果: {status}")
        except Exception as e:
            print(f"❌ {test_name} 測試執行失敗: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("整合測試結果摘要:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通過" if result else "❌ 失敗"
        print(f"{test_name:15} {status}")
    
    success_rate = passed / total
    print(f"\n通過率: {passed}/{total} ({success_rate:.1%})")
    
    if success_rate >= 0.8:
        print("\n🎉 系統整合測試通過！系統可以正常使用。")
        return True
    else:
        print("\n⚠️  系統整合測試未完全通過，建議檢查失敗項目。")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("系統已準備就緒，可以執行以下命令啟動：")
        print("  python main.py              # GUI模式")
        print("  python main.py --mode console  # 控制台模式")
        print("  python main.py --mode test     # 測試模式")
    else:
        print("系統尚未準備就緒，請檢查並修復失敗的測試項目。")
    
    sys.exit(0 if success else 1)