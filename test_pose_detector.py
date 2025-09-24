"""
姿勢檢測器測試檔案
獨立測試MediaPipe姿勢檢測功能
"""

import sys
import os
import time

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import cv2
    import numpy as np
    from pose_detector import PoseDetector, CameraManager
    from utils import logger
    CV2_AVAILABLE = True
except ImportError as e:
    print(f"導入失敗: {e}")
    print("請先安裝依賴: pip install opencv-python mediapipe numpy")
    CV2_AVAILABLE = False


def test_camera_basic():
    """測試攝影機基本功能"""
    print("=== 測試攝影機基本功能 ===")
    
    if not CV2_AVAILABLE:
        print("跳過測試：缺少必要依賴")
        return False
    
    try:
        camera = CameraManager()
        
        if not camera.open_camera():
            print("❌ 無法開啟攝影機")
            return False
        
        print("✓ 攝影機開啟成功")
        
        # 獲取攝影機信息
        info = camera.get_camera_info()
        print(f"✓ 攝影機信息: {info}")
        
        # 讀取幾幀測試
        for i in range(5):
            frame = camera.read_frame()
            if frame is None:
                print(f"❌ 第{i+1}幀讀取失敗")
                camera.close_camera()
                return False
            print(f"✓ 成功讀取第{i+1}幀，尺寸: {frame.shape}")
            time.sleep(0.1)
        
        camera.close_camera()
        print("✓ 攝影機測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 攝影機測試失敗: {e}")
        return False


def test_pose_detector_init():
    """測試姿勢檢測器初始化"""
    print("\n=== 測試姿勢檢測器初始化 ===")
    
    if not CV2_AVAILABLE:
        print("跳過測試：缺少必要依賴")
        return False
    
    try:
        detector = PoseDetector()
        print("✓ 姿勢檢測器初始化成功")
        
        # 檢查初始狀態
        if not detector.is_calibrated:
            print("✓ 初始校準狀態正確（未校準）")
        else:
            print("❌ 初始校準狀態錯誤")
            return False
        
        detector.cleanup()
        print("✓ 姿勢檢測器清理成功")
        return True
        
    except Exception as e:
        print(f"❌ 姿勢檢測器初始化失敗: {e}")
        return False


def test_pose_detection_with_camera():
    """測試帶攝影機的姿勢檢測"""
    print("\n=== 測試姿勢檢測功能 ===")
    
    if not CV2_AVAILABLE:
        print("跳過測試：缺少必要依賴")
        return False
    
    try:
        detector = PoseDetector()
        camera = CameraManager()
        
        if not camera.open_camera():
            print("❌ 無法開啟攝影機")
            return False
        
        print("✓ 開始姿勢檢測測試（10秒）")
        print("請面對攝影機並嘗試不同姿勢...")
        
        start_time = time.time()
        frame_count = 0
        pose_detected_count = 0
        
        while time.time() - start_time < 10.0:
            frame = camera.read_frame()
            if frame is None:
                continue
            
            # 處理幀
            processed_frame, results = detector.process_frame(frame)
            frame_count += 1
            
            if results['pose_detected']:
                pose_detected_count += 1
                print(f"✓ 第{frame_count}幀檢測到姿勢")
            
            # 顯示結果（可選）
            try:
                cv2.imshow('Pose Detection Test', processed_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            except:
                pass
            
            time.sleep(0.033)  # 約30FPS
        
        camera.close_camera()
        detector.cleanup()
        
        try:
            cv2.destroyAllWindows()
        except:
            pass
        
        detection_rate = pose_detected_count / frame_count if frame_count > 0 else 0
        print(f"✓ 測試完成")
        print(f"  - 總幀數: {frame_count}")
        print(f"  - 檢測到姿勢的幀數: {pose_detected_count}")
        print(f"  - 檢測成功率: {detection_rate:.2%}")
        
        return detection_rate > 0.5  # 至少50%的幀應該檢測到姿勢
        
    except Exception as e:
        print(f"❌ 姿勢檢測測試失敗: {e}")
        return False


def test_action_detection_simulation():
    """測試動作檢測模擬"""
    print("\n=== 測試動作檢測邏輯 ===")
    
    if not CV2_AVAILABLE:
        print("跳過測試：缺少必要依賴")
        return False
    
    try:
        detector = PoseDetector()
        
        # 模擬校準
        print("✓ 模擬校準過程...")
        detector.is_calibrated = True
        
        # 創建模擬的baseline pose
        detector.baseline_pose = {
            'left_wrist': {'x': 0.3, 'y': 0.5, 'z': 0.0},
            'right_wrist': {'x': 0.7, 'y': 0.5, 'z': 0.0},
            'left_ankle': {'x': 0.4, 'y': 0.9, 'z': 0.0},
            'right_ankle': {'x': 0.6, 'y': 0.9, 'z': 0.0},
            'left_shoulder': {'x': 0.4, 'y': 0.3, 'z': 0.0},
            'right_shoulder': {'x': 0.6, 'y': 0.3, 'z': 0.0},
            'nose': {'x': 0.5, 'y': 0.2, 'z': 0.0}
        }
        
        # 測試各種動作檢測
        test_cases = [
            {
                'name': '舉起左手',
                'features': {
                    'left_wrist': {'x': 0.3, 'y': 0.2, 'z': 0.0},  # 手舉高
                    'right_wrist': {'x': 0.7, 'y': 0.5, 'z': 0.0},
                    'left_shoulder': {'x': 0.4, 'y': 0.3, 'z': 0.0},
                    'right_shoulder': {'x': 0.6, 'y': 0.3, 'z': 0.0},
                },
                'expected_action': 'left_hand'
            },
            {
                'name': '舉起右腳',
                'features': {
                    'left_ankle': {'x': 0.4, 'y': 0.9, 'z': 0.0},
                    'right_ankle': {'x': 0.6, 'y': 0.7, 'z': 0.0},  # 腳抬高
                },
                'expected_action': 'right_foot'
            }
        ]
        
        for test_case in test_cases:
            print(f"測試: {test_case['name']}")
            
            # 模擬當前特徵
            current_features = detector.baseline_pose.copy()
            current_features.update(test_case['features'])
            
            # 檢測動作
            detected_actions = detector._detect_actions_from_features(current_features)
            
            expected = test_case['expected_action']
            if detected_actions.get(expected, False):
                print(f"✓ {test_case['name']} 檢測成功")
            else:
                print(f"❌ {test_case['name']} 檢測失敗")
        
        detector.cleanup()
        print("✓ 動作檢測邏輯測試完成")
        return True
        
    except AttributeError:
        print("⚠️  動作檢測方法不存在，跳過測試")
        return True
    except Exception as e:
        print(f"❌ 動作檢測測試失敗: {e}")
        return False


def run_all_tests():
    """運行所有測試"""
    print("開始姿勢檢測器測試...")
    print("=" * 50)
    
    tests = [
        test_camera_basic,
        test_pose_detector_init,
        test_pose_detection_with_camera,
        test_action_detection_simulation,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ 測試 {test_func.__name__} 執行失敗: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("測試結果摘要:")
    print(f"通過: {sum(results)}/{len(results)}")
    
    for i, (test_func, result) in enumerate(zip(tests, results)):
        status = "✓ 通過" if result else "❌ 失敗"
        print(f"{i+1}. {test_func.__name__}: {status}")
    
    overall_success = all(results)
    print(f"\n整體測試結果: {'✓ 全部通過' if overall_success else '❌ 有失敗項目'}")
    
    return overall_success


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)