"""
快速測試修復版粵語音訊系統
驗證連續播放功能
"""

import sys
import os
import time

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_manager_cantonese_fixed import CantoneseAudioManagerFixed
from utils import LoggerSetup

def test_button_functionality():
    """測試按鈕功能"""
    print("🔘 測試按鈕功能模擬")
    print("=" * 40)
    
    # 設定日誌
    LoggerSetup.setup_logger()
    
    # 創建修復版音訊管理器
    audio_manager = CantoneseAudioManagerFixed()
    
    print(f"使用引擎: {'本地粵語語音' if audio_manager.use_local_voice else 'gTTS'}")
    
    # 模擬系統啟動
    print("\n🚀 模擬系統啟動...")
    success1 = audio_manager.play_system_start()
    print(f"系統啟動語音: {'✅ 成功' if success1 else '❌ 失敗'}")
    time.sleep(3)
    
    # 模擬按下「播放動作說明」按鈕
    print("\n🔘 模擬按下「播放動作說明」按鈕...")
    success2 = audio_manager.play_action_instructions()
    print(f"動作說明語音: {'✅ 成功' if success2 else '❌ 失敗'}")
    time.sleep(5)
    
    # 模擬校準成功
    print("\n🎯 模擬校準成功...")
    success3 = audio_manager.play_calibration_success()
    print(f"校準成功語音: {'✅ 成功' if success3 else '❌ 失敗'}")
    time.sleep(3)
    
    # 模擬動作成功
    print("\n🏃 模擬動作觸發...")
    success4 = audio_manager.play_action_success('left_hand')
    print(f"左手動作語音: {'✅ 成功' if success4 else '❌ 失敗'}")
    time.sleep(3)
    
    # 再次按下「播放動作說明」按鈕
    print("\n🔘 再次按下「播放動作說明」按鈕...")
    success5 = audio_manager.play_action_instructions()
    print(f"再次動作說明語音: {'✅ 成功' if success5 else '❌ 失敗'}")
    
    # 統計結果
    total_tests = 5
    successful_tests = sum([1 for result in [success1, success2, success3, success4, success5] if result])
    
    print(f"\n📊 測試結果: {successful_tests}/{total_tests} ({'100%' if successful_tests == total_tests else f'{successful_tests/total_tests*100:.1f}%'})")
    
    if successful_tests == total_tests:
        print("🎉 所有測試通過！音訊系統修復成功！")
    else:
        print("⚠️  部分測試失敗，仍需修復")
    
    # 清理
    audio_manager.cleanup()

if __name__ == "__main__":
    test_button_functionality()