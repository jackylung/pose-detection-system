"""
全面測試粵語音訊系統
測試所有語音功能並驗證修復效果
"""

import os
import sys
import time
import threading
from typing import List

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_manager_cantonese import CantoneseAudioManager
from messages import Messages
from utils import logger, LoggerSetup


class AudioTestSuite:
    """音訊測試套件"""
    
    def __init__(self):
        """初始化測試套件"""
        LoggerSetup.setup_logger()
        self.audio_manager = CantoneseAudioManager()
        self.test_results = []
        
    def run_basic_voice_test(self) -> bool:
        """基本語音測試"""
        print("\n" + "="*60)
        print("🎵 基本語音測試")
        print("="*60)
        
        test_messages = [
            "你好，呢個係粵語語音測試",
            "姿勢檢測系統已啟動",  
            "請站立標準姿勢進行校準",
            "校準成功，可以開始檢測",
            "檢測完成"
        ]
        
        success_count = 0
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n📢 測試 {i}/5: {message}")
            
            start_time = time.time()
            success = self.audio_manager.speak(message)
            end_time = time.time()
            
            if success:
                print(f"   ✅ 播放成功 ({end_time - start_time:.2f}秒)")
                success_count += 1
            else:
                print(f"   ❌ 播放失敗")
            
            # 等待播放完成
            time.sleep(3)
        
        success_rate = success_count / len(test_messages) * 100
        print(f"\n📊 基本語音測試結果: {success_count}/{len(test_messages)} ({success_rate:.1f}%)")
        
        self.test_results.append(("基本語音測試", success_rate))
        return success_rate >= 80
    
    def run_system_message_test(self) -> bool:
        """系統訊息語音測試"""
        print("\n" + "="*60)
        print("🔧 系統訊息語音測試")
        print("="*60)
        
        system_tests = [
            ("系統啟動", lambda: self.audio_manager.play_system_start()),
            ("校準開始", lambda: self.audio_manager.play_calibration_start()),
            ("校準成功", lambda: self.audio_manager.play_calibration_success()),
            ("動作說明", lambda: self.audio_manager.play_action_instructions()),
        ]
        
        success_count = 0
        
        for i, (test_name, test_func) in enumerate(system_tests, 1):
            print(f"\n🎯 測試 {i}/4: {test_name}")
            
            try:
                start_time = time.time()
                test_func()
                end_time = time.time()
                
                print(f"   ✅ {test_name}播放成功 ({end_time - start_time:.2f}秒)")
                success_count += 1
            except Exception as e:
                print(f"   ❌ {test_name}播放失敗: {e}")
            
            # 等待播放完成
            time.sleep(3)
        
        success_rate = success_count / len(system_tests) * 100
        print(f"\n📊 系統訊息測試結果: {success_count}/{len(system_tests)} ({success_rate:.1f}%)")
        
        self.test_results.append(("系統訊息測試", success_rate))
        return success_rate >= 80
    
    def run_action_success_test(self) -> bool:
        """動作成功語音測試"""
        print("\n" + "="*60)
        print("🎯 動作成功語音測試")
        print("="*60)
        
        actions = ['left_hand', 'right_hand', 'both_hands', 'jump', 'squat']
        success_count = 0
        
        for i, action in enumerate(actions, 1):
            print(f"\n🏃 測試 {i}/5: {action} 動作成功語音")
            
            try:
                start_time = time.time()
                self.audio_manager.play_action_success(action)
                end_time = time.time()
                
                print(f"   ✅ {action}成功語音播放成功 ({end_time - start_time:.2f}秒)")
                success_count += 1
            except Exception as e:
                print(f"   ❌ {action}成功語音播放失敗: {e}")
            
            # 等待播放完成
            time.sleep(2)
        
        success_rate = success_count / len(actions) * 100
        print(f"\n📊 動作成功語音測試結果: {success_count}/{len(actions)} ({success_rate:.1f}%)")
        
        self.test_results.append(("動作成功語音測試", success_rate))
        return success_rate >= 80
    
    def run_rapid_playback_test(self) -> bool:
        """快速連續播放測試"""
        print("\n" + "="*60)
        print("⚡ 快速連續播放測試")
        print("="*60)
        
        messages = [
            "第一個測試訊息",
            "第二個測試訊息", 
            "第三個測試訊息",
            "第四個測試訊息",
            "第五個測試訊息"
        ]
        
        success_count = 0
        
        print("🚀 開始快速連續播放測試...")
        start_total = time.time()
        
        for i, message in enumerate(messages, 1):
            print(f"   📢 播放 {i}/5: {message}")
            
            start_time = time.time()
            success = self.audio_manager.speak(message)
            end_time = time.time()
            
            if success:
                print(f"     ✅ 成功 ({end_time - start_time:.2f}秒)")
                success_count += 1
            else:
                print(f"     ❌ 失敗")
            
            # 短暫間隔
            time.sleep(1)
        
        end_total = time.time()
        success_rate = success_count / len(messages) * 100
        
        print(f"\n📊 快速連續播放測試結果: {success_count}/{len(messages)} ({success_rate:.1f}%)")
        print(f"⏱️  總耗時: {end_total - start_total:.2f}秒")
        
        self.test_results.append(("快速連續播放測試", success_rate))
        return success_rate >= 80
    
    def run_volume_test(self) -> bool:
        """音量控制測試"""
        print("\n" + "="*60)
        print("🔊 音量控制測試")
        print("="*60)
        
        volume_levels = [0.3, 0.6, 1.0, 0.7]  # 最後回到預設音量
        test_message = "音量測試訊息"
        success_count = 0
        
        for i, volume in enumerate(volume_levels, 1):
            print(f"\n🔊 測試 {i}/4: 音量 {volume}")
            
            try:
                # 設置音量
                self.audio_manager.set_volume(volume)
                time.sleep(0.5)
                
                # 播放測試訊息
                start_time = time.time()
                success = self.audio_manager.speak(test_message)
                end_time = time.time()
                
                if success:
                    print(f"   ✅ 音量 {volume} 播放成功 ({end_time - start_time:.2f}秒)")
                    success_count += 1
                else:
                    print(f"   ❌ 音量 {volume} 播放失敗")
                
                time.sleep(2)
                
            except Exception as e:
                print(f"   ❌ 音量 {volume} 測試失敗: {e}")
        
        success_rate = success_count / len(volume_levels) * 100
        print(f"\n📊 音量控制測試結果: {success_count}/{len(volume_levels)} ({success_rate:.1f}%)")
        
        self.test_results.append(("音量控制測試", success_rate))
        return success_rate >= 80
    
    def run_button_simulation_test(self) -> bool:
        """按鈕模擬測試"""
        print("\n" + "="*60)
        print("🔘 按鈕模擬測試 (模擬GUI按鈕點擊)")
        print("="*60)
        
        button_tests = [
            ("播放動作說明按鈕", lambda: self.audio_manager.play_action_instructions()),
            ("播放系統啟動按鈕", lambda: self.audio_manager.play_system_start()),
            ("播放校準成功按鈕", lambda: self.audio_manager.play_calibration_success()),
        ]
        
        success_count = 0
        
        for i, (button_name, button_func) in enumerate(button_tests, 1):
            print(f"\n🔘 測試 {i}/3: {button_name}")
            
            try:
                print(f"   點擊 {button_name}...")
                start_time = time.time()
                button_func()
                end_time = time.time()
                
                print(f"   ✅ {button_name}響應成功 ({end_time - start_time:.2f}秒)")
                success_count += 1
            except Exception as e:
                print(f"   ❌ {button_name}響應失敗: {e}")
            
            # 等待播放完成
            time.sleep(3)
        
        success_rate = success_count / len(button_tests) * 100
        print(f"\n📊 按鈕模擬測試結果: {success_count}/{len(button_tests)} ({success_rate:.1f}%)")
        
        self.test_results.append(("按鈕模擬測試", success_rate))
        return success_rate >= 80
    
    def run_engine_initialization_test(self) -> bool:
        """引擎初始化測試"""
        print("\n" + "="*60)
        print("🔧 引擎初始化測試")
        print("="*60)
        
        test_results = []
        
        # 測試引擎狀態
        print("🔍 檢查引擎狀態...")
        is_initialized = self.audio_manager.is_initialized
        use_local_voice = self.audio_manager.use_local_voice
        
        print(f"   引擎已初始化: {'✅' if is_initialized else '❌'}")
        print(f"   使用本地語音: {'✅' if use_local_voice else '❌'}")
        print(f"   語音引擎類型: {'本地粵語語音(pyttsx3)' if use_local_voice else 'gTTS語音'}")
        
        test_results.append(is_initialized)
        
        # 測試引擎重新初始化
        if use_local_voice:
            print("\n🔄 測試引擎重新初始化...")
            try:
                reinit_success = self.audio_manager._reinitialize_engine()
                print(f"   引擎重新初始化: {'✅' if reinit_success else '❌'}")
                test_results.append(reinit_success)
                
                # 測試重新初始化後的播放
                print("   測試重新初始化後播放...")
                speak_success = self.audio_manager.speak("重新初始化測試")
                print(f"   重新初始化後播放: {'✅' if speak_success else '❌'}")
                test_results.append(speak_success)
                
                time.sleep(2)
                
            except Exception as e:
                print(f"   ❌ 引擎重新初始化失敗: {e}")
                test_results.append(False)
        
        success_rate = sum(test_results) / len(test_results) * 100
        print(f"\n📊 引擎初始化測試結果: {sum(test_results)}/{len(test_results)} ({success_rate:.1f}%)")
        
        self.test_results.append(("引擎初始化測試", success_rate))
        return success_rate >= 80
    
    def run_comprehensive_test(self):
        """運行全面測試"""
        print("🎪 粵語音訊系統全面測試")
        print("="*80)
        
        start_time = time.time()
        
        # 檢查音訊管理器狀態
        print(f"🎵 音訊管理器狀態:")
        print(f"   初始化狀態: {'✅' if self.audio_manager.is_initialized else '❌'}")
        print(f"   語音類型: {'本地粵語語音' if self.audio_manager.use_local_voice else 'gTTS語音'}")
        print(f"   語音啟用: {'✅' if self.audio_manager.is_voice_enabled() else '❌'}")
        print(f"   當前音量: {self.audio_manager.volume}")
        
        # 運行所有測試
        tests = [
            ("引擎初始化測試", self.run_engine_initialization_test),
            ("基本語音測試", self.run_basic_voice_test),
            ("系統訊息測試", self.run_system_message_test),
            ("動作成功語音測試", self.run_action_success_test),
            ("按鈕模擬測試", self.run_button_simulation_test),
            ("快速連續播放測試", self.run_rapid_playback_test),
            ("音量控制測試", self.run_volume_test),
        ]
        
        passed_tests = 0
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"\n❌ {test_name}執行失敗: {e}")
        
        end_time = time.time()
        
        # 輸出最終結果
        print("\n" + "🏆 測試總結" + "="*70)
        print(f"總測試時間: {end_time - start_time:.2f}秒")
        print(f"通過測試: {passed_tests}/{len(tests)}")
        
        print("\n📋 詳細結果:")
        for test_name, success_rate in self.test_results:
            status = "✅ 通過" if success_rate >= 80 else "❌ 失敗"
            print(f"   {test_name}: {success_rate:.1f}% {status}")
        
        overall_success_rate = passed_tests / len(tests) * 100
        
        if overall_success_rate >= 80:
            print(f"\n🎉 整體測試結果: {overall_success_rate:.1f}% - 系統運行正常!")
        else:
            print(f"\n⚠️  整體測試結果: {overall_success_rate:.1f}% - 系統需要修復!")
        
        return overall_success_rate >= 80
    
    def cleanup(self):
        """清理測試資源"""
        try:
            self.audio_manager.cleanup()
            print("\n🧹 測試資源已清理")
        except Exception as e:
            print(f"\n⚠️  清理資源時出錯: {e}")


def main():
    """主函數"""
    print("🚀 啟動粵語音訊系統全面測試")
    
    test_suite = AudioTestSuite()
    
    try:
        # 運行全面測試
        success = test_suite.run_comprehensive_test()
        
        if success:
            print("\n✨ 所有測試通過，音訊系統運行正常!")
            exit_code = 0
        else:
            print("\n💥 部分測試失敗，請檢查音訊系統配置!")
            exit_code = 1
    
    except KeyboardInterrupt:
        print("\n⏹️  測試被用戶中斷")
        exit_code = 1
    except Exception as e:
        print(f"\n💥 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        exit_code = 1
    finally:
        test_suite.cleanup()
    
    input("\n按 Enter 鍵退出...")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()