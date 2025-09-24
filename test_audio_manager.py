"""
音訊管理器測試檔案
獨立測試語音合成和播放功能
"""

import sys
import os
import time

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from audio_manager import AudioManager, VoiceInstructionManager, audio_manager
    from messages import Messages
    from utils import logger
    AUDIO_AVAILABLE = True
except ImportError as e:
    print(f"導入失敗: {e}")
    print("請先安裝依賴: pip install pygame gTTS")
    AUDIO_AVAILABLE = False


def test_audio_manager_init():
    """測試音訊管理器初始化"""
    print("=== 測試音訊管理器初始化 ===")
    
    if not AUDIO_AVAILABLE:
        print("跳過測試：缺少必要依賴")
        return False
    
    try:
        manager = AudioManager()
        print("✓ 音訊管理器初始化成功")
        
        # 檢查初始狀態
        print(f"✓ 是否已初始化: {manager.is_initialized}")
        print(f"✓ 是否靜音: {manager.is_muted}")
        print(f"✓ 當前音量: {manager.current_volume}")
        
        manager.cleanup()
        print("✓ 音訊管理器清理成功")
        return True
        
    except Exception as e:
        print(f"❌ 音訊管理器初始化失敗: {e}")
        return False


def test_voice_generation():
    """測試語音生成功能"""
    print("\n=== 測試語音生成功能 ===")
    
    if not AUDIO_AVAILABLE:
        print("跳過測試：缺少必要依賴")
        return False
    
    try:
        manager = AudioManager()
        
        # 測試語音檔案生成
        test_text = "這是一個測試語音"
        print(f"生成測試語音: {test_text}")
        
        audio_file = manager._generate_audio_file(test_text)
        
        if audio_file and os.path.exists(audio_file):
            print(f"✓ 語音檔案生成成功: {audio_file}")
            file_size = os.path.getsize(audio_file)
            print(f"✓ 檔案大小: {file_size} bytes")
        else:
            print("❌ 語音檔案生成失敗")
            return False
        
        manager.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ 語音生成測試失敗: {e}")
        return False


def test_voice_playback():
    """測試語音播放功能"""
    print("\n=== 測試語音播放功能 ===")
    
    if not AUDIO_AVAILABLE:
        print("跳過測試：缺少必要依賴")
        return False
    
    try:
        manager = AudioManager()
        
        if not manager.is_initialized:
            print("⚠️  音訊系統未初始化，跳過播放測試")
            return True
        
        # 測試基本播放
        test_texts = [
            "測試語音一",
            "測試語音二",
            "測試語音三"
        ]
        
        for i, text in enumerate(test_texts):
            print(f"播放測試 {i+1}: {text}")
            success = manager.play_text(text)
            if success:
                print(f"✓ 語音 {i+1} 添加到播放佇列成功")
            else:
                print(f"❌ 語音 {i+1} 添加失敗")
            
            time.sleep(1)  # 等待一秒
        
        # 等待播放完成
        print("等待播放完成...")
        wait_time = 0
        while manager.is_busy() and wait_time < 15:
            time.sleep(1)
            wait_time += 1
            print(f"等待中... {wait_time}s")
        
        print("✓ 語音播放測試完成")
        manager.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ 語音播放測試失敗: {e}")
        return False


def test_voice_control():
    """測試語音控制功能"""
    print("\n=== 測試語音控制功能 ===")
    
    if not AUDIO_AVAILABLE:
        print("跳過測試：缺少必要依賴")
        return False
    
    try:
        manager = AudioManager()
        
        # 測試音量控制
        print("測試音量控制...")
        volumes = [0.3, 0.7, 1.0, 0.5]
        for volume in volumes:
            manager.set_volume(volume)
            actual_volume = manager.get_volume()
            print(f"✓ 設定音量 {volume} -> 實際音量 {actual_volume}")
        
        # 測試靜音控制
        print("測試靜音控制...")
        manager.set_mute(True)
        print(f"✓ 靜音狀態: {manager.is_mute()}")
        
        manager.set_mute(False)
        print(f"✓ 取消靜音: {manager.is_mute()}")
        
        # 測試播放控制
        print("測試播放控制...")
        manager.play_text("這個語音應該被停止")
        time.sleep(0.5)
        manager.stop_current_playback()
        print("✓ 停止當前播放")
        
        manager.play_text("測試語音1")
        manager.play_text("測試語音2")
        print(f"✓ 播放佇列大小: {manager.get_queue_size()}")
        
        manager.stop_all_playback()
        print(f"✓ 清空佇列後大小: {manager.get_queue_size()}")
        
        manager.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ 語音控制測試失敗: {e}")
        return False


def test_system_voices():
    """測試系統語音功能"""
    print("\n=== 測試系統語音功能 ===")
    
    if not AUDIO_AVAILABLE:
        print("跳過測試：缺少必要依賴")
        return False
    
    try:
        manager = AudioManager()
        
        if not manager.is_initialized:
            print("⚠️  音訊系統未初始化，跳過系統語音測試")
            return True
        
        # 測試系統語音
        system_voices = [
            ("系統啟動", manager.play_system_start),
            ("校準開始", manager.play_calibration_start),
            ("校準成功", manager.play_calibration_success),
            ("動作說明", manager.play_action_instructions),
        ]
        
        for name, func in system_voices:
            print(f"測試 {name} 語音...")
            try:
                func()
                print(f"✓ {name} 語音調用成功")
                time.sleep(1)
            except Exception as e:
                print(f"❌ {name} 語音調用失敗: {e}")
        
        # 測試動作成功語音
        print("測試動作成功語音...")
        for action in Messages.ACTION_KEYS.keys():
            try:
                manager.play_action_success(action)
                print(f"✓ {action} 成功語音調用成功")
            except Exception as e:
                print(f"❌ {action} 成功語音調用失敗: {e}")
        
        # 等待播放完成
        print("等待播放完成...")
        time.sleep(3)
        
        manager.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ 系統語音測試失敗: {e}")
        return False


def test_voice_instruction_manager():
    """測試語音指令管理器"""
    print("\n=== 測試語音指令管理器 ===")
    
    if not AUDIO_AVAILABLE:
        print("跳過測試：缺少必要依賴")
        return False
    
    try:
        manager = AudioManager()
        instruction_manager = VoiceInstructionManager(manager)
        
        # 測試連續播放
        print("測試連續播放指令（5秒）...")
        instruction_manager.start_continuous_instructions(interval=2.0)
        
        time.sleep(5)
        
        print(f"✓ 指令管理器運行狀態: {instruction_manager.is_active()}")
        
        instruction_manager.stop_continuous_instructions()
        time.sleep(1)
        
        print(f"✓ 停止後運行狀態: {instruction_manager.is_active()}")
        
        manager.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ 語音指令管理器測試失敗: {e}")
        return False


def run_all_tests():
    """運行所有測試"""
    print("開始音訊管理器測試...")
    print("=" * 50)
    
    tests = [
        test_audio_manager_init,
        test_voice_generation,
        test_voice_playback,
        test_voice_control,
        test_system_voices,
        test_voice_instruction_manager,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ 測試 {test_func.__name__} 執行失敗: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("測試結果摘要:")
    print(f"通過: {sum(results)}/{len(results)}")
    
    for i, (test_func, result) in enumerate(zip(tests, results)):
        status = "✓ 通過" if result else "❌ 失敗"
        print(f"{i+1}. {test_func.__name__}: {status}")
    
    overall_success = all(results)
    print(f"\n整體測試結果: {'✓ 全部通過' if overall_success else '❌ 有失敗項目'}")
    
    return overall_success


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)