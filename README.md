# 姿勢檢測動作辨識系統

一個使用MediaPipe技術的即時姿勢檢測系統，能根據使用者的身體動作觸發鍵盤按鍵輸出，並提供語音提示和GUI界面。

## 系統特色

### 🎯 動作辨識功能
- **7種動作檢測**：舉起左手/右手、抬起左腳/右腳、向左/右轉身、點頭
- **即時檢測**：基於MediaPipe的高效姿勢檢測
- **容錯機制**：連續檢測1秒才觸發，避免誤判
- **自動校準**：啟動時自動校準標準站立姿勢

### 🎵 語音系統
- **多語言支援**：使用gTTS進行粵語語音合成
- **語音提示**：系統狀態、動作說明、成功檢測等語音反饋
- **語音控制**：可開啟/關閉語音模式，調節音量
- **循環播放**：可設定定時播放動作說明

### 🖥️ 圖形界面
- **直觀操作**：使用Tkinter製作的友好GUI界面
- **即時顯示**：攝影機畫面、骨骼檢測、系統狀態
- **動作控制**：每個動作可單獨開啟/關閉
- **大尺寸顯示**：按鍵輸出的大字符顯示

## 動作-按鍵對應表

| 動作 | 按鍵 | 說明 |
|------|------|------|
| 舉起左手 | A | 左手腕高於肩膀 |
| 舉起右手 | B | 右手腕高於肩膀 |
| 舉起左腳 | C | 左腳踝明顯抬高 |
| 舉起右腳 | D | 右腳踝明顯抬高 |
| 向左轉身 | E | 身體向左旋轉 |
| 向右轉身 | F | 身體向右旋轉 |
| 點點頭 | G | 頭部上下移動 |

## 系統需求

### 硬體需求
- **攝影機**：USB網路攝影機或筆記本內建攝影機
- **音訊設備**：喇叭或耳機（語音輸出）
- **處理器**：支援即時視頻處理的CPU
- **記憶體**：建議4GB以上RAM

### 軟體需求
- **作業系統**：Windows 11、Raspberry Pi OS、或其他Linux發行版
- **Python**：3.8或更高版本（建議3.10+）
- **攝影機驅動**：支援標準USB Video Class (UVC)

## 安裝與使用

### 方法一：使用打包版本（推薦用戶）
1. 從Release頁面下載最新的打包版本
2. 解壓縮後雙擊 `姿勢檢測系統.exe` 即可運行

### 方法二：源碼運行（推薦開發者）
1. 確保已安裝Python 3.10或更高版本
2. 克隆此倉庫：
   ```bash
   git clone https://github.com/jackylung/pose-detection-system.git
   cd pose-detection-system
   ```
3. 安裝依賴：
   ```bash
   pip install -r requirements.txt
   ```
4. 運行系統：
   ```bash
   python main.py
   ```

## 專案結構

本倉庫包含姿勢檢測系統的核心文件：
- 主程序：[main.py](file://c:\Users\JackyCheung\qoder_projects\pose_detection\main.py)
- 姿勢檢測模組：[pose_detector.py](file://c:\Users\JackyCheung\qoder_projects\pose_detection\pose_detector.py)
- GUI界面：[gui_app.py](file://c:\Users\JackyCheung\qoder_projects\pose_detection\gui_app.py)
- 語音管理：[audio_manager.py](file://c:\Users\JackyCheung\qoder_projects\pose_detection\audio_manager.py) 等
- 配置文件：[messages.py](file://c:\Users\JackyCheung\qoder_projects\pose_detection\messages.py)
- 工具函數：[utils.py](file://c:\Users\JackyCheung\qoder_projects\pose_detection\utils.py)
- 音頻文件：`sounds/` 目錄
- 依賴列表：[requirements.txt](file://c:\Users\JackyCheung\qoder_projects\pose_detection\requirements.txt)
- 打包工具：[build.bat](file://c:\Users\JackyCheung\qoder_projects\pose_detection\build.bat) 和 [build_executable.py](file://c:\Users\JackyCheung\qoder_projects\pose_detection\build_executable.py)

注意：為了保持倉庫的簡潔性，測試文件已被移除。如需完整的測試套件，請聯繫開發者。

## 開發與貢獻

歡迎提交Issue和Pull Request來改善此項目。

## 授權

本項目採用MIT授權。