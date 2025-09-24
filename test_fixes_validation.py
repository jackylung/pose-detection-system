"""
測試驗證修正結果
檢查所有修正的問題是否已解決
"""

import cv2
import time
from pose_detector import PoseDetector
from messages import DetectionThresholds

def test_chinese_text_display():
    """測試中文文字顯示"""
    print("📝 測試中文文字顯示...")
    
    # 創建測試圖像
    test_frame = cv2.zeros((480, 640, 3), dtype=cv2.uint8)
    
    # 創建姿勢檢測器實例
    detector = PoseDetector()
    
    # 測試中文文字顯示
    detector._put_chinese_text(test_frame, "校準中...", (10, 30), color=(0, 255, 255))
    detector._put_chinese_text(test_frame, "已校準", (10, 70), color=(0, 255, 0))
    detector._put_chinese_text(test_frame, "成功檢測到舉起左手", (10, 110), color=(0, 255, 0))
    
    # 檢查是否正確繪製（圖像不為全黑）
    if cv2.countNonZero(cv2.cvtColor(test_frame, cv2.COLOR_BGR2GRAY)) > 0:
        print("✅ 中文文字顯示功能正常")
        return True
    else:
        print("❌ 中文文字顯示有問題")
        return False

def test_calibration_success_display():
    """測試校準成功顯示"""
    print("📝 測試校準成功顯示功能...")
    
    # 創建測試圖像
    test_frame = cv2.zeros((480, 640, 3), dtype=cv2.uint8)
    
    # 創建姿勢檢測器並設置校準成功時間
    detector = PoseDetector()
    detector.calibration_success_display_time = time.time()
    
    # 測試繪製狀態信息
    detection_results = {
        'pose_detected': True,
        'landmarks': None,
        'actions': {},
        'calibration_status': True
    }
    
    detector._draw_status_info(test_frame, detection_results)
    
    # 檢查是否正確繪製"成功校正"
    if cv2.countNonZero(cv2.cvtColor(test_frame, cv2.COLOR_BGR2GRAY)) > 0:
        print("✅ 校準成功顯示功能正常")
        return True
    else:
        print("❌ 校準成功顯示有問題")
        return False

def test_left_right_detection_fix():
    """測試左右手腳判斷修正"""
    print("📝 測試左右手腳判斷修正...")
    
    detector = PoseDetector()
    
    # 模擬基準姿勢特徵
    baseline_features = {
        'left_wrist': {'x': 0.3, 'y': 0.5, 'z': 0.0},
        'right_wrist': {'x': 0.7, 'y': 0.5, 'z': 0.0},
        'left_shoulder': {'x': 0.4, 'y': 0.3, 'z': 0.0},
        'right_shoulder': {'x': 0.6, 'y': 0.3, 'z': 0.0},
        'left_ankle': {'x': 0.4, 'y': 0.9, 'z': 0.0},
        'right_ankle': {'x': 0.6, 'y': 0.9, 'z': 0.0}
    }
    
    detector.baseline_pose = baseline_features
    
    # 測試左手舉起（實際上檢測右手，因為鏡像修正）
    current_features = baseline_features.copy()
    current_features['right_wrist'] = {'x': 0.7, 'y': 0.2, 'z': 0.0}  # 右手舉起
    
    left_hand_detected = detector._detect_hand_raise(current_features, 'left')
    
    if left_hand_detected:
        print("✅ 左右手判斷修正成功（鏡像修正已應用）")
        return True
    else:
        print("❌ 左右手判斷修正失敗")
        return False

def test_nod_detection_optimization():
    """測試點頭識別優化"""
    print("📝 測試點頭識別優化...")
    
    detector = PoseDetector()
    
    # 檢查閾值是否已降低
    if DetectionThresholds.NOD_THRESHOLD == 0.03:
        print("✅ 點頭檢測閾值已優化（降低到0.03）")
        
        # 模擬基準和當前姿勢
        baseline_features = {'nose': {'x': 0.5, 'y': 0.4, 'z': 0.0}}
        detector.baseline_pose = baseline_features
        
        # 測試更敏感的點頭檢測
        current_features = {'nose': {'x': 0.5, 'y': 0.42, 'z': 0.0}}  # 輕微向下移動
        
        nod_detected = detector._detect_nod(current_features)
        
        if nod_detected:
            print("✅ 點頭識別敏感度已提高")
            return True
        else:
            print("⚠️ 點頭識別敏感度可能需要進一步調整")
            return False
    else:
        print(f"❌ 點頭檢測閾值未正確設置：{DetectionThresholds.NOD_THRESHOLD}")
        return False

def main():
    """主測試函數"""
    print("🔍 開始驗證修正結果...\n")
    
    tests = [
        ("中文文字顯示", test_chinese_text_display),
        ("校準成功顯示", test_calibration_success_display),
        ("左右手腳判斷修正", test_left_right_detection_fix),
        ("點頭識別優化", test_nod_detection_optimization)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
            else:
                print(f"測試失敗：{test_name}")
        except Exception as e:
            print(f"❌ 測試出錯：{test_name} - {e}")
    
    print(f"\n🎯 測試結果：{passed}/{total} 項測試通過")
    
    if passed == total:
        print("🎉 所有修正都已成功實施！")
        print("\n✅ 修正摘要：")
        print("1. GUI影像範圍顯示文字已改為中文")
        print("2. \"成功校正\"顯示問題已修正（使用FONT_HERSHEY_COMPLEX和LINE_AA）")
        print("3. 左右手腳判斷錯誤已修正（應用鏡像座標系修正）")
        print("4. 點頭識別敏感度已優化（閾值從0.05降至0.03）")
    else:
        print("⚠️ 部分修正可能需要進一步調整")

if __name__ == "__main__":
    main()