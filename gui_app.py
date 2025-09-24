"""
GUI應用模組
使用Tkinter創建圖形用戶界面，顯示系統狀態和控制功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import cv2
from PIL import Image, ImageTk
import numpy as np
from typing import Optional, Dict, List

from messages import Messages, SystemConfig
from utils import logger, keyboard_sim, system_monitor, get_timestamp
from pose_detector import PoseDetector, CameraManager
from audio_manager_cantonese_fixed import CantoneseAudioManagerFixed
from audio_manager import voice_instruction_manager


class PoseDetectionGUI:
    """姿勢檢測GUI主應用"""
    
    def __init__(self, audio_manager=None):
        """初始化GUI應用"""
        self.root = tk.Tk()
        self.setup_window()
        
        # 使用傳入的音訊管理器或創建新的
        if audio_manager:
            self.audio_manager = audio_manager
            logger.info("使用傳入的音訊管理器")
        else:
            # 初始化粵語音訊管理器
            self.audio_manager = CantoneseAudioManagerFixed()
            logger.info("創建新的音訊管理器")
        
        # 核心組件
        self.pose_detector = PoseDetector()
        self.camera_manager = CameraManager()
        
        # 狀態變數（需要在setup_widgets之前初始化）
        self.is_running = False
        self.current_frame = None
        self.last_action = ""
        self.last_key = ""
        
        # 動作啟用狀態
        self.action_enabled = {}
        for action in Messages.ACTION_KEYS.keys():
            self.action_enabled[action] = tk.BooleanVar(value=True)
        
        # 語音模式
        self.voice_enabled = tk.BooleanVar(value=True)
        
        # GUI組件（在變數初始化後設定）
        self.setup_widgets()
        
        # 運行線程
        self.detection_thread = None
        self.gui_update_thread = None
        
        # 初始化圖像引用
        self.current_photo = None
        
        # 優化：緩存視窗大小以減少重複計算
        self.cached_widget_size = (640, 480)
        self.size_update_counter = 0
    
    def setup_window(self):
        """設定主視窗"""
        self.root.title(Messages.GUI_TEXTS['title'])
        self.root.geometry(f"{SystemConfig.GUI_WIDTH}x{SystemConfig.GUI_HEIGHT}")
        self.root.resizable(True, True)
        
        # 設定關閉事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 設定視窗大小變化事件處理
        self.root.bind('<Configure>', self.on_window_resize)
        
        # 設定圖標（如果有的話）
        try:
            # self.root.iconbitmap('icon.ico')  # 可選
            pass
        except:
            pass
    
    def setup_widgets(self):
        """設定GUI組件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # 配置網格權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 創建各個區域
        self.create_control_panel(main_frame)
        self.create_video_display(main_frame)
        self.create_action_panel(main_frame)
        self.create_status_panel(main_frame)
        self.create_key_display(main_frame)
    
    def create_control_panel(self, parent):
        """創建控制面板"""
        control_frame = ttk.LabelFrame(parent, text="系統控制", padding="5")
        control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        
        # 啟動/停止按鈕
        self.start_button = ttk.Button(
            control_frame, 
            text=Messages.GUI_TEXTS['start_system'], 
            command=self.toggle_system
        )
        self.start_button.grid(row=0, column=0, padx=(0, 5))
        
        # 語音控制
        self.voice_checkbox = ttk.Checkbutton(
            control_frame,
            text=Messages.GUI_TEXTS['voice_mode'],
            variable=self.voice_enabled,
            command=self.toggle_voice_mode
        )
        self.voice_checkbox.grid(row=0, column=2, padx=(0, 5))
        
        # 音量控制
        ttk.Label(control_frame, text="音量:").grid(row=0, column=3, padx=(10, 5))
        self.volume_scale = ttk.Scale(
            control_frame,
            from_=0, to=100,
            orient=tk.HORIZONTAL,
            length=100,
            command=self.on_volume_change
        )
        self.volume_scale.set(70)
        self.volume_scale.grid(row=0, column=4, padx=(0, 5))
    
    def create_video_display(self, parent):
        """創建視頻顯示區域"""
        video_frame = ttk.LabelFrame(parent, text="攝影機畫面", padding="5")
        video_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        
        # 視頻標籤
        self.video_label = ttk.Label(video_frame, text="攝影機未啟動", anchor=tk.CENTER)
        self.video_label.grid(row=0, column=0, sticky="nsew")
        
        video_frame.columnconfigure(0, weight=1)
        video_frame.rowconfigure(0, weight=1)
    
    def create_action_panel(self, parent):
        """創建動作控制面板"""
        action_frame = ttk.LabelFrame(parent, text="支援的動作", padding="5")
        action_frame.grid(row=1, column=1, sticky="nsew")
        
        # 動作說明標題
        ttk.Label(action_frame, text="動作 → 按鍵", font=("Arial", 10, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 10)
        )
        
        # 動作複選框
        row = 1
        for action, key in Messages.ACTION_KEYS.items():
            instruction = Messages.ACTION_INSTRUCTIONS[action]
            
            # 複選框
            checkbox = ttk.Checkbutton(
                action_frame,
                text=f"{instruction} → {key}",
                variable=self.action_enabled[action]
            )
            checkbox.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
            row += 1
    
    def create_status_panel(self, parent):
        """創建狀態面板"""
        status_frame = ttk.LabelFrame(parent, text="系統狀態", padding="5")
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        
        # 狀態標籤
        self.status_label = ttk.Label(status_frame, text="系統待機中")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # FPS標籤
        self.fps_label = ttk.Label(status_frame, text="FPS: 0")
        self.fps_label.grid(row=0, column=1, padx=(20, 0))
        
        # 運行時間標籤
        self.runtime_label = ttk.Label(status_frame, text="運行時間: 00:00:00")
        self.runtime_label.grid(row=0, column=2, padx=(20, 0))
        
        # 最後動作標籤
        self.last_action_label = ttk.Label(status_frame, text="最後動作: 無")
        self.last_action_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
    
    def create_key_display(self, parent):
        """創建按鍵顯示區域"""
        key_frame = ttk.LabelFrame(parent, text="按鍵輸出", padding="10")
        key_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        
        # 大尺寸按鍵顯示
        self.key_display = ttk.Label(
            key_frame, 
            text="－", 
            font=("Arial", 48, "bold"),
            anchor=tk.CENTER,
            foreground="red"
        )
        self.key_display.grid(row=0, column=0, sticky="ew")
        
        key_frame.columnconfigure(0, weight=1)
    
    def toggle_system(self):
        """切換系統運行狀態"""
        if not self.is_running:
            self.start_system()
        else:
            self.stop_system()
    
    def start_system(self):
        """啟動系統"""
        try:
            # 開啟攝影機
            if not self.camera_manager.open_camera():
                messagebox.showerror("錯誤", "無法開啟攝影機")
                return
            
            # 啟動檢測線程
            self.is_running = True
            self.detection_thread = threading.Thread(target=self.detection_worker, daemon=True)
            self.detection_thread.start()
            
            # 啟動GUI更新（使用after方法而非線程）
            self.gui_update_worker()
            
            # 更新UI
            self.start_button.config(text=Messages.GUI_TEXTS['stop_system'])
            
            # 播放啟動語音
            if self.voice_enabled.get():
                self.audio_manager.play_system_start()
            
            logger.info("系統已啟動")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"啟動系統時發生錯誤: {e}")
            logger.error(f"啟動系統失敗: {e}")
    
    def stop_system(self):
        """停止系統"""
        self.is_running = False
        
        # 等待線程結束
        if self.detection_thread:
            self.detection_thread.join(timeout=2.0)
        
        # 關閉攝影機
        self.camera_manager.close_camera()
        
        # 停止語音指令循環
        voice_instruction_manager.stop_continuous_instructions()
        
        # 更新UI
        self.start_button.config(text=Messages.GUI_TEXTS['start_system'])

        self.video_label.config(image="", text="攝影機未啟動")
        self.key_display.config(text="－")
        
        logger.info("系統已停止")
    

    
    def toggle_voice_mode(self):
        """切換語音模式"""
        is_enabled = self.voice_enabled.get()
        self.audio_manager.set_enabled(is_enabled)
        
        # 注意：voice_instruction_manager 只用於連續語音指令，不必要時可以略過
        logger.info(f"語音模式已{'開啟' if is_enabled else '關閉'}")
    
    def on_volume_change(self, value):
        """音量改變回調"""
        volume = float(value) / 100.0
        self.audio_manager.set_volume(volume)
    
    def on_window_resize(self, event):
        """視窗大小變化事件處理（即時響應版本）"""
        # 只處理主視窗的變化事件，忽略子組件的變化
        if event.widget == self.root:
            # 立即重置緩存尺寸，強制重新計算影像尺寸
            self.cached_widget_size = (640, 480)  # 重置為預設值，觸發重新計算
            self.size_update_counter = 0  # 重置計數器，立即更新
            
            # 立即觸發一次GUI更新，不等待下一個循環
            if self.is_running and self.current_frame is not None:
                self.root.after_idle(self.update_gui)
            
            logger.debug(f"視窗大小已變化為 {event.width}x{event.height}，將立即重新調整影像尺寸")
    
    def detection_worker(self):
        """優化的檢測工作線程 - 專注於幀處理"""
        frame_count = 0
        
        while self.is_running:
            try:
                # 讀取幀
                frame = self.camera_manager.read_frame()
                if frame is None:
                    continue
                
                frame_count += 1
                
                # 處理幀（優化：減少不必要的處理）
                processed_frame, results = self.pose_detector.process_frame(frame)
                self.current_frame = processed_frame
                
                # 檢查校準狀態和語音提示（優化：避免重複播放）
                calibration_status = results['calibration_status']
                
                if isinstance(calibration_status, dict):
                    # 新的校準結果格式，包含語音提示
                    voice_prompt = calibration_status.get('voice_prompt')
                    if voice_prompt and self.voice_enabled.get():
                        # PoseDetector已經處理了冷卻邏輯，直接播放
                        self.audio_manager.speak(voice_prompt)
                    
                    if calibration_status.get('completed') and not self.pose_detector.is_calibrated:
                        # 校準完成時只會觸發一次
                        pass
                else:
                    # 向後兼容：處理舊的布爾格式
                    if calibration_status and not self.pose_detector.is_calibrated and self.voice_enabled.get():
                        self.audio_manager.speak(Messages.CALIBRATION_SUCCESS)
                
                # 處理觸發的動作
                if self.pose_detector.is_calibrated:
                    triggered_actions = self.pose_detector.get_triggered_actions()
                    for action in triggered_actions:
                        self.handle_action_triggered(action)
                
                # 更新系統監控 - 直接在檢測線程中計算FPS
                system_monitor.update_fps()
                
                # 優化：控制檢測幀率為20FPS，大幅減少CPU使用率
                time.sleep(0.05)
                
            except Exception as e:
                logger.error(f"檢測線程錯誤: {e}")
    
    def handle_action_triggered(self, action: str):
        """處理觸發的動作"""
        # 檢查動作是否啟用
        if not self.action_enabled[action].get():
            return
        
        # 獲取對應按鍵
        key = Messages.get_action_key(action)
        
        # 模擬按鍵
        if keyboard_sim.press_key(key):
            self.last_action = Messages.get_success_message(action)
            self.last_key = key
            
            # 播放成功語音
            if self.voice_enabled.get():
                self.audio_manager.play_action_success(action)
            
            logger.info(f"動作觸發: {action} → {key}")
    
    def gui_update_worker(self):
        """優化的GUI更新工作線程 - 使用after方法確保線程安全"""
        def schedule_update():
            if self.is_running:
                try:
                    if self.current_frame is not None:
                        self.update_gui()
                except Exception as e:
                    logger.error(f"GUI更新錯誤: {e}")
                finally:
                    # 調度下一次更新 - 16ms為60FPS，提供最流暢的縮放響應
                    self.root.after(16, schedule_update)
        
        # 啟動GUI更新循環
        self.root.after(50, schedule_update)  # 略微延遲開始以確保系統初始化完成
    
    def update_gui(self):
        """更新GUI顯示"""
        try:
            # 更新視頻顯示
            if self.current_frame is not None:
                self.update_video_display(self.current_frame)
            
            # 更新狀態信息
            self.update_status_display()
            
            # 更新按鍵顯示
            self.update_key_display()
            
        except Exception as e:
            logger.error(f"更新GUI時發生錯誤: {e}")
    
    def update_video_display(self, frame: np.ndarray):
        """更新視頻顯示（超快響應版本）"""
        try:
            # 極速優化：每幀都檢查視窗尺寸變化以實現即時響應
            self.size_update_counter += 1
            should_update_size = True  # 每幀都檢查以實現最快響應
            
            if should_update_size:
                try:
                    widget_width = self.video_label.winfo_width()
                    widget_height = self.video_label.winfo_height()
                    
                    # 降低最小尺寸要求，讓小視窗也能正常顯示
                    if widget_width > 50 and widget_height > 50:
                        # 檢查尺寸是否真的改變了，避免不必要的更新
                        if (widget_width, widget_height) != self.cached_widget_size:
                            self.cached_widget_size = (widget_width, widget_height)
                            logger.debug(f"視窗尺寸已更新為: {widget_width}x{widget_height}")
                except Exception as e:
                    logger.debug(f"獲取視窗尺寸時發生錯誤: {e}")
            
            widget_width, widget_height = self.cached_widget_size
            
            # 獲取原始圖像尺寸
            frame_height, frame_width = frame.shape[:2]
            
            # 計算縮放比例，保持寬高比（移除最大縮放限制以允許放大）
            scale_w = widget_width / frame_width
            scale_h = widget_height / frame_height
            scale = min(scale_w, scale_h)  # 移除1.0的限制，允許放大顯示
            
            # 計算新的尺寸（確保最小為32x32，最適合小視窗顯示）
            new_width = max(int(frame_width * scale), 32)
            new_height = max(int(frame_height * scale), 32)
            
            # 確保尺寸不會超過視窗大小
            new_width = min(new_width, widget_width)
            new_height = min(new_height, widget_height)
            
            # 調整圖像大小（使用平衡的插值方法）
            resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            
            # 轉換為PIL圖像
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            photo = ImageTk.PhotoImage(pil_image)
            
            # 更新標籤（使用after方法確保線程安全）
            def update_label():
                try:
                    self.video_label.config(image=photo, text="")
                    self.current_photo = photo  # 保持引用
                except:
                    pass
            
            self.root.after_idle(update_label)
            
        except Exception as e:
            logger.error(f"更新視頻顯示時發生錯誤: {e}")
    
    def update_status_display(self):
        """更新狀態顯示（優化版本）"""
        try:
            # 系統狀態
            if self.pose_detector.is_calibrated:
                status = "系統就緒 - 檢測中"
            elif self.is_running:
                status = "校準中..."
            else:
                status = "系統待機中"
            
            # 使用after_idle確保線程安全
            def update_labels():
                try:
                    self.status_label.config(text=status)
                    
                    # FPS
                    fps = system_monitor.get_fps()
                    self.fps_label.config(text=f"FPS: {fps:.1f}")
                    
                    # 運行時間
                    runtime = system_monitor.get_runtime()
                    self.runtime_label.config(text=f"運行時間: {runtime}")
                    
                    # 最後動作
                    if self.last_action:
                        self.last_action_label.config(text=f"最後動作: {self.last_action}")
                except:
                    pass
            
            self.root.after_idle(update_labels)
            
        except Exception as e:
            logger.error(f"更新狀態顯示時發生錯誤: {e}")
    
    def update_key_display(self):
        """更新按鍵顯示"""
        try:
            if self.last_key:
                self.key_display.config(text=self.last_key, foreground="green")
                # 1秒後恢復
                self.root.after(1000, lambda: self.key_display.config(text="－", foreground="red"))
                self.last_key = ""  # 清除以避免重複顯示
                
        except Exception as e:
            logger.error(f"更新按鍵顯示時發生錯誤: {e}")
    
    def on_closing(self):
        """窗口關閉事件"""
        try:
            # 停止系統
            if self.is_running:
                self.stop_system()
            
            # 清理資源
            self.pose_detector.cleanup()
            self.audio_manager.cleanup()
            
            # 關閉窗口
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"關閉應用時發生錯誤: {e}")
        finally:
            self.root.quit()
    
    def run(self):
        """運行GUI應用"""
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"運行GUI應用時發生錯誤: {e}")


class ActionConfigDialog:
    """動作配置對話框"""
    
    def __init__(self, parent):
        """初始化配置對話框"""
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()
    
    def setup_dialog(self):
        """設定對話框"""
        self.dialog.title("動作配置")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # 模態對話框
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # TODO: 實現動作配置界面
        ttk.Label(self.dialog, text="動作配置功能（待實現）").pack(pady=20)
        
        # 關閉按鈕
        ttk.Button(
            self.dialog,
            text="關閉",
            command=self.dialog.destroy
        ).pack(pady=10)


def main():
    """主函數"""
    try:
        app = PoseDetectionGUI()
        app.run()
    except Exception as e:
        logger.error(f"應用啟動失敗: {e}")


if __name__ == "__main__":
    main()