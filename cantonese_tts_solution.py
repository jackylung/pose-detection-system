"""
粵語（廣東話）語音合成解決方案
使用 Azure Cognitive Services 的真正粵語語音
"""

import os
import pygame
import requests
import tempfile
import time
from pathlib import Path

class CantoneseAzureTTS:
    """使用 Azure Cognitive Services 的粵語 TTS"""
    
    def __init__(self, subscription_key=None, region="eastasia"):
        """
        初始化 Azure TTS
        
        Args:
            subscription_key: Azure 訂閱金鑰
            region: Azure 地區
        """
        self.subscription_key = subscription_key
        self.region = region
        self.voice_name = "zh-HK-HiuGaaiNeural"  # Azure 的廣東話女聲
        # 備用聲音: "zh-HK-WanLungNeural" (廣東話男聲)
    
    def speak(self, text):
        """
        合成並播放粵語語音
        
        Args:
            text: 要合成的文字
        """
        if not self.subscription_key:
            print("錯誤：需要 Azure 訂閱金鑰才能使用真正的粵語語音合成")
            print("請到 https://azure.microsoft.com/zh-tw/services/cognitive-services/speech-services/ 申請")
            return False
        
        # 構建 SSML
        ssml = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-HK'>
            <voice name='{self.voice_name}'>
                {text}
            </voice>
        </speak>
        """
        
        # 請求標頭
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3'
        }
        
        # API 端點
        url = f"https://{self.region}.tts.speech.microsoft.com/cognitiveservices/v1"
        
        try:
            # 發送請求
            response = requests.post(url, headers=headers, data=ssml.encode('utf-8'))
            response.raise_for_status()
            
            # 保存音訊檔案
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(response.content)
                temp_filename = temp_file.name
            
            # 播放音訊
            pygame.mixer.init()
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            
            print(f"正在播放粵語語音: {text}")
            
            # 等待播放完成
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            
            # 清理檔案
            os.unlink(temp_filename)
            return True
            
        except Exception as e:
            print(f"Azure TTS 錯誤: {e}")
            return False

class LocalCantoneseWorkaround:
    """本地粵語替代方案（使用預錄音檔或拼音）"""
    
    def __init__(self):
        self.sound_dir = Path("cantonese_sounds")
        self.sound_dir.mkdir(exist_ok=True)
    
    def speak(self, text):
        """
        播放本地粵語音檔或使用替代方案
        
        Args:
            text: 要播放的文字
        """
        # 檢查是否有預錄的粵語音檔
        sound_file = self.sound_dir / f"{hash(text)}.mp3"
        
        if sound_file.exists():
            self._play_sound(str(sound_file))
            return True
        else:
            print(f"未找到預錄音檔: {text}")
            print("建議：")
            print("1. 使用 Azure Cognitive Services")
            print("2. 錄製本地粵語音檔")
            print("3. 使用線上粵語TTS服務")
            return False
    
    def _play_sound(self, filename):
        """播放音檔"""
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
            pygame.mixer.quit()
        except Exception as e:
            print(f"播放錯誤: {e}")

def demonstrate_solutions():
    """演示不同的粵語解決方案"""
    print("粵語語音合成解決方案測試")
    print("=" * 50)
    
    test_text = "你好，我係測試粵語語音合成系統"
    
    print("\\n1. gTTS 限制說明：")
    print("   - gTTS 不支援真正的粵語")
    print("   - zh-tw 只是繁體中文，但仍是普通話發音")
    print("   - zh-hk 同樣不是粵語發音")
    
    print("\\n2. 建議的解決方案：")
    
    # 方案1：Azure TTS (推薦)
    print("\\n方案1：Azure Cognitive Services (推薦)")
    print("- 支援真正的廣東話語音")
    print("- 聲音選項：zh-HK-HiuGaaiNeural (女聲), zh-HK-WanLungNeural (男聲)")
    print("- 需要：Azure 訂閱金鑰")
    
    azure_key = input("\\n請輸入 Azure 訂閱金鑰 (沒有請按 Enter 跳過): ").strip()
    
    if azure_key:
        azure_tts = CantoneseAzureTTS(subscription_key=azure_key)
        print("測試 Azure 粵語語音...")
        success = azure_tts.speak(test_text)
        if success:
            print("✅ Azure 粵語語音測試成功！")
        else:
            print("❌ Azure 粵語語音測試失敗")
    else:
        print("跳過 Azure 測試")
    
    # 方案2：本地音檔
    print("\\n方案2：本地預錄音檔")
    print("- 錄製粵語音檔並保存到 cantonese_sounds/ 目錄")
    print("- 完全離線，但需要手動錄製")
    
    local_tts = LocalCantoneseWorkaround()
    local_tts.speak(test_text)
    
    print("\\n3. 其他替代方案：")
    print("- 使用線上粵語TTS API（如百度、騰訊）")
    print("- 使用 espeak 配合粵語語音包")
    print("- 使用 festival 語音合成系統")
    
    print("\\n結論：如果要真正的粵語語音，建議使用 Azure Cognitive Services")

if __name__ == "__main__":
    demonstrate_solutions()