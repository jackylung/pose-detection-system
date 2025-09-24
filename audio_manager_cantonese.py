"""
粵語音訊管理模組
優先使用本地 Microsoft Tracy 粵語語音，備用 gTTS
"""

import os
import pygame
import tempfile
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any
import hashlib
import queue

# 嘗試導入 pyttsx3
try:
    import pyttsx3
    from pyttsx3.engine import Engine
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    pyttsx3 = None
    Engine = None

# 嘗試導入 gTTS
try:
    from gtts import gTTS as gTTSClass
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    gTTSClass = None

from messages import SystemConfig, Messages
from utils import logger


class CantoneseAudioManager:
    """粵語音訊管理器"""
    
    def __init__(self):
        """初始化音訊管理器"""
        self.engine: Optional[Any] = None
        self.is_enabled = True
        self.volume = 0.7
        self.rate = 150
        self.voice_id = None
        self.is_speaking = False
        self.use_local_voice = False
        self._engine_lock = threading.Lock()  # 加入線程鎖
        self._speech_queue = queue.Queue()  # 音訊佇列
        
        # 音訊目錄
        self.sound_dir = Path(SystemConfig.SOUND_DIR)
        self.sound_dir.mkdir(exist_ok=True)
        
        # 嘗試初始化本地粵語語音
        if PYTTSX3_AVAILABLE:
            if self._initialize_local_voice():
                self.use_local_voice = True
                logger.info("使用本地粵語語音引擎")
            else:
                logger.warning("本地粵語語音初始化失敗，將使用 gTTS")
        
        # 如果本地語音不可用，初始化 pygame
        if not self.use_local_voice:
            self._initialize_audio_system()
            self._pregenerate_common_sounds()
        
        # 設置語音處理線程
        if self.use_local_voice:
            self._speech_worker_thread = threading.Thread(
                target=self._speech_worker, daemon=True
            )
            self._speech_worker_thread.start()
            logger.info("語音處理線程已啟動")
        
        logger.info("粵語音訊管理器初始化完成")
    
    def _initialize_local_voice(self) -> bool:
        """初始化本地粵語語音引擎"""
        if not PYTTSX3_AVAILABLE:
            return False
            
        try:
            assert pyttsx3 is not None  # Type guard
            self.engine = pyttsx3.init()
            
            # 設置基本屬性
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            
            # 查找並設置粵語語音
            voices = self.engine.getProperty('voices')
            if not voices:
                return False
            
            # 查找香港粵語語音 (Microsoft Tracy)
            for voice in voices:
                if voice and (('zh-HK' in str(voice.languages) if voice.languages else False) or
                             ('HongKong' in voice.name if voice.name else False) or
                             ('Tracy' in voice.name if voice.name else False)):
                    self.voice_id = voice.id
                    self.engine.setProperty('voice', voice.id)
                    logger.info(f"找到粵語語音: {voice.name}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"本地語音引擎初始化失敗: {e}")
            return False
    
    def _speech_worker(self):
        """語音處理工作線程"""
        while True:
            try:
                # 從佇列中獲取語音任務
                text = self._speech_queue.get(timeout=1)
                if text is None:  # 停止信號
                    break
                
                # 使用線程鎖保護語音引擎
                with self._engine_lock:
                    self._safe_speak_local(text)
                
                # 標記任務完成
                self._speech_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"語音處理線程錯誤: {e}")
                if not self._speech_queue.empty():
                    self._speech_queue.task_done()
    
    def _safe_speak_local(self, text: str) -> bool:
        """安全的本地語音播放（在線程鎖保護下）"""
        try:
            # 重新初始化引擎
            if not self._reinitialize_engine_unsafe():
                return False
            
            assert self.engine is not None
            logger.info(f"播放粵語語音: {text}")
            
            # 使用同步方式播放
            self.engine.say(text)
            self.engine.runAndWait()
            
            return True
            
        except Exception as e:
            logger.error(f"安全語音播放失敗: {e}")
            return False
    
    def _reinitialize_engine_unsafe(self) -> bool:
        """重新初始化語音引擎（不安全版本，需要在鎖保護下使用）"""
        if not PYTTSX3_AVAILABLE:
            return False
            
        try:
            # 停止並清理現有引擎
            if self.engine:
                try:
                    self.engine.stop()
                except:
                    pass
                self.engine = None
            
            # 重新創建引擎
            assert pyttsx3 is not None  # Type guard
            self.engine = pyttsx3.init()
            
            # 設置屬性
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            
            # 設置語音
            if self.voice_id:
                self.engine.setProperty('voice', self.voice_id)
            
            return True
            
        except Exception as e:
            logger.error(f"重新初始化語音引擎失敗: {e}")
            return False
    
    def _reinitialize_engine(self) -> bool:
        """重新初始化語音引擎（線程安全版本）"""
        with self._engine_lock:
            return self._reinitialize_engine_unsafe()
    
    def _initialize_audio_system(self):
        """初始化 pygame 音訊系統"""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.music.set_volume(self.volume)
            logger.info("pygame音訊系統初始化成功")
        except Exception as e:
            logger.error(f"pygame音訊系統初始化失敗: {e}")
    
    def _pregenerate_common_sounds(self):
        """預生成常用語音檔案"""
        if not GTTS_AVAILABLE:
            logger.error("gTTS 不可用，無法預生成語音檔案")
            return
            
        logger.info("開始預生成語音檔案...")
        
        # 常用訊息
        common_messages = [
            Messages.SYSTEM_START,
            Messages.CALIBRATION_START,
            Messages.CALIBRATION_SUCCESS,
            Messages.CALIBRATION_FAILED,
        ]
        
        # 預生成動作說明
        for action, message in Messages.ACTION_INSTRUCTIONS.items():
            common_messages.append(message)
        
        # 預生成動作成功訊息
        for action, message in Messages.ACTION_SUCCESS.items():
            common_messages.append(message)
        
        # 生成音訊檔案
        for message in common_messages:
            self._generate_audio_file(message)
        
        logger.info("語音檔案預生成完成")
    
    def _generate_audio_file(self, text: str) -> Optional[str]:
        """生成音訊檔案"""
        if not GTTS_AVAILABLE:
            return None
            
        try:
            # 生成檔案名
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            filename = f"voice_{text_hash}.{SystemConfig.SOUND_FORMAT}"
            filepath = self.sound_dir / filename
            
            # 如果檔案已存在，直接返回
            if filepath.exists():
                return str(filepath)
            
            # 生成語音檔案
            if gTTSClass:
                tts = gTTSClass(text=text, lang='zh-TW', slow=SystemConfig.TTS_SLOW)
                tts.save(str(filepath))
            
            logger.info(f"語音檔案已生成: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"生成語音檔案失敗 '{text}': {e}")
            return None
    
    def speak(self, text: str) -> bool:
        """
        播放語音
        
        Args:
            text: 要播放的文字
            
        Returns:
            bool: 播放是否成功
        """
        if not self.is_enabled:
            return False
        
        if self.use_local_voice:
            return self._speak_local(text)
        else:
            return self._speak_gtts(text)
    
    def _speak_local(self, text: str) -> bool:
        """使用本地語音播放（線程安全版本）"""
        try:
            if not self.use_local_voice:
                return False
            
            # 將語音任務放入佇列
            self._speech_queue.put(text)
            logger.info(f"語音任務已加入佇列: {text}")
            
            return True
            
        except Exception as e:
            logger.error(f"本地語音播放失敗: {e}")
            return False
    
    def _speak_gtts(self, text: str) -> bool:
        """使用 gTTS 播放語音"""
        if not GTTS_AVAILABLE:
            return False
        
        try:
            # 嘗試使用預生成的檔案
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            filename = f"voice_{text_hash}.{SystemConfig.SOUND_FORMAT}"
            filepath = self.sound_dir / filename
            
            if not filepath.exists():
                # 即時生成語音檔案
                filepath = self._generate_audio_file(text)
                if not filepath:
                    return False
            
            # 播放音訊檔案
            def play_thread():
                try:
                    pygame.mixer.music.load(str(filepath))
                    pygame.mixer.music.play()
                    
                    # 等待播放完成
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                        
                except Exception as e:
                    logger.error(f"播放音訊檔案失敗: {e}")
            
            thread = threading.Thread(target=play_thread, daemon=True)
            thread.start()
            
            logger.info(f"播放語音檔案: {text}")
            return True
            
        except Exception as e:
            logger.error(f"gTTS語音播放失敗: {e}")
            return False
    
    def speak_blocking(self, text: str) -> bool:
        """
        阻塞式播放語音
        
        Args:
            text: 要播放的文字
            
        Returns:
            bool: 播放是否成功
        """
        if not self.is_enabled:
            return False
        
        if self.use_local_voice:
            return self._speak_local_blocking(text)
        else:
            return self._speak_gtts_blocking(text)
    
    def _speak_local_blocking(self, text: str) -> bool:
        """阻塞式本地語音播放"""
        try:
            if not self.use_local_voice:
                return False
            
            # 直接在當前線程中播放（阻塞式）
            with self._engine_lock:
                return self._safe_speak_local(text)
            
        except Exception as e:
            logger.error(f"阻塞本地語音播放失敗: {e}")
            return False
    
    def _speak_gtts_blocking(self, text: str) -> bool:
        """阻塞式 gTTS 語音播放"""
        if not GTTS_AVAILABLE:
            return False
        
        try:
            # 生成或獲取音訊檔案
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            filename = f"voice_{text_hash}.{SystemConfig.SOUND_FORMAT}"
            filepath = self.sound_dir / filename
            
            if not filepath.exists():
                filepath = self._generate_audio_file(text)
                if not filepath:
                    return False
            
            # 播放音訊檔案
            pygame.mixer.music.load(str(filepath))
            pygame.mixer.music.play()
            
            # 等待播放完成
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            logger.info(f"阻塞播放語音檔案: {text}")
            return True
            
        except Exception as e:
            logger.error(f"阻塞gTTS語音播放失敗: {e}")
            return False
    
    def set_enabled(self, enabled: bool):
        """設置是否啟用語音"""
        self.is_enabled = enabled
        logger.info(f"語音{'啟用' if enabled else '停用'}")
    
    def is_voice_enabled(self) -> bool:
        """檢查語音是否啟用"""
        return self.is_enabled
    
    def set_volume(self, volume: float):
        """
        設置音量
        
        Args:
            volume: 音量 (0.0-1.0)
        """
        try:
            self.volume = max(0.0, min(1.0, volume))
            
            if self.use_local_voice:
                with self._engine_lock:
                    if self.engine:
                        self.engine.setProperty('volume', self.volume)
            else:
                pygame.mixer.music.set_volume(self.volume)
            
            logger.info(f"音量已設定為: {self.volume}")
        except Exception as e:
            logger.error(f"設置音量失敗: {e}")
    
    def set_rate(self, rate: int):
        """
        設置語速 (僅適用於本地語音)
        
        Args:
            rate: 語速 (50-300)
        """
        if not self.use_local_voice:
            logger.warning("gTTS 不支援語速調整")
            return
            
        try:
            self.rate = max(50, min(300, rate))
            with self._engine_lock:
                if self.engine:
                    self.engine.setProperty('rate', self.rate)
            logger.info(f"語速已設定為: {self.rate}")
        except Exception as e:
            logger.error(f"設置語速失敗: {e}")
    
    def stop(self):
        """停止語音播放"""
        try:
            if self.use_local_voice:
                with self._engine_lock:
                    if self.engine:
                        self.engine.stop()
                        self.is_speaking = False
                # 清空佇列
                while not self._speech_queue.empty():
                    try:
                        self._speech_queue.get_nowait()
                        self._speech_queue.task_done()
                    except queue.Empty:
                        break
            else:
                pygame.mixer.music.stop()
            
            logger.info("語音播放已停止")
        except Exception as e:
            logger.error(f"停止語音播放失敗: {e}")
    
    def cleanup(self):
        """清理資源"""
        try:
            self.stop()
            
            # 停止語音處理線程
            if hasattr(self, '_speech_queue'):
                self._speech_queue.put(None)  # 發送停止信號
                if hasattr(self, '_speech_worker_thread'):
                    self._speech_worker_thread.join(timeout=2)
            
            # 清理引擎
            with self._engine_lock:
                if self.use_local_voice and self.engine:
                    try:
                        self.engine.stop()
                    except:
                        pass
                    self.engine = None
                else:
                    pygame.mixer.quit()
            
            self.is_speaking = False
            logger.info("粵語音訊管理器已清理")
        except Exception as e:
            logger.error(f"清理音訊管理器失敗: {e}")
    
    @property
    def is_initialized(self) -> bool:
        """檢查音訊管理器是否已初始化"""
        if self.use_local_voice:
            return self.engine is not None
        else:
            return pygame.mixer.get_init() is not None
    
    def play_system_start(self):
        """播放系統啟動語音"""
        self.speak(Messages.SYSTEM_START)
    
    def play_calibration_start(self):
        """播放校準開始語音"""
        self.speak(Messages.CALIBRATION_START)
    
    def play_calibration_success(self):
        """播放校準成功語音"""
        self.speak(Messages.CALIBRATION_SUCCESS)
    
    def play_action_instructions(self):
        """播放動作說明語音"""
        instructions = Messages.get_all_instructions()
        self.speak(instructions)
    
    def play_action_success(self, action: str):
        """
        播放動作成功語音
        
        Args:
            action: 動作名稱
        """
        success_message = Messages.get_success_message(action)
        self.speak(success_message)


def test_cantonese_audio():
    """測試粵語音訊功能"""
    print("測試粵語音訊管理器...")
    print("=" * 50)
    
    # 創建音訊管理器
    audio_manager = CantoneseAudioManager()
    
    # 測試語音
    test_sentences = [
        "你好，呢個係粵語語音測試",
        "姿勢檢測系統已啟動",
        "請站立標準姿勢進行校準",
        "成功檢測到舉起左手",
        "成功檢測到舉起右手"
    ]
    
    print(f"使用{'本地粵語語音' if audio_manager.use_local_voice else 'gTTS語音'}引擎")
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\\n測試 {i}: {sentence}")
        success = audio_manager.speak_blocking(sentence)
        if success:
            print("✅ 播放成功")
        else:
            print("❌ 播放失敗")
        time.sleep(1)
    
    print("\\n✅ 測試完成！")
    
    # 清理
    audio_manager.cleanup()


if __name__ == "__main__":
    test_cantonese_audio()