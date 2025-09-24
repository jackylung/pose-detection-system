"""
使用 pyttsx3 和本地 Microsoft Tracy 粵語語音的音訊管理器
"""

import os
import pyttsx3
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any
import hashlib

from messages import SystemConfig, Messages
from utils import logger


class PyttsTTSAudioManager:
    """使用 pyttsx3 和本地粵語語音的音訊管理器"""
    
    def __init__(self):
        """初始化音訊管理器"""
        self.engine = None
        self.is_enabled = True
        self.volume = 0.7
        self.rate = 150
        self.voice_id = None
        self.is_speaking = False
        
        # 粵語語音ID（Microsoft Tracy - Hong Kong Cantonese）
        self.cantonese_voice_id = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ZH-HK_TRACY_11.0"
        
        self._initialize_engine()
        logger.info("pyttsx3粵語語音管理器初始化完成")
    
    def _initialize_engine(self):
        """初始化TTS引擎"""
        try:
            self.engine = pyttsx3.init()
            
            # 設置基本屬性
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            
            # 嘗試設置粵語語音
            if self._set_cantonese_voice():
                logger.info("成功設置粵語語音：Microsoft Tracy (香港)")
            else:
                logger.warning("未能設置粵語語音，使用預設語音")
            
            return True
            
        except Exception as e:
            logger.error(f"TTS引擎初始化失敗: {e}")
            return False
    
    def _set_cantonese_voice(self) -> bool:
        """設置粵語語音"""
        try:
            if not self.engine:
                return False
                
            voices = self.engine.getProperty('voices')
            if not voices:
                return False
            
            # 查找香港粵語語音
            for voice in voices:
                if voice and (('zh-HK' in str(voice.languages) if voice.languages else False) or 
                             ('HongKong' in voice.name if voice.name else False) or 
                             ('Tracy' in voice.name if voice.name else False)):
                    self.voice_id = voice.id
                    self.engine.setProperty('voice', voice.id)
                    logger.info(f"找到粵語語音: {voice.name}")
                    return True
            
            # 如果沒找到，嘗試直接使用已知的ID
            try:
                self.engine.setProperty('voice', self.cantonese_voice_id)
                self.voice_id = self.cantonese_voice_id
                logger.info("使用直接設定的粵語語音ID")
                return True
            except:
                pass
                
            return False
            
        except Exception as e:
            logger.error(f"設置粵語語音失敗: {e}")
            return False
    
    def speak(self, text: str) -> bool:
        """
        播放語音
        
        Args:
            text: 要播放的文字
            
        Returns:
            bool: 播放是否成功
        """
        if not self.is_enabled or not self.engine:
            return False
        
        try:
            # 防止重複播放
            if self.is_speaking:
                return False
            
            self.is_speaking = True
            
            # 在新線程中播放語音，避免阻塞
            def speak_thread():
                try:
                    logger.info(f"播放粵語語音: {text}")
                    self.engine.say(text)
                    self.engine.runAndWait()
                finally:
                    self.is_speaking = False
            
            thread = threading.Thread(target=speak_thread, daemon=True)
            thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"語音播放失敗: {e}")
            self.is_speaking = False
            return False
    
    def speak_blocking(self, text: str) -> bool:
        """
        阻塞式播放語音
        
        Args:
            text: 要播放的文字
            
        Returns:
            bool: 播放是否成功
        """
        if not self.is_enabled or not self.engine:
            return False
        
        try:
            logger.info(f"阻塞播放粵語語音: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
            return True
            
        except Exception as e:
            logger.error(f"阻塞語音播放失敗: {e}")
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
            if self.engine:
                self.engine.setProperty('volume', self.volume)
            logger.info(f"音量已設定為: {self.volume}")
        except Exception as e:
            logger.error(f"設置音量失敗: {e}")
    
    def set_rate(self, rate: int):
        """
        設置語速
        
        Args:
            rate: 語速 (50-300)
        """
        try:
            self.rate = max(50, min(300, rate))
            if self.engine:
                self.engine.setProperty('rate', self.rate)
            logger.info(f"語速已設定為: {self.rate}")
        except Exception as e:
            logger.error(f"設置語速失敗: {e}")
    
    def stop(self):
        """停止語音播放"""
        try:
            if self.engine:
                self.engine.stop()
            self.is_speaking = False
            logger.info("語音播放已停止")
        except Exception as e:
            logger.error(f"停止語音播放失敗: {e}")
    
    def test_voice(self) -> bool:
        """測試語音功能"""
        test_text = "你好，呢個係粵語語音測試"
        logger.info("開始測試粵語語音...")
        
        success = self.speak_blocking(test_text)
        
        if success:
            logger.info("粵語語音測試成功！")
        else:
            logger.error("粵語語音測試失敗")
        
        return success
    
    def get_available_voices(self) -> list:
        """獲取所有可用語音"""
        try:
            if not self.engine:
                return []
            
            voices = self.engine.getProperty('voices')
            voice_info = []
            
            for voice in voices:
                voice_info.append({
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages,
                    'is_cantonese': 'zh-HK' in str(voice.languages) or 'HongKong' in voice.name
                })
            
            return voice_info
            
        except Exception as e:
            logger.error(f"獲取語音列表失敗: {e}")
            return []
    
    def cleanup(self):
        """清理資源"""
        try:
            if self.engine:
                self.engine.stop()
                self.engine = None
            self.is_speaking = False
            logger.info("pyttsx3語音管理器已清理")
        except Exception as e:
            logger.error(f"清理語音管理器失敗: {e}")


def test_cantonese_voice():
    """測試粵語語音功能"""
    print("測試粵語語音功能...")
    print("=" * 50)
    
    # 創建音訊管理器
    audio_manager = PyttsTTSAudioManager()
    
    # 顯示可用語音
    voices = audio_manager.get_available_voices()
    print(f"\\n找到 {len(voices)} 個語音引擎：")
    
    cantonese_found = False
    for i, voice in enumerate(voices):
        print(f"\\n語音 {i+1}:")
        print(f"  名稱: {voice['name']}")
        print(f"  語言: {voice['languages']}")
        if voice['is_cantonese']:
            print("  *** 粵語語音 ***")
            cantonese_found = True
    
    # 測試語音
    if cantonese_found:
        print("\\n開始測試粵語語音...")
        success = audio_manager.test_voice()
        
        if success:
            print("✅ 粵語語音測試成功！")
            
            # 測試更多文字
            test_sentences = [
                "姿勢檢測系統已啟動",
                "請站立標準姿勢進行校準",
                "成功檢測到舉起左手",
                "成功檢測到舉起右手"
            ]
            
            print("\\n測試系統語音...")
            for sentence in test_sentences:
                print(f"播放: {sentence}")
                audio_manager.speak_blocking(sentence)
                time.sleep(1)
            
            print("✅ 所有測試完成！")
        else:
            print("❌ 粵語語音測試失敗")
    else:
        print("❌ 未找到粵語語音包")
        print("建議安裝 Windows 粵語語音包")
    
    # 清理
    audio_manager.cleanup()


if __name__ == "__main__":
    test_cantonese_voice()