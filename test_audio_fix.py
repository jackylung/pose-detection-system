#!/usr/bin/env python3
"""
測試修正後的音訊功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_manager_cantonese import CantoneseAudioManager
from messages import Messages

def test_audio_fix():
    """測試音訊修正"""
    print("測試修正後的粵語音訊功能...")
    print("=" * 50)
    
    # 創建音訊管理器
    audio_manager = CantoneseAudioManager()
    
    print(f"音訊管理器初始化: {'✅' if audio_manager.is_initialized else '❌'}")
    print(f"使用本地語音: {'✅' if audio_manager.use_local_voice else '❌'}")
    print(f"初始音量: {audio_manager.volume}")
    print(f"語音啟用: {'✅' if audio_manager.is_enabled else '❌'}")
    
    # 測試音量設定
    print("\n測試音量設定...")
    audio_manager.set_volume(0.8)
    print(f"設定音量後: {audio_manager.volume}")
    
    # 測試語音播放
    print("\n測試語音播放...")
    test_messages = [
        "音訊測試開始",
        Messages.SYSTEM_START,
        Messages.CALIBRATION_SUCCESS,
        "測試完成"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"  測試 {i}: {message}")
        success = audio_manager.speak(message)
        print(f"    結果: {'✅ 成功' if success else '❌ 失敗'}")
        # 等待播放完成
        import time
        time.sleep(2)
    
    # 清理
    audio_manager.cleanup()
    print("\n✅ 測試完成！")

if __name__ == "__main__":
    test_audio_fix()