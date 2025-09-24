"""
工具模組
包含鍵盤模擬、日誌設定、系統工具等功能
"""

import os
import sys
import time
import threading
from datetime import datetime
from typing import Optional, List
import logging
import logging
from datetime import datetime
from typing import Optional, List

# 設定基本日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pose_detection.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('pose_detection')

# 嘗試導入不同的鍵盤模擬庫
try:
    import keyboard
    KEYBOARD_LIB = 'keyboard'
    keyboard_module = keyboard
except ImportError:
    keyboard_module = None
    try:
        from pynput import keyboard as pynput_keyboard
        from pynput.keyboard import Key, Listener
        KEYBOARD_LIB = 'pynput'
    except ImportError:
        KEYBOARD_LIB = None

from messages import SystemConfig


class LoggerSetup:
    """日誌設定類別"""
    
    @staticmethod
    def setup_logger():
        """設定日誌系統"""
        logger = logging.getLogger('pose_detection')
        logger.setLevel(logging.INFO)
        
        # 清除現有處理器
        logger.handlers.clear()
        
        # 檔案處理器
        file_handler = logging.FileHandler('pose_detection.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 控制台處理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 格式化
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        logger.info("日誌系統初始化完成")
        return logger


class KeyboardSimulator:
    """鍵盤模擬器類別"""
    
    def __init__(self):
        """初始化鍵盤模擬器"""
        self.last_key_time = {}
        self.key_cooldown = 0.5  # 縮短按鍵冷卻時間（秒）
        
        if KEYBOARD_LIB is None:
            logger.warning("未找到鍵盤模擬庫，將使用基本模擬")
        else:
            logger.info(f"使用鍵盤模擬庫: {KEYBOARD_LIB}")
    
    def press_key(self, key: str) -> bool:
        """
        模擬按鍵
        
        Args:
            key: 要按下的按鍵字符
            
        Returns:
            bool: 是否成功按下按鍵
        """
        current_time = time.time()
        
        # 檢查冷卻時間
        if key in self.last_key_time:
            if current_time - self.last_key_time[key] < self.key_cooldown:
                logger.debug(f"按鍵 {key} 仍在冷卻中")
                return False
        
        try:
            success = False
            
            if KEYBOARD_LIB == 'keyboard' and keyboard_module:
                # 對於字符按鍵，直接發送字符
                if len(key) == 1 and key.isalnum():
                    keyboard_module.write(key)
                else:
                    # 對於特殊按鍵，使用press_and_release
                    keyboard_module.press_and_release(key.lower())
                success = True
                logger.info(f"使用keyboard庫按下按鍵: {key}")
                
            elif KEYBOARD_LIB == 'pynput':
                from pynput.keyboard import Controller
                kb_controller = Controller()
                # 對於字符按鍵，直接輸入字符
                if len(key) == 1 and key.isalnum():
                    kb_controller.type(key)
                else:
                    # 對於特殊按鍵，使用press/release
                    kb_controller.press(key.lower())
                    kb_controller.release(key.lower())
                success = True
                logger.info(f"使用pynput庫按下按鍵: {key}")
                
            else:
                # 基本模擬（僅記錄）
                logger.info(f"模擬按下按鍵: {key}")
                success = True
            
            if success:
                self.last_key_time[key] = current_time
                
            return success
            
        except Exception as e:
            logger.error(f"按鍵模擬失敗: {key}, 錯誤: {e}")
            return False
    
    def is_key_available(self, key: str) -> bool:
        """檢查按鍵是否可用（不在冷卻中）"""
        current_time = time.time()
        if key in self.last_key_time:
            return current_time - self.last_key_time[key] >= self.key_cooldown
        return True


class USBHIDSimulator:
    """USB HID鍵盤模擬器（高級功能）"""
    
    def __init__(self):
        """初始化USB HID模擬器"""
        self.enabled = False
        self.device = None
        
        # 這裡可以添加USB HID設備初始化代碼
        # 需要額外的硬體支援（如Arduino等）
        logger.info("USB HID模擬器初始化（未啟用）")
    
    def setup_hid_device(self):
        """設定HID設備"""
        # TODO: 實現USB HID設備設定
        pass
    
    def send_key(self, key: str):
        """透過USB HID發送按鍵"""
        if not self.enabled:
            logger.warning("USB HID未啟用")
            return False
        
        # TODO: 實現USB HID按鍵發送
        logger.info(f"USB HID發送按鍵: {key}")
        return True


class SystemMonitor:
    """系統監控類別"""
    
    def __init__(self):
        """初始化系統監控"""
        self.start_time = time.time()
        self.frame_count = 0
        self.fps = 0
        self.last_fps_update = time.time()
        self.fps_frame_count = 0  # 用於FPS計算的幀數
    
    def update_fps(self):
        """更新FPS計算"""
        self.frame_count += 1
        self.fps_frame_count += 1
        current_time = time.time()
        
        # 每秒更新一次FPS
        if current_time - self.last_fps_update >= 1.0:
            time_diff = current_time - self.last_fps_update
            self.fps = self.fps_frame_count / time_diff if time_diff > 0 else 0
            self.fps_frame_count = 0
            self.last_fps_update = current_time
    
    def get_fps(self) -> float:
        """獲取當前FPS"""
        return self.fps
    
    def get_runtime(self) -> str:
        """獲取運行時間"""
        runtime = time.time() - self.start_time
        hours = int(runtime // 3600)
        minutes = int((runtime % 3600) // 60)
        seconds = int(runtime % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class FileManager:
    """檔案管理類別"""
    
    @staticmethod
    def ensure_directory(directory: str):
        """確保目錄存在"""
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"創建目錄: {directory}")
    
    @staticmethod
    def get_sound_file_path(filename: str) -> str:
        """獲取音訊檔案完整路徑"""
        FileManager.ensure_directory(SystemConfig.SOUND_DIR)
        return os.path.join(SystemConfig.SOUND_DIR, f"{filename}.{SystemConfig.SOUND_FORMAT}")
    
    @staticmethod
    def file_exists(filepath: str) -> bool:
        """檢查檔案是否存在"""
        return os.path.exists(filepath)
    
    @staticmethod
    def get_file_size(filepath: str) -> int:
        """獲取檔案大小"""
        if FileManager.file_exists(filepath):
            return os.path.getsize(filepath)
        return 0


class ActionBuffer:
    """動作緩衝器 - 用於實現容錯機制"""
    
    def __init__(self, buffer_size: int = 30):
        """
        初始化動作緩衝器
        
        Args:
            buffer_size: 緩衝區大小（幀數）
        """
        self.buffer_size = buffer_size
        self.buffers = {}
        self.action_states = {}
        self.action_start_times = {}  # 記錄動作開始時間
        self.action_durations = {}    # 記錄動作持續時間
    
    def add_detection(self, action: str, detected: bool):
        """
        添加動作檢測結果
        
        Args:
            action: 動作名稱
            detected: 是否檢測到動作
        """
        import time
        
        if action not in self.buffers:
            self.buffers[action] = []
            self.action_states[action] = False
            self.action_start_times[action] = 0
            self.action_durations[action] = 0
        
        # 添加檢測結果到緩衝區
        self.buffers[action].append(detected)
        
        # 維持緩衝區大小
        if len(self.buffers[action]) > self.buffer_size:
            self.buffers[action].pop(0)
        
        # 記錄動作開始時間和持續時間
        current_time = time.time()
        if detected and self.action_start_times[action] == 0:
            # 動作開始
            self.action_start_times[action] = current_time
            self.action_durations[action] = 0
        elif detected and self.action_start_times[action] > 0:
            # 動作持續
            self.action_durations[action] = current_time - self.action_start_times[action]
        elif not detected:
            # 動作結束
            self.action_start_times[action] = 0
            self.action_durations[action] = 0
    
    def is_action_stable(self, action: str, stability_ratio: float = 0.8) -> bool:
        """
        檢查動作是否穩定檢測到
        
        Args:
            action: 動作名稱
            stability_ratio: 穩定比例閾值
            
        Returns:
            bool: 動作是否穩定
        """
        if action not in self.buffers:
            return False
            
        # 如果緩衝區還不滿，動作還不穩定
        if len(self.buffers[action]) < self.buffer_size:
            return False
        
        # 計算檢測到的比例
        detected_count = sum(self.buffers[action])
        detection_ratio = detected_count / len(self.buffers[action])
        
        # 檢查動作是否持續了足夠長的時間（至少1秒）
        duration_stable = self.action_durations.get(action, 0) >= 1.0
        
        return detection_ratio >= stability_ratio and duration_stable
    
    def should_trigger_action(self, action: str) -> bool:
        """
        判斷是否應該觸發動作
        
        Args:
            action: 動作名稱
            
        Returns:
            bool: 是否應該觸發
        """
        current_stable = self.is_action_stable(action)
        previous_state = self.action_states.get(action, False)
        
        # 只有當動作從不穩定變為穩定時才觸發
        if current_stable and not previous_state:
            self.action_states[action] = True
            return True
        elif not current_stable:
            self.action_states[action] = False
        
        return False
    
    def reset_action(self, action: str):
        """重置特定動作的緩衝區"""
        if action in self.buffers:
            self.buffers[action].clear()
            self.action_states[action] = False
            self.action_start_times[action] = 0
            self.action_durations[action] = 0
    
    def reset_all(self):
        """重置所有動作的緩衝區"""
        for action in self.buffers:
            self.reset_action(action)


class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self):
        """初始化性能分析器"""
        self.timings = {}
        self.counters = {}
    
    def start_timing(self, name: str):
        """開始計時"""
        self.timings[name] = time.time()
    
    def end_timing(self, name: str) -> Optional[float]:
        """結束計時並返回耗時"""
        if name in self.timings:
            duration = time.time() - self.timings[name]
            del self.timings[name]
            return duration
        return None
    
    def increment_counter(self, name: str):
        """增加計數器"""
        self.counters[name] = self.counters.get(name, 0) + 1
    
    def get_counter(self, name: str) -> int:
        """獲取計數器值"""
        return self.counters.get(name, 0)
    
    def reset_counters(self):
        """重置所有計數器"""
        self.counters.clear()


# 全域工具實例
logger = LoggerSetup.setup_logger()
keyboard_sim = KeyboardSimulator()
system_monitor = SystemMonitor()
action_buffer = ActionBuffer()
profiler = PerformanceProfiler()


def get_timestamp() -> str:
    """獲取當前時間戳字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_execute(func, *args, **kwargs):
    """安全執行函數，捕獲異常"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"執行函數 {func.__name__} 時發生錯誤: {e}")
        return None