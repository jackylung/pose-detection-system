"""
語音管理模組
負責語音合成、播放控制和音訊檔案管理
"""

import os
import threading
import time
from typing import Optional, Dict, List
import hashlib

# 嘗試導入音訊相關庫
try:
    import pygame
    PYGAME_AVAILABLE = True
    pygame_module = pygame
except ImportError:
    PYGAME_AVAILABLE = False
    pygame_module = None

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
    gtts_module = gTTS
except ImportError:
    GTTS_AVAILABLE = False
    gtts_module = None

from messages import Messages, SystemConfig
from utils import logger, FileManager


class AudioManager:
    """語音管理器類別"""
    
    def __init__(self):
        """初始化語音管理器"""
        self.is_initialized = False
        self.is_muted = False
        self.current_volume = 0.7
        self.voice_queue = []
        self.is_playing = False
        self.play_thread = None
        
        # 音訊緩存
        self.audio_cache = {}
        
        # 初始化音訊系統
        self._initialize_audio_system()
        
        # 預生成常用語音
        self._pregenerate_common_sounds()
        
        logger.info("語音管理器初始化完成")
    
    def _initialize_audio_system(self) -> bool:
        """
        初始化音訊系統
        
        Returns:
            bool: 是否成功初始化
        """
        if not PYGAME_AVAILABLE or not pygame_module:
            logger.warning("pygame未安裝，語音功能將受限")
            return False
        
        try:
            pygame_module.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.is_initialized = True
            logger.info("pygame音訊系統初始化成功")
            return True
        except Exception as e:
            logger.error(f"音訊系統初始化失敗: {e}")
            return False
    
    def _pregenerate_common_sounds(self):
        """預生成常用語音檔案"""
        if not GTTS_AVAILABLE or not gtts_module:
            logger.warning("gTTS未安裝，無法生成語音檔案")
            return
        
        # 需要預生成的語音文字
        texts_to_generate = [
            Messages.SYSTEM_START,
            Messages.CALIBRATION_START,
            Messages.CALIBRATION_SUCCESS,
            Messages.get_all_instructions()
        ]
        
        # 添加動作成功訊息
        for action_message in Messages.ACTION_SUCCESS.values():
            texts_to_generate.append(action_message)
        
        # 添加動作說明
        for instruction in Messages.ACTION_INSTRUCTIONS.values():
            texts_to_generate.append(instruction)
        
        logger.info("開始預生成語音檔案...")
        
        for text in texts_to_generate:
            try:
                self._generate_audio_file(text)
            except Exception as e:
                logger.error(f"生成語音檔案失敗: {text}, 錯誤: {e}")
        
        logger.info("語音檔案預生成完成")
    
    def _generate_audio_file(self, text: str) -> Optional[str]:
        """
        生成語音檔案
        
        Args:
            text: 要轉換的文字
            
        Returns:
            Optional[str]: 生成的檔案路徑，失敗時返回None
        """
        if not GTTS_AVAILABLE or not gtts_module:
            logger.warning("gTTS不可用，無法生成語音檔案")
            return None
        
        try:
            # 生成檔案名（使用文字的hash值）
            text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:8]
            filename = f"voice_{text_hash}"
            filepath = FileManager.get_sound_file_path(filename)
            
            # 檢查檔案是否已存在
            if FileManager.file_exists(filepath):
                logger.debug(f"語音檔案已存在: {filepath}")
                return filepath
            
            # 生成語音檔案
            tts = gtts_module(text=text, lang=SystemConfig.TTS_LANGUAGE, slow=SystemConfig.TTS_SLOW)
            tts.save(filepath)
            
            logger.info(f"語音檔案已生成: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"生成語音檔案時發生錯誤: {e}")
            return None
    
    def play_text(self, text: str, priority: int = 1) -> bool:
        """
        播放文字語音
        
        Args:
            text: 要播放的文字
            priority: 優先級（數字越小越優先）
            
        Returns:
            bool: 是否成功添加到播放佇列
        """
        if self.is_muted:
            logger.debug("語音已靜音，跳過播放")
            return False
        
        if not self.is_initialized:
            logger.warning("音訊系統未初始化，無法播放語音")
            return False
        
        # 生成音訊檔案
        audio_file = self._generate_audio_file(text)
        if not audio_file:
            return False
        
        # 添加到播放佇列
        audio_item = {
            'file': audio_file,
            'text': text,
            'priority': priority,
            'timestamp': time.time()
        }
        
        self.voice_queue.append(audio_item)
        
        # 按優先級排序
        self.voice_queue.sort(key=lambda x: x['priority'])
        
        # 啟動播放線程
        if not self.is_playing:
            self._start_playback_thread()
        
        logger.debug(f"語音已添加到佇列: {text[:20]}...")
        return True
    
    def _start_playback_thread(self):
        """啟動播放線程"""
        if self.play_thread and self.play_thread.is_alive():
            return
        
        self.play_thread = threading.Thread(target=self._playback_worker, daemon=True)
        self.play_thread.start()
    
    def _playback_worker(self):
        """播放工作線程"""
        self.is_playing = True
        
        while self.voice_queue and not self.is_muted:
            try:
                # 獲取下一個要播放的音訊
                audio_item = self.voice_queue.pop(0)
                
                # 播放音訊檔案
                self._play_audio_file(audio_item['file'])
                
                # 等待播放完成
                while pygame_module and pygame_module.mixer.get_busy():
                    time.sleep(0.1)
                
                # 短暫延遲
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"播放音訊時發生錯誤: {e}")
        
        self.is_playing = False
        logger.debug("播放線程結束")
    
    def _play_audio_file(self, filepath: str) -> bool:
        """
        播放音訊檔案
        
        Args:
            filepath: 音訊檔案路徑
            
        Returns:
            bool: 是否成功播放
        """
        if not FileManager.file_exists(filepath) or not pygame_module:
            logger.error(f"音訊檔案不存在或pygame不可用: {filepath}")
            return False
        
        try:
            pygame_module.mixer.music.load(filepath)
            pygame_module.mixer.music.set_volume(self.current_volume)
            pygame_module.mixer.music.play()
            
            logger.debug(f"開始播放音訊: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"播放音訊檔案時發生錯誤: {e}")
            return False
    
    def play_system_start(self):
        """播放系統啟動語音"""
        self.play_text(Messages.SYSTEM_START, priority=0)
    
    def play_calibration_start(self):
        """播放校準開始語音"""
        self.play_text(Messages.CALIBRATION_START, priority=0)
    
    def play_calibration_success(self):
        """播放校準成功語音"""
        self.play_text(Messages.CALIBRATION_SUCCESS, priority=0)
    
    def play_action_instructions(self):
        """播放動作說明語音"""
        instructions = Messages.get_all_instructions()
        self.play_text(instructions, priority=1)
    
    def play_action_success(self, action: str):
        """
        播放動作成功語音
        
        Args:
            action: 動作名稱
        """
        success_message = Messages.get_success_message(action)
        self.play_text(success_message, priority=0)
    
    def play_instruction_loop(self, interval: float = 10.0):
        """
        循環播放動作說明
        
        Args:
            interval: 播放間隔（秒）
        """
        def loop_worker():
            while not self.is_muted:
                self.play_action_instructions()
                time.sleep(interval)
        
        loop_thread = threading.Thread(target=loop_worker, daemon=True)
        loop_thread.start()
        logger.info("開始循環播放動作說明")
    
    def set_mute(self, muted: bool):
        """
        設定靜音模式
        
        Args:
            muted: 是否靜音
        """
        self.is_muted = muted
        
        if muted:
            self.stop_all_playback()
            logger.info("語音已靜音")
        else:
            logger.info("語音已開啟")
    
    def is_mute(self) -> bool:
        """獲取當前靜音狀態"""
        return self.is_muted
    
    def set_volume(self, volume: float):
        """
        設定音量
        
        Args:
            volume: 音量（0.0-1.0）
        """
        self.current_volume = max(0.0, min(1.0, volume))
        if self.is_initialized and pygame_module:
            pygame_module.mixer.music.set_volume(self.current_volume)
        logger.info(f"音量已設定為: {self.current_volume}")
    
    def get_volume(self) -> float:
        """獲取當前音量"""
        return self.current_volume
    
    def stop_current_playback(self):
        """停止當前播放"""
        if self.is_initialized and pygame_module:
            pygame_module.mixer.music.stop()
        logger.debug("已停止當前播放")
    
    def stop_all_playback(self):
        """停止所有播放並清空佇列"""
        self.voice_queue.clear()
        self.stop_current_playback()
        logger.debug("已停止所有播放並清空佇列")
    
    def get_queue_size(self) -> int:
        """獲取播放佇列大小"""
        return len(self.voice_queue)
    
    def is_busy(self) -> bool:
        """檢查是否正在播放"""
        if not self.is_initialized or not pygame_module:
            return False
        return bool(pygame_module.mixer.get_busy()) or bool(self.voice_queue)
    
    def cleanup(self):
        """清理資源"""
        self.stop_all_playback()
        if self.is_initialized and pygame_module:
            pygame_module.mixer.quit()
        logger.info("語音管理器已清理")


class VoiceInstructionManager:
    """語音說明管理器"""
    
    def __init__(self, audio_manager: AudioManager):
        """
        初始化語音說明管理器
        
        Args:
            audio_manager: 語音管理器實例
        """
        self.audio_manager = audio_manager
        self.instruction_thread = None
        self.is_running = False
        self.interval = 15.0  # 預設間隔15秒
    
    def start_continuous_instructions(self, interval: float = 15.0):
        """
        開始連續播放動作說明
        
        Args:
            interval: 播放間隔（秒）
        """
        if self.is_running:
            return
        
        self.interval = interval
        self.is_running = True
        
        def instruction_worker():
            while self.is_running:
                if not self.audio_manager.is_mute():
                    self.audio_manager.play_action_instructions()
                
                # 分段等待，便於快速響應停止信號
                for _ in range(int(interval * 10)):
                    if not self.is_running:
                        break
                    time.sleep(0.1)
        
        self.instruction_thread = threading.Thread(target=instruction_worker, daemon=True)
        self.instruction_thread.start()
        
        logger.info(f"開始連續播放動作說明，間隔: {interval}秒")
    
    def stop_continuous_instructions(self):
        """停止連續播放動作說明"""
        self.is_running = False
        if self.instruction_thread:
            self.instruction_thread.join(timeout=1.0)
        logger.info("停止連續播放動作說明")
    
    def is_active(self) -> bool:
        """檢查是否正在連續播放"""
        return self.is_running


class AudioTester:
    """音訊測試器"""
    
    def __init__(self):
        """初始化音訊測試器"""
        self.audio_manager = AudioManager()
    
    def test_basic_playback(self):
        """測試基本播放功能"""
        logger.info("開始測試基本播放功能...")
        
        test_texts = [
            "測試語音播放",
            "系統正常運作",
            "音訊測試完成"
        ]
        
        for text in test_texts:
            self.audio_manager.play_text(text)
            time.sleep(2)
        
        logger.info("基本播放功能測試完成")
    
    def test_action_voices(self):
        """測試動作語音"""
        logger.info("開始測試動作語音...")
        
        # 測試系統語音
        self.audio_manager.play_system_start()
        time.sleep(3)
        
        self.audio_manager.play_calibration_start()
        time.sleep(3)
        
        # 測試動作成功語音
        for action in Messages.ACTION_KEYS.keys():
            self.audio_manager.play_action_success(action)
            time.sleep(2)
        
        logger.info("動作語音測試完成")
    
    def test_volume_control(self):
        """測試音量控制"""
        logger.info("開始測試音量控制...")
        
        volumes = [0.3, 0.6, 1.0, 0.7]
        
        for volume in volumes:
            self.audio_manager.set_volume(volume)
            self.audio_manager.play_text(f"當前音量: {int(volume * 100)}%")
            time.sleep(2)
        
        logger.info("音量控制測試完成")
    
    def test_mute_function(self):
        """測試靜音功能"""
        logger.info("開始測試靜音功能...")
        
        self.audio_manager.play_text("測試靜音前")
        time.sleep(2)
        
        self.audio_manager.set_mute(True)
        self.audio_manager.play_text("這段語音不應該播放")
        time.sleep(1)
        
        self.audio_manager.set_mute(False)
        self.audio_manager.play_text("靜音測試完成")
        time.sleep(2)
        
        logger.info("靜音功能測試完成")
    
    def run_all_tests(self):
        """運行所有測試"""
        logger.info("開始音訊系統完整測試...")
        
        self.test_basic_playback()
        self.test_action_voices()
        self.test_volume_control()
        self.test_mute_function()
        
        logger.info("音訊系統完整測試完成")
        
        # 清理
        self.audio_manager.cleanup()


# 全域音訊管理器實例
audio_manager = AudioManager()
voice_instruction_manager = VoiceInstructionManager(audio_manager)


if __name__ == "__main__":
    # 直接運行時進行測試
    tester = AudioTester()
    tester.run_all_tests()