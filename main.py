"""
姿勢檢測系統主程式
整合所有模組，提供統一的入口點
"""

import sys
import os
import time
import argparse
import signal
from typing import Optional

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from messages import Messages, SystemConfig
from utils import logger, LoggerSetup
from gui_app import PoseDetectionGUI
from audio_manager_cantonese_fixed import CantoneseAudioManagerFixed
from audio_manager import AudioTester
from pose_detector import PoseDetector, CameraManager


class PoseDetectionSystem:
    """姿勢檢測系統主類"""
    
    def __init__(self):
        """初始化系統"""
        # 設定日誌
        LoggerSetup.setup_logger()
        
        # 初始化粵語音訊管理器
        self.audio_manager = CantoneseAudioManagerFixed()
        
        # 系統組件
        self.gui_app: Optional[PoseDetectionGUI] = None
        self.running = False
        
        # 註冊信號處理器
        self._register_signal_handlers()
        
        logger.info("姿勢檢測系統初始化完成")
    
    def _register_signal_handlers(self):
        """註冊系統信號處理器"""
        def signal_handler(signum, frame):
            logger.info(f"接收到信號 {signum}，正在優雅關閉系統...")
            self.shutdown()
            sys.exit(0)
        
        # 註冊常見的終止信號
        try:
            signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
            signal.signal(signal.SIGTERM, signal_handler)  # 終止信號
            if hasattr(signal, 'SIGBREAK'):  # Windows
                signal.signal(signal.SIGBREAK, signal_handler)
        except Exception as e:
            logger.warning(f"註冊信號處理器時發生錯誤: {e}")
    
    def check_dependencies(self) -> bool:
        """檢查系統依賴"""
        logger.info("檢查系統依賴...")
        
        missing_deps = []
        
        # 檢查必要的庫
        try:
            import cv2
            logger.info(f"OpenCV版本: {cv2.__version__}")
        except ImportError:
            missing_deps.append("opencv-python")
        
        try:
            import mediapipe as mp
            logger.info(f"MediaPipe版本: {mp.__version__}")
        except ImportError:
            missing_deps.append("mediapipe")
        
        try:
            import numpy as np
            logger.info(f"NumPy版本: {np.__version__}")
        except ImportError:
            missing_deps.append("numpy")
        
        try:
            import pygame
            logger.info(f"Pygame版本: {pygame.version.ver}")
        except ImportError:
            missing_deps.append("pygame")
        
        try:
            from gtts import gTTS
            logger.info("gTTS庫可用")
        except ImportError:
            missing_deps.append("gTTS")
        
        try:
            from PIL import Image
            logger.info(f"Pillow版本: {Image.__version__}")
        except ImportError:
            missing_deps.append("Pillow")
        
        # 檢查可選的庫
        try:
            import keyboard
            logger.info("keyboard庫可用")
        except ImportError:
            try:
                import pynput
                logger.info("pynput庫可用")
            except ImportError:
                logger.warning("鍵盤模擬庫不可用，將使用基本模擬")
        
        if missing_deps:
            logger.error(f"缺少必要依賴: {', '.join(missing_deps)}")
            logger.error("請執行: pip install -r requirements.txt")
            return False
        
        logger.info("所有依賴檢查通過")
        return True
    
    def check_hardware(self) -> bool:
        """檢查硬體設備"""
        logger.info("檢查硬體設備...")
        
        # 檢查攝影機
        camera_manager = CameraManager()
        if not camera_manager.open_camera():
            logger.error("無法訪問攝影機設備")
            return False
        
        camera_info = camera_manager.get_camera_info()
        logger.info(f"攝影機信息: {camera_info}")
        camera_manager.close_camera()
        
        # 檢查音訊系統
        if not self.audio_manager.is_initialized:
            logger.warning("音訊系統初始化失敗，語音功能可能不可用")
        else:
            logger.info("音訊系統正常")
        
        logger.info("硬體設備檢查完成")
        return True
    
    def run_gui_mode(self):
        """運行GUI模式"""
        logger.info("啟動GUI模式...")
        
        try:
            # 將音訊管理器傳遞給GUI，避免創建多個實例
            self.gui_app = PoseDetectionGUI(audio_manager=self.audio_manager)
            self.running = True
            
            logger.info("GUI應用已啟動")
            self.gui_app.run()
            
        except Exception as e:
            logger.error(f"GUI模式運行失敗: {e}")
            raise
        finally:
            self.running = False
    
    def run_console_mode(self):
        """運行控制台模式（無GUI）"""
        logger.info("啟動控制台模式...")
        
        try:
            # 初始化組件
            pose_detector = PoseDetector()
            camera_manager = CameraManager()
            
            if not camera_manager.open_camera():
                logger.error("無法開啟攝影機")
                return
            
            self.running = True
            logger.info("控制台模式已啟動，按Ctrl+C停止")
            
            # 播放啟動語音
            self.audio_manager.play_system_start()
            
            # 嘗試導入cv2用於顯示
            cv2_available = False
            try:
                import cv2
                cv2_available = True
            except ImportError:
                logger.warning("OpenCV不可用，無法顯示圖像")
            
            while self.running:
                try:
                    # 讀取幀
                    frame = camera_manager.read_frame()
                    if frame is None:
                        continue
                    
                    # 處理幀
                    processed_frame, results = pose_detector.process_frame(frame)
                    
                    # 顯示處理後的幀（如果有GUI環境）
                    if cv2_available:
                        import cv2 as cv2_module
                        cv2_module.imshow('Pose Detection', processed_frame)
                        if cv2_module.waitKey(1) & 0xFF == ord('q'):
                            break
                    
                    # 處理檢測結果
                    if results['calibration_status'] and not pose_detector.is_calibrated:
                        self.audio_manager.play_calibration_success()
                    
                    # 處理觸發的動作
                    if pose_detector.is_calibrated:
                        triggered_actions = pose_detector.get_triggered_actions()
                        for action in triggered_actions:
                            key = Messages.get_action_key(action)
                            logger.info(f"動作觸發: {action} → {key}")
                            self.audio_manager.play_action_success(action)
                
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"處理幀時發生錯誤: {e}")
            
        except Exception as e:
            logger.error(f"控制台模式運行失敗: {e}")
            raise
        finally:
            self.running = False
            try:
                if 'camera_manager' in locals() and camera_manager:
                    camera_manager.close_camera()
                if 'pose_detector' in locals() and pose_detector:
                    pose_detector.cleanup()
                if cv2_available:
                    import cv2 as cv2_module
                    cv2_module.destroyAllWindows()
            except Exception as e:
                logger.error(f"清理資源時發生錯誤: {e}")
    
    def run_test_mode(self):
        """運行測試模式"""
        logger.info("啟動測試模式...")
        
        try:
            # 測試粵語音訊系統
            logger.info("開始測試粵語音訊功能...")
            
            # 測試基本語音
            test_messages = [
                Messages.SYSTEM_START,
                Messages.CALIBRATION_START,
                Messages.CALIBRATION_SUCCESS,
                Messages.get_success_message('left_hand'),
                Messages.get_success_message('right_hand')
            ]
            
            for i, message in enumerate(test_messages, 1):
                logger.info(f"測試 {i}: {message}")
                success = self.audio_manager.speak(message)
                if success:
                    logger.info("✅ 語音播放成功")
                else:
                    logger.error("❌ 語音播放失敗")
                time.sleep(2)  # 等待播放完成
            
            logger.info("粵語音訊測試完成")
            
            # 測試姿勢檢測
            pose_detector = PoseDetector()
            logger.info("姿勢檢測器創建成功")
            pose_detector.cleanup()
            
            # 測試攝影機
            camera_manager = CameraManager()
            if camera_manager.open_camera():
                logger.info("攝影機測試成功")
                camera_manager.close_camera()
            else:
                logger.error("攝影機測試失敗")
            
            logger.info("所有測試完成")
            
        except Exception as e:
            logger.error(f"測試模式運行失敗: {e}")
            raise
    
    def shutdown(self):
        """關閉系統"""
        logger.info("正在關閉系統...")
        
        self.running = False
        
        # 清理GUI應用
        if self.gui_app:
            try:
                self.gui_app.on_closing()
            except:
                pass
        
        # 清理音訊系統
        try:
            self.audio_manager.cleanup()
        except:
            pass
        
        logger.info("系統已關閉")


