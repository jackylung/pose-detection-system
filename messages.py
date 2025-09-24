"""
語音提示訊息管理模組
統一管理所有語音提示的文字內容，支援多語言
"""

class Messages:
    """語音訊息類別，集中管理所有語音提示"""
    
    # 系統啟動訊息
    SYSTEM_START = "姿勢檢測系統已啟動"
    CALIBRATION_START = "請站立標準姿勢進行校準"
    CALIBRATION_SUCCESS = "校準完成"
    CALIBRATION_SUCCESS_CANTONESE = "成功校正"  # 新增粵語校準成功訊息
    CALIBRATION_FAILED = "校準失敗，請重新調整姿勢"
    
    # 新增校準指導訊息
    CALIBRATION_INSTRUCTION = "請保持站立姿勢，雙臂自然下垂，面對鏡頭，保持身體放鬆"
    DISTANCE_TOO_CLOSE = "您距離鏡頭太近，請往後退一些，確保全身在鏡頭範圍內"
    DISTANCE_TOO_FAR = "您距離鏡頭太遠，請往前靠近一些"
    BODY_NOT_COMPLETE = "請確保全身都在鏡頭範圍內，包括頭部、手臂和雙腿"
    
    # 動作說明訊息
    ACTION_INSTRUCTIONS = {
        'left_hand': '按鍵"A" -> 舉起左手',
        'right_hand': '按鍵"B" -> 舉起右手', 
        'both_hands': '按鍵"C" -> 舉起雙手',
        'left_foot': '按鍵"D" -> 舉起左腳',
        'left_knee': '按鍵"E" -> 舉起左腳膝頭',
        'right_foot': '按鍵"F" -> 舉起右腳',
        'right_knee': '按鍵"G" -> 舉起右腳膝頭',
        'turn_left_head': '按鍵"1" -> 向左擰頭',
        'turn_right_head': '按鍵"2" -> 向右擰頭'
    }
    
    # 動作成功檢測訊息
    ACTION_SUCCESS = {
        'left_hand': '檢測到舉起左手',
        'right_hand': '檢測到舉起右手',
        'both_hands': '檢測到舉起雙手',
        'left_foot': '檢測到舉起左腳', 
        'left_knee': '檢測到舉起左腳膝頭',
        'right_foot': '檢測到舉起右腳',
        'right_knee': '檢測到舉起右腳膝頭',
        'turn_left_head': '檢測到向左擰頭',
        'turn_right_head': '檢測到向右擰頭'
    }
    
    # 鍵盤對應
    ACTION_KEYS = {
        'left_hand': 'A',
        'right_hand': 'B',
        'both_hands': 'C',
        'left_foot': 'D',
        'left_knee': 'E',
        'right_foot': 'F',
        'right_knee': 'G',
        'turn_left_head': '1',
        'turn_right_head': '2'
    }
    
    # GUI顯示文字
    GUI_TEXTS = {
        'title': "姿勢檢測系統",
        'status': "狀態",
        'calibration': "校準",
        'actions': "支援的動作",
        'voice_mode': "語音模式",
        'mute': "靜音",
        'unmute': "開啟語音",
        'start_system': "啟動系統",
        'stop_system': "停止系統",
        'last_action': "最後動作",
        'key_pressed': "按鍵輸出"
    }
    
    # 系統狀態訊息
    STATUS_MESSAGES = {
        'initializing': "系統初始化中...",
        'calibrating': "姿勢校準中...",
        'ready': "系統就緒",
        'running': "檢測中...",
        'paused': "系統暫停",
        'error': "系統錯誤"
    }
    
    # 錯誤訊息
    ERROR_MESSAGES = {
        'camera_not_found': "找不到攝影機設備",
        'audio_init_failed': "音訊初始化失敗",
        'pose_detection_failed': "姿勢檢測失敗",
        'keyboard_sim_failed': "鍵盤模擬失敗"
    }
    
    @classmethod
    def get_all_instructions(cls):
        """獲取所有動作說明的完整文字"""
        instructions = []
        for action, instruction in cls.ACTION_INSTRUCTIONS.items():
            instructions.append(instruction)
        return "。".join(instructions)
    
    @classmethod
    def get_action_key(cls, action):
        """根據動作名稱獲取對應按鍵"""
        return cls.ACTION_KEYS.get(action, '')
    
    @classmethod
    def get_success_message(cls, action):
        """根據動作名稱獲取成功檢測訊息"""
        return cls.ACTION_SUCCESS.get(action, f"檢測到{action}")


# 動作檢測的閾值參數
class DetectionThresholds:
    """動作檢測閾值參數"""
    
    # 手部動作閾值
    HAND_RAISE_THRESHOLD = 0.15  # 手舉起的最小高度差
    
    # 腳部動作閾值  
    FOOT_RAISE_THRESHOLD = 0.1   # 腳抬起的最小高度差
    
    # 轉身動作閾值
    TURN_ANGLE_THRESHOLD = 30    # 轉身的最小角度（度）
    
    # 點頭動作閾值
    NOD_THRESHOLD = 0.03         # 點頭的最小位移（降低以提高敏感度）
    
    # 動作持續時間閾值（秒）
    ACTION_DURATION = 1.0        # 動作需要持續的時間
    
    # 校準相關闾值
    CALIBRATION_FRAMES = 15      # 校準需要的穩定幀數（減少以便更容易完成）
    STABILITY_THRESHOLD = 0.08   # 姿勢穩定性闾值（放寬以便用戶更容易完成校準）


# 系統配置參數
class SystemConfig:
    """系統配置參數"""
    
    # 攝影機設定
    CAMERA_INDEX = 0             # 預設攝影機索引
    CAMERA_WIDTH = 640           # 攝影機寬度
    CAMERA_HEIGHT = 480          # 攝影機高度
    CAMERA_FPS = 30              # 攝影機幀率
    
    # GUI設定
    GUI_WIDTH = 800              # GUI視窗寬度
    GUI_HEIGHT = 600             # GUI視窗高度
    
    # 語音設定
    TTS_LANGUAGE = 'zh-tw'       # gTTS語言設定（繁體中文/廣東話）
    TTS_SLOW = False             # TTS語速
    
    # 日誌設定
    LOG_LEVEL = "INFO"           # 日誌級別
    LOG_FILE = "pose_detection.log"  # 日誌檔案名
    
    # 音訊檔案設定
    SOUND_DIR = "sounds"         # 音訊檔案目錄
    SOUND_FORMAT = "mp3"         # 音訊格式