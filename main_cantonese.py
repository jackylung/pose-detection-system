"""
使用粵語語音的姿勢檢測系統主程式
"""

import sys
import os

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from messages import Messages, SystemConfig
from utils import logger, LoggerSetup
from audio_manager_cantonese import CantoneseAudioManager
from pose_detector import PoseDetector, CameraManager


class CantonesePhoneDetectionSystem:
    """粵語姿勢檢測系統"""
    
    def __init__(self):
        """初始化系統"""
        # 設定日誌
        LoggerSetup.setup_logger()
        
        # 初始化組件
        self.audio_manager = CantoneseAudioManager()
        self.pose_detector = PoseDetector()
        self.camera_manager = CameraManager()
        self.running = False
        
        logger.info("粵語姿勢檢測系統初始化完成")
    
    def test_system(self):
        """測試系統功能"""
        print("測試粵語姿勢檢測系統...")
        print("=" * 50)
        
        # 測試音訊
        print("\\n1. 測試粵語語音...")
        test_messages = [
            Messages.SYSTEM_START,
            Messages.CALIBRATION_START,
            Messages.CALIBRATION_SUCCESS,
            "成功檢測到舉起左手",
            "成功檢測到舉起右手"
        ]
        
        for msg in test_messages:
            print(f"播放: {msg}")
            self.audio_manager.speak_blocking(msg)
        
        # 測試攝影機
        print("\\n2. 測試攝影機...")
        if self.camera_manager.open_camera():
            print("✅ 攝影機測試成功")
            camera_info = self.camera_manager.get_camera_info()
            print(f"攝影機信息: {camera_info}")
            self.camera_manager.close_camera()
        else:
            print("❌ 攝影機測試失敗")
        
        print("\\n✅ 系統測試完成！")
    
    def run_simple_demo(self):
        """運行簡單演示"""
        print("\\n啟動粵語姿勢檢測演示...")
        print("按 Ctrl+C 停止演示")
        
        try:
            if not self.camera_manager.open_camera():
                print("❌ 無法開啟攝影機")
                return
            
            # 播放啟動訊息
            self.audio_manager.speak("姿勢檢測系統已啟動")
            
            # 嘗試導入cv2用於顯示
            try:
                import cv2
                cv2_available = True
                print("✅ 將顯示攝影機畫面，按 'q' 鍵退出")
            except ImportError:
                cv2_available = False
                print("⚠️ OpenCV不可用，僅在控制台輸出結果")
            
            self.running = True
            frame_count = 0
            
            while self.running:
                # 讀取幀
                frame = self.camera_manager.read_frame()
                if frame is None:
                    continue
                
                frame_count += 1
                
                # 處理幀（每5幀處理一次以提高性能）
                if frame_count % 5 == 0:
                    processed_frame, results = self.pose_detector.process_frame(frame)
                    
                    # 檢查是否有姿勢檢測結果
                    if results['pose_detected']:
                        if not results['calibration_status']:
                            print(f"校準中... {self.pose_detector.calibration_frames}/30")
                        else:
                            # 檢查動作
                            triggered_actions = self.pose_detector.get_triggered_actions()
                            for action in triggered_actions:
                                key = Messages.get_action_key(action)
                                message = Messages.get_success_message(action)
                                print(f"檢測到動作: {message} -> {key}鍵")
                                
                                # 播放語音
                                self.audio_manager.speak(message)
                    
                    # 顯示處理後的幀
                    if cv2_available:
                        cv2.imshow('Cantonese Pose Detection', processed_frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                
                # 簡單的幀率控制
                if cv2_available:
                    cv2.waitKey(1)
        
        except KeyboardInterrupt:
            print("\\n用戶中斷演示")
        except Exception as e:
            print(f"❌ 演示運行錯誤: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理資源"""
        print("\\n清理系統資源...")
        
        self.running = False
        
        if self.camera_manager:
            self.camera_manager.close_camera()
        
        if self.pose_detector:
            self.pose_detector.cleanup()
        
        if self.audio_manager:
            self.audio_manager.cleanup()
        
        # 關閉OpenCV視窗
        try:
            import cv2
            cv2.destroyAllWindows()
        except ImportError:
            pass
        
        print("✅ 清理完成")


def main():
    """主函數"""
    print("粵語姿勢檢測系統")
    print("=" * 50)
    
    # 創建系統實例
    system = CantonesePhoneDetectionSystem()
    
    try:
        # 選擇運行模式
        while True:
            print("\\n請選擇運行模式:")
            print("1. 測試系統功能")
            print("2. 運行姿勢檢測演示")
            print("3. 退出")
            
            choice = input("\\n請輸入選擇 (1-3): ").strip()
            
            if choice == '1':
                system.test_system()
            elif choice == '2':
                system.run_simple_demo()
            elif choice == '3':
                print("退出系統")
                break
            else:
                print("無效選擇，請重新輸入")
    
    except KeyboardInterrupt:
        print("\\n用戶中斷程序")
    except Exception as e:
        print(f"系統錯誤: {e}")
    finally:
        system.cleanup()


if __name__ == "__main__":
    main()