def create_argument_parser() -> argparse.ArgumentParser:
    """創建命令行參數解析器"""
    parser = argparse.ArgumentParser(
        description="姿勢檢測系統 - 使用MediaPipe進行即時姿勢檢測和動作識別",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python main.py                    # 啟動GUI模式
  python main.py --mode console     # 啟動控制台模式
  python main.py --mode test        # 運行測試模式
  python main.py --check           # 檢查系統依賴和硬體
        """
    )
    
    parser.add_argument(
        '--mode', '-m',
        choices=['gui', 'console', 'test'],
        default='gui',
        help='運行模式（預設: gui）'
    )
    
    parser.add_argument(
        '--check', '-c',
        action='store_true',
        help='檢查系統依賴和硬體後退出'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='啟用調試模式'
    )
    
    parser.add_argument(
        '--camera', 
        type=int,
        default=0,
        help='攝影機索引（預設: 0）'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='姿勢檢測系統 v1.0.0'
    )
    
    return parser


def main():
    """主函數"""
    # 解析命令行參數
    parser = create_argument_parser()
    args = parser.parse_args()
    
    try:
        # 創建系統實例
        system = PoseDetectionSystem()
        
        # 設定攝影機索引
        SystemConfig.CAMERA_INDEX = args.camera
        
        # 檢查依賴和硬體
        if not system.check_dependencies():
            print("依賴檢查失敗，請安裝缺少的庫")
            sys.exit(1)
        
        if not system.check_hardware():
            print("硬體檢查失敗，請檢查攝影機和音訊設備")
            sys.exit(1)
        
        # 如果只是檢查，則退出
        if args.check:
            print("系統檢查完成，所有組件正常")
            sys.exit(0)
        
        # 根據模式運行
        if args.mode == 'gui':
            system.run_gui_mode()
        elif args.mode == 'console':
            system.run_console_mode()
        elif args.mode == 'test':
            system.run_test_mode()
    
    except KeyboardInterrupt:
        logger.info("用戶中斷程序")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序執行失敗: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()