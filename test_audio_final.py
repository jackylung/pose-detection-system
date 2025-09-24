"""
最終音訊系統測試
測試修復後的單一音訊管理器實例
"""

import sys
import os
import time

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_manager_cantonese_fixed import CantoneseAudioManagerFixed
from utils import LoggerSetup

def test_single_instance_audio():
    """測試單一實例音訊管理器"""
    print("🎵 測試單一實例音訊管理器")
    print("=" * 50)
    
    # 設定日誌
    LoggerSetup.setup_logger()
    
    # 創建單一音訊管理器實例
    audio_manager = CantoneseAudioManagerFixed()
    
    print(f"🎯 引擎類型: {'本地粵語語音' if audio_manager.use_local_voice else 'gTTS'}")
    print(f"🔊 音量設定: {audio_manager.volume}")
    print(f"⚡ 語音啟用: {audio_manager.is_enabled}")
    
    # 測試連續播放（模擬GUI環境中的情況）
    test_messages = [
        "姿勢檢測系統已啟動",  # 系統啟動
        "成功檢測到舉起右手",   # 動作檢測
        "舉起左手等於A鍵。舉起右手等於B鍵。舉起左腳等於C鍵。舉起右腳等於D鍵。向左轉身等於E鍵。向右轉身等於F鍵。點點頭等於G鍵",  # 動作說明
        "校準完成",            # 校準成功
        "測試完成"             # 結束
    ]
    
    success_count = 0
    total_tests = len(test_messages)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🔄 測試 {i}/{total_tests}: {message[:20]}...")
        
        start_time = time.time()
        success = audio_manager.speak(message)
        end_time = time.time()
        
        # 等待播放完成
        timeout = 30  # 30秒超時
        wait_start = time.time()
        while audio_manager.is_speaking and (time.time() - wait_start < timeout):
            time.sleep(0.1)
        
        duration = end_time - start_time
        
        if success:
            print(f"   ✅ 播放成功 ({duration:.2f}秒)")
            success_count += 1
        else:
            print(f"   ❌ 播放失敗 ({duration:.2f}秒)")
        
        # 短暫間隔防止衝突  
        time.sleep(0.5)
    
    # 統計結果
    success_rate = (success_count / total_tests) * 100
    print(f"\n📊 最終結果: {success_count}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 測試通過！音訊系統修復成功！")
        print("📝 建議：現在可以執行 main.py 測試完整系統")
    else:
        print("⚠️  測試失敗，需要進一步調試")
    
    # 清理
    print("\n🧹 清理音訊管理器...")
    audio_manager.cleanup()
    print("✅ 測試完成")

if __name__ == "__main__":
    test_single_instance_audio()