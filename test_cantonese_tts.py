"""
粵語（廣東話）語音測試程序
測試不同的語言代碼和TTS服務
"""

import os
import pygame
from gtts import gTTS
import tempfile
import time

def test_tts_language(text, lang_code, description):
    """
    測試指定語言代碼的TTS效果
    
    Args:
        text: 要合成的文字
        lang_code: 語言代碼
        description: 語言描述
    """
    print(f"\n=== 測試 {description} (語言代碼: {lang_code}) ===")
    
    try:
        # 生成語音
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        # 創建臨時檔案
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_filename = temp_file.name
        
        # 保存語音檔案
        tts.save(temp_filename)
        print(f"語音檔案已生成: {temp_filename}")
        
        # 播放語音
        pygame.mixer.init()
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()
        
        print(f"正在播放: {text}")
        print("請仔細聽語音是否為粵語...")
        
        # 等待播放完成
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        # 停止播放並釋放資源
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        time.sleep(0.5)  # 等待資源釋放
        
        # 清理臨時檔案
        try:
            os.unlink(temp_filename)
        except Exception as cleanup_error:
            print(f"清理檔案時出錯（可忽略）: {cleanup_error}")
        
        print("播放完成")
        return True
        
    except Exception as e:
        print(f"錯誤: {e}")
        return False

def main():
    """主測試函數"""
    print("粵語（廣東話）TTS測試程序")
    print("=" * 50)
    
    # 測試文字
    test_text = "你好，我係測試粵語語音合成"
    
    # 測試不同的語言代碼
    test_cases = [
        ("zh", "簡體中文/普通話"),
        ("zh-cn", "簡體中文/普通話"),
        ("zh-tw", "繁體中文/可能係粵語"),
        ("zh-TW", "繁體中文/台灣話"),
        ("yue", "粵語（如果支援）"),
        ("zh-hk", "香港中文（如果支援）"),
        ("zh-HK", "香港中文（如果支援）")
    ]
    
    successful_tests = []
    
    for lang_code, description in test_cases:
        success = test_tts_language(test_text, lang_code, description)
        if success:
            successful_tests.append((lang_code, description))
        
        # 等待用戶確認
        input("\n按 Enter 繼續下一個測試...")
    
    print("\n" + "=" * 50)
    print("測試總結:")
    print(f"成功測試的語言代碼: {len(successful_tests)}")
    
    for lang_code, description in successful_tests:
        print(f"- {lang_code}: {description}")
    
    if successful_tests:
        print("\n請告訴我哪個語言代碼播放的是真正的粵語！")
    else:
        print("\n所有測試都失敗了，可能需要檢查網絡連接或gTTS服務")

if __name__ == "__main__":
    main()