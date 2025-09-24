"""
使用 pyttsx3 測試本地語音引擎
檢查系統是否有粵語語音包
"""

import pyttsx3
import time

def test_local_voices():
    """測試系統本地語音引擎"""
    print("測試本地語音引擎...")
    print("=" * 50)
    
    try:
        # 初始化 pyttsx3
        engine = pyttsx3.init()
        
        # 獲取所有可用的語音
        voices = engine.getProperty('voices')
        
        print(f"找到 {len(voices)} 個語音引擎：")
        
        cantonese_voices = []
        chinese_voices = []
        
        for i, voice in enumerate(voices):
            print(f"\\n語音 {i+1}:")
            print(f"  ID: {voice.id}")
            print(f"  名稱: {voice.name}")
            print(f"  語言: {voice.languages}")
            
            # 檢查是否為中文或粵語相關
            voice_info = f"{voice.name} {voice.id}".lower()
            if any(keyword in voice_info for keyword in ['hong kong', 'cantonese', 'hk', '粵', '廣東']):
                cantonese_voices.append((i, voice))
                print("  *** 可能的粵語語音 ***")
            elif any(keyword in voice_info for keyword in ['chinese', 'zh', '中文', 'mandarin']):
                chinese_voices.append((i, voice))
                print("  *** 中文語音 ***")
        
        # 測試語音
        test_text = "你好，我係測試粵語語音合成"
        
        if cantonese_voices:
            print(f"\\n找到 {len(cantonese_voices)} 個可能的粵語語音，開始測試：")
            for i, (voice_idx, voice) in enumerate(cantonese_voices):
                print(f"\\n測試粵語語音 {i+1}: {voice.name}")
                test_voice(engine, voice.id, test_text)
                input("按 Enter 繼續...")
        
        if chinese_voices:
            print(f"\\n找到 {len(chinese_voices)} 個中文語音，開始測試：")
            for i, (voice_idx, voice) in enumerate(chinese_voices):
                print(f"\\n測試中文語音 {i+1}: {voice.name}")
                test_voice(engine, voice.id, test_text)
                input("按 Enter 繼續...")
        
        if not cantonese_voices and not chinese_voices:
            print("\\n未找到中文或粵語語音包")
            print("建議安裝 Windows 語音包或使用線上服務")
        
        return cantonese_voices, chinese_voices
        
    except Exception as e:
        print(f"錯誤: {e}")
        return [], []

def test_voice(engine, voice_id, text):
    """測試指定的語音"""
    try:
        engine.setProperty('voice', voice_id)
        engine.setProperty('rate', 150)  # 語速
        engine.setProperty('volume', 0.8)  # 音量
        
        print(f"正在播放: {text}")
        engine.say(text)
        engine.runAndWait()
        
    except Exception as e:
        print(f"播放失敗: {e}")

def main():
    """主函數"""
    print("本地語音引擎測試程序")
    print("檢查系統是否有粵語語音包")
    print("=" * 50)
    
    cantonese_voices, chinese_voices = test_local_voices()
    
    print("\\n" + "=" * 50)
    print("測試總結:")
    
    if cantonese_voices:
        print(f"✅ 找到 {len(cantonese_voices)} 個可能的粵語語音")
        print("建議使用這些語音進行粵語合成")
    else:
        print("❌ 未找到粵語語音包")
    
    if chinese_voices:
        print(f"✅ 找到 {len(chinese_voices)} 個中文語音")
    
    print("\\n建議：")
    if not cantonese_voices:
        print("1. 安裝 Windows 粵語語音包")
        print("2. 使用 Azure Cognitive Services")
        print("3. 使用線上粵語TTS服務")
        print("4. 錄製本地粵語音檔")
    else:
        print("1. 使用找到的本地粵語語音")
        print("2. 調整語速和音調以獲得更好效果")

if __name__ == "__main__":
    # 先安裝 pyttsx3
    try:
        import pyttsx3
        main()
    except ImportError:
        print("需要安裝 pyttsx3 庫")
        print("請執行: pip install pyttsx3")
        
        # 嘗試安裝
        import subprocess
        import sys
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyttsx3"])
            import pyttsx3
            print("pyttsx3 安裝成功！重新啟動測試...")
            main()
        except Exception as e:
            print(f"安裝失敗: {e}")