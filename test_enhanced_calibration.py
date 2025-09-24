"""
測試增強校準功能
測試新的校準語音提示和距離檢測功能
"""

import time
from audio_manager_cantonese_fixed import CantoneseAudioManagerFixed
from messages import Messages

def test_enhanced_calibration_features():
    """測試增強的校準功能"""
    print("測試增強校準功能...")
    print("=" * 60)
    
    # 創建音訊管理器
    audio_manager = CantoneseAudioManagerFixed()
    
    print(f"音訊管理器初始化: {'✅' if audio_manager.is_initialized else '❌'}")
    print(f"使用本地語音: {'✅' if audio_manager.use_local_voice else '❌'}")
    
    # 測試新的校準語音提示
    print("\n1. 測試校準指導語音...")
    print(f"播放: {Messages.CALIBRATION_INSTRUCTION}")
    success1 = audio_manager.speak(Messages.CALIBRATION_INSTRUCTION)
    print(f"結果: {'✅ 成功' if success1 else '❌ 失敗'}")
    time.sleep(4)
    
    print("\n2. 測試距離提示語音...")
    
    # 測試距離太近提示
    print(f"播放: {Messages.DISTANCE_TOO_CLOSE}")
    success2 = audio_manager.speak(Messages.DISTANCE_TOO_CLOSE)
    print(f"距離太近提示: {'✅ 成功' if success2 else '❌ 失敗'}")
    time.sleep(4)
    
    # 測試距離太遠提示
    print(f"播放: {Messages.DISTANCE_TOO_FAR}")
    success3 = audio_manager.speak(Messages.DISTANCE_TOO_FAR)
    print(f"距離太遠提示: {'✅ 成功' if success3 else '❌ 失敗'}")
    time.sleep(4)
    
    # 測試身體不完整提示
    print(f"播放: {Messages.BODY_NOT_COMPLETE}")
    success4 = audio_manager.speak(Messages.BODY_NOT_COMPLETE)
    print(f"身體不完整提示: {'✅ 成功' if success4 else '❌ 失敗'}")
    time.sleep(4)
    
    print("\n3. 測試校準成功語音...")
    print(f"播放: {Messages.CALIBRATION_SUCCESS}")
    success5 = audio_manager.speak(Messages.CALIBRATION_SUCCESS)
    print(f"校準成功語音: {'✅ 成功' if success5 else '❌ 失敗'}")
    time.sleep(3)
    
    # 統計結果
    total_tests = 5
    successful_tests = sum([1 for result in [success1, success2, success3, success4, success5] if result])
    
    print(f"\n📊 測試結果統計:")
    print(f"總測試數: {total_tests}")
    print(f"成功數: {successful_tests}")
    print(f"成功率: {successful_tests/total_tests*100:.1f}%")
    
    if successful_tests == total_tests:
        print("\n🎉 所有校準語音測試通過！增強校準功能正常運作！")
    else:
        print(f"\n⚠️  {total_tests - successful_tests} 個測試失敗，需要檢查")
    
    # 清理
    audio_manager.cleanup()
    
    return successful_tests == total_tests

def test_calibration_workflow_simulation():
    """模擬完整的校準工作流程"""
    print("\n" + "=" * 60)
    print("模擬完整校準工作流程")
    print("=" * 60)
    
    audio_manager = CantoneseAudioManagerFixed()
    
    # 模擬校準開始
    print("\n步驟 1: 用戶按下校準按鈕")
    print("播放校準指導語音...")
    audio_manager.speak(Messages.CALIBRATION_INSTRUCTION)
    time.sleep(5)
    
    # 模擬距離檢測問題
    print("\n步驟 2: 檢測到用戶距離太近")
    print("播放距離太近提示...")
    audio_manager.speak(Messages.DISTANCE_TOO_CLOSE)
    time.sleep(4)
    
    # 模擬用戶調整後距離適中
    print("\n步驟 3: 用戶調整距離後，開始正式校準")
    print("等待校準過程...")
    time.sleep(2)
    
    # 模擬校準完成
    print("\n步驟 4: 校準完成")
    print("播放校準成功語音...")
    audio_manager.speak(Messages.CALIBRATION_SUCCESS)
    time.sleep(3)
    
    print("\n✅ 校準工作流程模擬完成！")
    
    audio_manager.cleanup()

if __name__ == "__main__":
    # 測試增強校準功能
    test_result = test_enhanced_calibration_features()
    
    if test_result:
        # 如果基本測試通過，進行工作流程模擬
        test_calibration_workflow_simulation()
    
    print("\n🏁 所有測試完成！")