"""
測試優化後的影像流暢度
"""

import time
import cv2
import numpy as np
from pose_detector import PoseDetector, CameraManager 
from utils import logger

def test_frame_processing_performance():
    """測試幀處理性能"""
    print("測試優化後的幀處理性能...")
    print("=" * 60)
    
    # 初始化組件
    pose_detector = PoseDetector()
    camera_manager = CameraManager()
    
    if not camera_manager.open_camera():
        print("❌ 無法開啟攝影機")
        return False
    
    print("✅ 攝影機已開啟")
    
    # 測試參數
    test_duration = 10  # 測試10秒
    frame_times = []
    fps_measurements = []
    
    print(f"開始 {test_duration} 秒的性能測試...")
    
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < test_duration:
        # 記錄每幀處理時間
        frame_start = time.time()
        
        # 讀取幀
        frame = camera_manager.read_frame()
        if frame is None:
            continue
        
        # 處理幀
        processed_frame, results = pose_detector.process_frame(frame)
        
        frame_end = time.time()
        frame_time = frame_end - frame_start
        frame_times.append(frame_time)
        
        frame_count += 1
        
        # 計算即時FPS
        current_fps = 1.0 / frame_time if frame_time > 0 else 0
        fps_measurements.append(current_fps)
        
        # 顯示處理後的幀（可選）
        cv2.imshow('Performance Test', processed_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # 清理
    camera_manager.close_camera()
    cv2.destroyAllWindows()
    pose_detector.cleanup()
    
    # 計算統計數據
    total_time = time.time() - start_time
    avg_fps = frame_count / total_time
    avg_frame_time = np.mean(frame_times) * 1000  # 轉換為毫秒
    min_frame_time = np.min(frame_times) * 1000
    max_frame_time = np.max(frame_times) * 1000
    std_frame_time = np.std(frame_times) * 1000
    
    avg_processing_fps = np.mean(fps_measurements)
    min_fps = np.min(fps_measurements)
    max_fps = np.max(fps_measurements)
    
    # 輸出結果
    print(f"\n📊 性能測試結果:")
    print(f"總測試時間: {total_time:.2f} 秒")
    print(f"處理幀數: {frame_count}")
    print(f"平均FPS: {avg_fps:.2f}")
    print(f"平均幀處理時間: {avg_frame_time:.2f} 毫秒")
    print(f"最小幀處理時間: {min_frame_time:.2f} 毫秒")
    print(f"最大幀處理時間: {max_frame_time:.2f} 毫秒")
    print(f"幀處理時間標準差: {std_frame_time:.2f} 毫秒")
    print(f"")
    print(f"📈 FPS 統計:")
    print(f"平均處理FPS: {avg_processing_fps:.2f}")
    print(f"最小FPS: {min_fps:.2f}")
    print(f"最大FPS: {max_fps:.2f}")
    
    # 性能評估
    print(f"\n🎯 性能評估:")
    if avg_fps >= 20:
        print("✅ 優秀 - 影像流暢度良好 (>= 20 FPS)")
    elif avg_fps >= 15:
        print("⚠️  良好 - 影像基本流暢 (15-20 FPS)")
    elif avg_fps >= 10:
        print("⚠️  普通 - 影像略有卡頓 (10-15 FPS)")
    else:
        print("❌ 差 - 影像嚴重卡頓 (< 10 FPS)")
    
    if avg_frame_time <= 50:
        print("✅ 幀處理時間優秀 (<= 50ms)")
    elif avg_frame_time <= 100:
        print("⚠️  幀處理時間良好 (50-100ms)")
    else:
        print("❌ 幀處理時間過長 (> 100ms)")
    
    # 返回性能是否良好
    return avg_fps >= 15 and avg_frame_time <= 100

def benchmark_optimization():
    """基準優化測試"""
    print("\n" + "=" * 60)
    print("🔧 優化建議")
    print("=" * 60)
    
    print("已實施的優化措施:")
    print("✅ 簡化中文文字渲染，改用英文顯示")
    print("✅ 緩存視窗大小，減少重複計算")
    print("✅ 減少GUI更新頻率 (30FPS -> 20FPS)")
    print("✅ 優化幀處理頻率 (30FPS -> 25FPS)")
    print("✅ 限制狀態信息顯示數量")
    print("✅ 使用線性插值進行圖像縮放")
    
    print("\n如果性能仍不理想，可考慮:")
    print("🔧 降低攝影機解析度 (640x480 -> 320x240)")
    print("🔧 減少MediaPipe模型複雜度 (1 -> 0)")
    print("🔧 跳幀處理 (每2幀處理一次)")
    print("🔧 禁用骨架繪製以節省處理時間")

if __name__ == "__main__":
    try:
        result = test_frame_processing_performance()
        benchmark_optimization()
        
        if result:
            print("\n🎉 性能測試通過！影像流暢度已大幅改善！")
        else:
            print("\n⚠️  性能仍需進一步優化")
    
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()