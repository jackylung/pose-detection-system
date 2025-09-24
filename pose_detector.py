"""
姿勢檢測模組
使用MediaPipe進行即時姿勢檢測和動作識別
"""

import cv2
import numpy as np
import mediapipe as mp
import math
import time
from typing import Optional, Dict, Tuple, List, Any
from PIL import Image, ImageDraw, ImageFont

from messages import DetectionThresholds, SystemConfig, Messages
from utils import logger, action_buffer, profiler

class PoseDetector:
    """姿勢檢測器類別"""
    
    def __init__(self):
        """初始化姿勢檢測器"""
        # MediaPipe初始化
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # 姿勢檢測模型（優化性能）
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.7,  # 提高閾值減少誤檢
            min_tracking_confidence=0.5,
            model_complexity=0  # 使用最簡單模型提高FPS
        )
        
        # 校準相關
        self.is_calibrated = False
        self.calibration_frames = 0
        self.baseline_pose = None
        
        # 校準成功顯示管理
        self.calibration_success_display_time = 0
        self.calibration_success_display_duration = 3.0  # 顯示3秒
        
        # 動作檢測狀態
        self.current_landmarks = None
        self.previous_landmarks = None
        self.action_history = {}
        
        # 幀計數
        self.frame_count = 0
        
        # 優化：語音提示狀態管理（避免重複播放）
        self.last_voice_prompts = {}
        self.voice_prompt_cooldown = 10.0  # 10秒冷卻時間
        self.last_prompt_time = 0
        
        # 校準會話管理 - 確保每次校準會話只播放一次語音（徹底解決重複播放）
        self.calibration_voice_played = {
            'body_incomplete': False,
            'distance_issue': False,
            'calibration_success': False
        }
        
        # 緩存字體以提高性能
        self.font_cache = None
        self._initialize_font_cache()
        
        logger.info("姿勢檢測器初始化完成")
    
    def _initialize_font_cache(self):
        """初始化字體緩存"""
        try:
            # Windows系統字體
            self.font_cache = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 24)
        except:
            try:
                # 備用字體
                self.font_cache = ImageFont.truetype("arial.ttf", 24)
            except:
                # 使用預設字體
                self.font_cache = ImageFont.load_default()
    
    def _put_chinese_text(self, img, text, position, font_size=24, color=(0, 255, 0)):
        """
        在圖像上繪製中文文字（使用PIL/Pillow實現完整中文支持）
        
        Args:
            img: OpenCV圖像
            text: 要顯示的文字
            position: 文字位置 (x, y)
            font_size: 字體大小
            color: 文字顏色 (B, G, R)
        """
        try:
            # 檢查是否包含中文字符
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
            
            if has_chinese:
                # 使用PIL繪製中文文字
                from PIL import Image, ImageDraw, ImageFont
                import numpy as np
                
                # 轉換OpenCV圖像為PIL圖像
                img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                draw = ImageDraw.Draw(img_pil)
                
                # 設置字體
                try:
                    # 使用系統中文字體
                    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", font_size)
                except:
                    try:
                        font = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", font_size)
                    except:
                        # 使用默認字體
                        font = ImageFont.load_default()
                
                # 轉換顏色格式 (BGR -> RGB)
                pil_color = (color[2], color[1], color[0])
                
                # 繪製文字
                draw.text(position, text, font=font, fill=pil_color)
                
                # 轉換回OpenCV格式
                img_opencv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
                
                # 將結果複製回原圖像
                img[:] = img_opencv
                
            else:
                # 英文字符使用OpenCV直接繪製
                cv2.putText(img, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA)
            
        except Exception as e:
            # 如果PIL方法失敗，使用簡化顯示
            logger.warning(f"中文文字繪製失敗，使用簡化顯示: {e}")
            # 對於中文，顯示英文狀態
            english_mapping = {
                "校準中": "Calibrating",
                "已校準": "Calibrated",
                "校準完成": "Completed",
                "成功檢測到舉起左手": "Left Hand Up",
                "成功檢測到舉起右手": "Right Hand Up",
                "成功檢測到舉起左腳": "Left Foot Up",
                "成功檢測到舉起右腳": "Right Foot Up",
                "檢測到點點頭": "Nod Detected"
            }
            
            display_text = english_mapping.get(text, "Status")
            cv2.putText(img, display_text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
    
    def _draw_center_chinese_text(self, img, text, font_size=48):
        """
        在畫面中心繪製大字體中文文字
        
        Args:
            img: OpenCV圖像
            text: 要顯示的文字
            font_size: 字體大小
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            import numpy as np
            
            height, width = img.shape[:2]
            center_x = width // 2
            center_y = height // 2
            
            # 轉換OpenCV圖像為PIL圖像
            img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_pil)
            
            # 設置大字體
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", font_size)
            except:
                try:
                    font = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # 計算文字尺寸以便居中
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            text_x = center_x - text_width // 2
            text_y = center_y - text_height // 2
            
            # 繪製陰影（黑色）
            draw.text((text_x + 3, text_y + 3), text, font=font, fill=(0, 0, 0))
            # 繪製主文字（綠色）
            draw.text((text_x, text_y), text, font=font, fill=(0, 255, 0))
            
            # 轉換回OpenCV格式
            img_opencv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            
            # 將結果複製回原圖像
            img[:] = img_opencv
            
        except Exception as e:
            # 如果失敗，使用英文显示
            logger.warning(f"中心中文文字繪製失敗: {e}")
            # 使用OpenCV繪製英文
            height, width = img.shape[:2]
            center_x = width // 2
            center_y = height // 2
            
            display_text = "Calibration Success"
            font_scale = 1.5
            thickness = 3
            
            text_size = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
            text_x = center_x - text_size[0] // 2
            text_y = center_y + text_size[1] // 2
            
            # 繪製陰影和主文字
            cv2.putText(img, display_text, (text_x + 2, text_y + 2), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness + 1)
            cv2.putText(img, display_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        處理單一幀圖像
        
        Args:
            frame: 輸入圖像幀
            
        Returns:
            Tuple[np.ndarray, Dict]: 處理後的圖像和檢測結果
        """
        profiler.start_timing('frame_processing')
        
        self.frame_count += 1
        detection_results = {
            'pose_detected': False,
            'landmarks': None,
            'actions': {},
            'calibration_status': self.is_calibrated
        }
        
        # 轉換顏色空間
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 姿勢檢測
        results = self.pose.process(rgb_frame)
        
        if results.pose_landmarks:
            detection_results['pose_detected'] = True
            detection_results['landmarks'] = results.pose_landmarks
            
            # 更新當前landmarks
            self.previous_landmarks = self.current_landmarks
            self.current_landmarks = results.pose_landmarks
            
            # 繪製姿勢骨架
            self.mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
            # 校準檢查
            if not self.is_calibrated:
                calibration_result = self._check_calibration(results.pose_landmarks)
                detection_results['calibration_status'] = calibration_result
            else:
                # 動作檢測
                detected_actions = self._detect_actions(results.pose_landmarks)
                detection_results['actions'] = detected_actions
        
        # 添加狀態信息到圖像
        self._draw_status_info(frame, detection_results)
        
        profiler.end_timing('frame_processing')
        return frame, detection_results
    
    def _check_calibration(self, landmarks) -> Dict[str, Any]:
        """
        檢查姿勢校準（簡化版本 - 使用布林旗標確保每個提示只播放一次）
        
        Args:
            landmarks: 檢測到的關鍵點
            
        Returns:
            Dict: 校準結果包含狀態和提示訊息
        """
        import time
        
        calibration_result = {
            'completed': False,
            'voice_prompt': None,
            'status_message': '校準中...'
        }
        
        # 檢查身體完整性
        body_check = self._check_body_completeness(landmarks)
        if not body_check['complete']:
            # 使用布林旗標管理 - 確保只播放一次
            if not self.calibration_voice_played['body_incomplete']:
                calibration_result['voice_prompt'] = body_check['prompt']
                self.calibration_voice_played['body_incomplete'] = True
                logger.info("設定語音提示 - 身體不完整（只播放一次）")
            
            calibration_result['status_message'] = body_check['message']
            self.calibration_frames = 0
            return calibration_result
        
        # 檢查距離
        distance_check = self._check_distance(landmarks)
        if distance_check['prompt']:
            # 使用布林旗標管理 - 確保只播放一次
            if not self.calibration_voice_played['distance_issue']:
                calibration_result['voice_prompt'] = distance_check['prompt']
                self.calibration_voice_played['distance_issue'] = True
                logger.info("設定語音提示 - 距離問題（只播放一次）")
            
            calibration_result['status_message'] = distance_check['message']
            self.calibration_frames = 0
            return calibration_result
        
        # 檢查姿勢穩定性
        if self._is_standing_pose(landmarks):
            self.calibration_frames += 1
            calibration_result['status_message'] = f"校準中... {self.calibration_frames}/{DetectionThresholds.CALIBRATION_FRAMES} (保持穩定姿勢)"
            
            # 每5幀輸出一次進度日誌
            if self.calibration_frames % 5 == 0:
                logger.info(f"校準進度: {self.calibration_frames}/{DetectionThresholds.CALIBRATION_FRAMES}")
            
            if self.calibration_frames >= DetectionThresholds.CALIBRATION_FRAMES:
                self.baseline_pose = self._extract_pose_features(landmarks)
                self.is_calibrated = True
                calibration_result['completed'] = True
                
                # 校準成功提示只播放一次
                if not self.calibration_voice_played['calibration_success']:
                    calibration_result['voice_prompt'] = Messages.CALIBRATION_SUCCESS_CANTONESE
                    self.calibration_voice_played['calibration_success'] = True
                    logger.info("設定語音提示 - 校準成功（只播放一次）")
                
                calibration_result['status_message'] = '校準完成 - 系統就緒'
                
                # 設定成功顯示時間
                import time
                self.calibration_success_display_time = time.time()
                
                logger.info("姿勢校準完成")
        else:
            # 姿勢不穩定，重置計數器
            if self.calibration_frames > 0:
                logger.debug(f"姿勢不穩定，重置計數器（前進度: {self.calibration_frames}/{DetectionThresholds.CALIBRATION_FRAMES}）")
            self.calibration_frames = 0
            calibration_result['status_message'] = "請保持穩定的站立姿勢"
        
        return calibration_result
    
    def _is_standing_pose(self, landmarks) -> bool:
        """
        檢查是否為標準站立姿勢（增強調試版本）
        
        Args:
            landmarks: 關鍵點
            
        Returns:
            bool: 是否為站立姿勢
        """
        try:
            # 獲取關鍵點
            left_shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_hip = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP]
            
            # 檢查肩膀水平
            shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
            
            # 檢查臀部水平
            hip_diff = abs(left_hip.y - right_hip.y)
            
            # 檢查身體直立
            torso_straight = abs((left_shoulder.x + right_shoulder.x) / 2 - (left_hip.x + right_hip.x) / 2)
            
            # 評估測試
            shoulder_ok = shoulder_diff < DetectionThresholds.STABILITY_THRESHOLD
            hip_ok = hip_diff < DetectionThresholds.STABILITY_THRESHOLD
            torso_ok = torso_straight < DetectionThresholds.STABILITY_THRESHOLD
            
            # 調試信息（每20幀輸出一次）
            if self.frame_count % 20 == 0:
                logger.debug(f"穩定性檢查: 肩膀={shoulder_diff:.4f}({'OK' if shoulder_ok else 'FAIL'}), "
                           f"臀部={hip_diff:.4f}({'OK' if hip_ok else 'FAIL'}), "
                           f"身體={torso_straight:.4f}({'OK' if torso_ok else 'FAIL'}), "
                           f"閾值={DetectionThresholds.STABILITY_THRESHOLD}")
            
            return shoulder_ok and hip_ok and torso_ok
            
        except Exception as e:
            logger.error(f"檢查站立姿勢時發生錯誤: {e}")
            return False
    
    def _extract_pose_features(self, landmarks) -> Dict:
        """
        提取姿勢特徵
        
        Args:
            landmarks: 關鍵點
            
        Returns:
            Dict: 姿勢特徵字典
        """
        features = {}
        
        # 關鍵點位置
        key_points = {
            'left_wrist': landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST],
            'right_wrist': landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST],
            'left_ankle': landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ANKLE],
            'right_ankle': landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ANKLE],
            'left_shoulder': landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER],
            'right_shoulder': landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER],
            'left_knee': landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_KNEE],
            'right_knee': landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_KNEE],
            'nose': landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
        }
        
        for name, point in key_points.items():
            features[name] = {'x': point.x, 'y': point.y, 'z': point.z}
        
        return features

    def _detect_actions(self, landmarks) -> Dict:
        """
        檢測動作（優化版本：每次只檢測一個最可靠的動作）
        
        Args:
            landmarks: 關鍵點
            
        Returns:
            Dict: 檢測到的動作字典
        """
        if not self.baseline_pose:
            return {}
        
        detected_actions = {}
        current_features = self._extract_pose_features(landmarks)
        
        # 先檢測所有基本動作
        actions_detected = {}
        actions_detected['left_hand'] = self._detect_hand_raise(current_features, 'left')
        actions_detected['right_hand'] = self._detect_hand_raise(current_features, 'right')
        actions_detected['left_foot'] = self._detect_foot_raise(current_features, 'left')
        actions_detected['right_foot'] = self._detect_foot_raise(current_features, 'right')
        actions_detected['turn_left_head'] = self._detect_head_turn(current_features, 'left')
        actions_detected['turn_right_head'] = self._detect_head_turn(current_features, 'right')
        
        # 檢測膝蓋動作
        actions_detected['left_knee'] = self._detect_knee_raise(
            current_features, 
            'left',
            actions_detected['left_foot']
        )
        actions_detected['right_knee'] = self._detect_knee_raise(
            current_features, 
            'right',
            actions_detected['right_foot']
        )
        
        # 檢測雙手舉起動作
        actions_detected['both_hands'] = self._detect_both_hands_raise(
            current_features, 
            actions_detected['left_hand'], 
            actions_detected['right_hand']
        )
        
        # 為每個動作計算可靠性分數
        action_scores = {}
        
        # 計算每個動作的可靠性分數
        for action, detected in actions_detected.items():
            if detected:
                # 基於檢測的置信度計算分數
                confidence = self._calculate_action_confidence(action, current_features, actions_detected)
                action_scores[action] = confidence
        
        # 選擇最可靠的動作
        if len(action_scores) > 0:
            # 選擇分數最高的動作
            most_reliable_action = max(action_scores.keys(), key=lambda x: action_scores[x])
            # 只有當分數超過閾值時才觸發動作
            if action_scores[most_reliable_action] > 0.5:
                detected_actions[most_reliable_action] = True
                
                # 對於雙手動作，同時標記單手動作
                if most_reliable_action == 'both_hands':
                    detected_actions['left_hand'] = True
                    detected_actions['right_hand'] = True
        else:
            # 如果沒有檢測到任何動作，確保所有動作都設置為False
            for action in actions_detected.keys():
                detected_actions[action] = False
        
        # 更新動作緩衝區
        for action, detected in detected_actions.items():
            action_buffer.add_detection(action, detected)
        
        return detected_actions
    
    def _calculate_action_confidence(self, action: str, current_features: Dict, all_actions: Dict) -> float:
        """
        計算動作的可靠性分數
        
        Args:
            action: 動作名稱
            current_features: 當前姿勢特徵
            all_actions: 所有動作的檢測結果
            
        Returns:
            float: 可靠性分數 (0.0-1.0)
        """
        # 檢查基準姿勢是否存在
        if not self.baseline_pose:
            return 0.0
            
        if action == 'both_hands':
            # 雙手舉起的可靠性基於左右手舉起的一致性
            if all_actions.get('left_hand', False) and all_actions.get('right_hand', False):
                left_wrist = current_features['left_wrist']
                right_wrist = current_features['right_wrist']
                left_shoulder = current_features['left_shoulder']
                right_shoulder = current_features['right_shoulder']
                
                # 計算雙手相對於肩膀的高度
                left_height = left_shoulder['y'] - left_wrist['y']
                right_height = right_shoulder['y'] - right_wrist['y']
                
                # 計算一致性（高度差異越小，分數越高）
                height_diff = abs(left_height - right_height)
                consistency = max(0.0, 1.0 - height_diff / 0.1)
                
                return min(1.0, consistency + 0.5)  # 基礎分數0.5 + 一致性分數
        
        elif action in ['left_hand', 'right_hand']:
            # 單手舉起的可靠性基於舉起的高度
            side = 'left' if action == 'left_hand' else 'right'
            actual_side = 'right' if side == 'left' else 'left'  # MediaPipe鏡像修正
            
            wrist_key = f'{actual_side}_wrist'
            shoulder_key = f'{actual_side}_shoulder'
            
            if wrist_key in current_features and shoulder_key in current_features:
                wrist = current_features[wrist_key]
                shoulder = current_features[shoulder_key]
                
                # 計算舉起的高度差
                height_diff = shoulder['y'] - wrist['y']
                # 轉換為0-1的分數
                return min(1.0, max(0.0, height_diff / 0.2))
            return 0.0
        
        elif action in ['left_foot', 'right_foot']:
            # 腳部抬起的可靠性基於抬起的高度
            side = 'left' if action == 'left_foot' else 'right'
            actual_side = 'right' if side == 'left' else 'left'  # MediaPipe鏡像修正
            
            ankle_key = f'{actual_side}_ankle'
            
            if ankle_key in current_features and ankle_key in self.baseline_pose:
                ankle = current_features[ankle_key]
                baseline_ankle = self.baseline_pose[ankle_key]
                
                # 計算抬起的高度差
                height_diff = baseline_ankle['y'] - ankle['y']
                # 轉換為0-1的分數
                return min(1.0, max(0.0, height_diff / 0.1))
            return 0.0
        
        elif action in ['left_knee', 'right_knee']:
            # 膝蓋抬起的可靠性基於抬起的高度
            side = 'left' if action == 'left_knee' else 'right'
            actual_side = 'right' if side == 'left' else 'left'  # MediaPipe鏡像修正
            
            knee_key = f'{actual_side}_knee'
            ankle_key = f'{actual_side}_ankle'
            
            if (knee_key in current_features and ankle_key in current_features and 
                knee_key in self.baseline_pose and ankle_key in self.baseline_pose):
                knee = current_features[knee_key]
                ankle = current_features[ankle_key]
                baseline_knee = self.baseline_pose[knee_key]
                baseline_ankle = self.baseline_pose[ankle_key]
                
                # 計算抬起的高度差
                current_height = knee['y'] - ankle['y']
                baseline_height = baseline_knee['y'] - baseline_ankle['y']
                height_diff = baseline_height - current_height
                
                # 轉換為0-1的分數
                return min(1.0, max(0.0, height_diff / 0.05))
            return 0.0
        
        elif action in ['turn_left_head', 'turn_right_head']:
            # 頭部轉動的可靠性基於轉動的角度
            direction = 'left' if action == 'turn_left_head' else 'right'
            
            if 'nose' in current_features and 'nose' in self.baseline_pose:
                nose = current_features['nose']
                baseline_nose = self.baseline_pose['nose']
                
                # 使用肩膀作為參考點來計算頭部轉動
                left_shoulder = current_features['left_shoulder']
                right_shoulder = current_features['right_shoulder']
                shoulder_center_x = (left_shoulder['x'] + right_shoulder['x']) / 2
                
                # 計算鼻子相對於肩膀中心的水平位置變化
                current_nose_relative_x = nose['x'] - shoulder_center_x
                baseline_nose_relative_x = baseline_nose['x'] - shoulder_center_x
                x_diff = abs(current_nose_relative_x - baseline_nose_relative_x)
                
                # 轉換為0-1的分數
                return min(1.0, max(0.0, x_diff / 0.05))
            return 0.0
        
        # 默認分數
        return 0.5 if all_actions.get(action, False) else 0.0
    
    def _detect_both_hands_raise(self, current_features: Dict, left_hand_detected: bool, right_hand_detected: bool) -> bool:
        """
        檢測雙手舉起動作（優化版本）
        
        Args:
            current_features: 當前姿勢特徵
            left_hand_detected: 左手是否檢測到舉起
            right_hand_detected: 右手是否檢測到舉起
            
        Returns:
            bool: 是否檢測到雙手舉起
        """
        if not self.baseline_pose:
            return False
            
        # 只有當左右手都檢測到舉起時，才認為是雙手舉起
        # 這樣可以區分單手和雙手動作
        if not (left_hand_detected and right_hand_detected):
            return False
            
        # 進一步檢查雙手舉起的高度是否相近，以確保是真正的雙手舉起動作
        left_wrist = current_features['left_wrist']
        right_wrist = current_features['right_wrist']
        left_shoulder = current_features['left_shoulder']
        right_shoulder = current_features['right_shoulder']
        
        # 計算雙手相對於肩膀的高度
        left_height = left_shoulder['y'] - left_wrist['y']
        right_height = right_shoulder['y'] - right_wrist['y']
        
        # 檢查雙手高度差異是否在合理範圍內
        height_diff = abs(left_height - right_height)
        
        # 如果雙手高度差異不大，則認為是雙手舉起
        return height_diff < DetectionThresholds.HAND_RAISE_THRESHOLD * 0.5
    
    def _detect_hand_raise(self, current_features: Dict, side: str) -> bool:
        """
        檢測手部舉起動作（修正左右手判斷）
        
        Args:
            current_features: 當前姿勢特徵
            side: 'left' 或 'right'
            
        Returns:
            bool: 是否檢測到手部舉起
        """
        if not self.baseline_pose:
            return False
            
        # 注意：MediaPipe的座標系統是鏡像的，需要修正左右
        # 當用戶舉起左手時，在鏡像中顯示為右手
        actual_side = 'right' if side == 'left' else 'left'
        
        wrist_key = f'{actual_side}_wrist'
        shoulder_key = f'{actual_side}_shoulder'
        
        if wrist_key not in current_features or shoulder_key not in current_features:
            return False
        
        # 當前手腕和肩膀位置
        current_wrist = current_features[wrist_key]
        current_shoulder = current_features[shoulder_key]
        
        # 基準位置
        baseline_wrist = self.baseline_pose[wrist_key]
        baseline_shoulder = self.baseline_pose[shoulder_key]
        
        # 計算手腕相對於肩膀的高度變化
        current_relative_height = current_wrist['y'] - current_shoulder['y']
        baseline_relative_height = baseline_wrist['y'] - baseline_shoulder['y']
        
        height_diff = baseline_relative_height - current_relative_height
        
        return height_diff > DetectionThresholds.HAND_RAISE_THRESHOLD
    
    def _detect_foot_raise(self, current_features: Dict, side: str) -> bool:
        """
        檢測腳部抬起動作（修正左右腳判斷）
        
        Args:
            current_features: 當前姿勢特徵
            side: 'left' 或 'right'
            
        Returns:
            bool: 是否檢測到腳部抬起
        """
        if not self.baseline_pose:
            return False
            
        # 注意：MediaPipe的座標系統是鏡像的，需要修正左右
        # 當用戶抬起左腳時，在鏡像中顯示為右腳
        actual_side = 'right' if side == 'left' else 'left'
        
        ankle_key = f'{actual_side}_ankle'
        
        if ankle_key not in current_features:
            return False
        
        current_ankle = current_features[ankle_key]
        baseline_ankle = self.baseline_pose[ankle_key]
        
        # 計算腳踝高度變化
        height_diff = baseline_ankle['y'] - current_ankle['y']
        
        return height_diff > DetectionThresholds.FOOT_RAISE_THRESHOLD
    
    def _detect_knee_raise(self, current_features: Dict, side: str, foot_detected: bool) -> bool:
        """
        檢測膝蓋抬起動作（優化版本）
        
        Args:
            current_features: 當前姿勢特徵
            side: 'left' 或 'right'
            foot_detected: 對應的腳是否檢測到抬起
            
        Returns:
            bool: 是否檢測到膝蓋抬起
        """
        if not self.baseline_pose:
            return False
            
        # 注意：MediaPipe的座標系統是鏡像的，需要修正左右
        # 當用戶抬起左膝時，在鏡像中顯示為右膝
        actual_side = 'right' if side == 'left' else 'left'
        
        knee_key = f'{actual_side}_knee'
        ankle_key = f'{actual_side}_ankle'
        
        # 檢查關鍵點是否可用
        if knee_key not in current_features or ankle_key not in current_features:
            return False
            
        if knee_key not in self.baseline_pose or ankle_key not in self.baseline_pose:
            return False
        
        # 獲取當前和基準位置
        current_knee = current_features[knee_key]
        current_ankle = current_features[ankle_key]
        baseline_knee = self.baseline_pose[knee_key]
        baseline_ankle = self.baseline_pose[ankle_key]
        
        # 計算膝蓋相對於腳踝的高度變化
        current_knee_height = current_knee['y'] - current_ankle['y']
        baseline_knee_height = baseline_knee['y'] - baseline_ankle['y']
        
        height_diff = baseline_knee_height - current_knee_height
        
        # 使用較小的閾值來檢測膝蓋抬起
        knee_threshold = DetectionThresholds.FOOT_RAISE_THRESHOLD * 0.7
        
        # 如果對應的腳已經抬起，則膝蓋抬起的檢測應該更敏感
        # 因為當腳抬起時，膝蓋通常也會抬起
        if foot_detected:
            knee_threshold *= 0.8
        
        return height_diff > knee_threshold
    
    def _detect_head_turn(self, current_features: Dict, direction: str) -> bool:
        """
        檢測頭部轉動動作
        
        Args:
            current_features: 當前姿勢特徵
            direction: 'left' 或 'right'
            
        Returns:
            bool: 是否檢測到頭部轉動
        """
        if not self.baseline_pose or 'nose' not in current_features:
            return False
        
        current_nose = current_features['nose']
        baseline_nose = self.baseline_pose['nose']
        
        # 使用肩膀作為參考點來檢測頭部轉動
        left_shoulder = current_features['left_shoulder']
        right_shoulder = current_features['right_shoulder']
        shoulder_center_x = (left_shoulder['x'] + right_shoulder['x']) / 2
        
        # 計算鼻子相對於肩膀中心的水平位置變化
        current_nose_relative_x = current_nose['x'] - shoulder_center_x
        baseline_nose_relative_x = baseline_nose['x'] - shoulder_center_x
        
        x_diff = current_nose_relative_x - baseline_nose_relative_x
        
        # 根據方向判斷
        if direction == 'left':
            # 向左轉頭：鼻子向左移動（x值減小）
            return x_diff < -0.02
        else:
            # 向右轉頭：鼻子向右移動（x值增加）
            return x_diff > 0.02
    
    def _detect_nod(self, current_features: Dict) -> bool:
        """
        檢測點頭動作（優化版本）
        
        Args:
            current_features: 當前姿勢特徵
            
        Returns:
            bool: 是否檢測到點頭
        """
        if not self.baseline_pose or 'nose' not in current_features:
            return False
        
        current_nose = current_features['nose']
        baseline_nose = self.baseline_pose['nose']
        
        # 使用多個點來更準確檢測點頭動作
        # 檢測鼻子和耳朵的相對位置變化
        nose_y_diff = baseline_nose['y'] - current_nose['y']
        
        # 添加額外的檢測點（如果可用）
        additional_confidence = 0
        
        # 檢查是否有耳朵關鍵點可用於增強檢測
        if 'left_ear' in current_features and 'left_ear' in self.baseline_pose:
            left_ear_diff = self.baseline_pose['left_ear']['y'] - current_features['left_ear']['y']
            if abs(left_ear_diff - nose_y_diff) < 0.02:  # 耳朵和鼻子同向移動
                additional_confidence += 0.01
        
        if 'right_ear' in current_features and 'right_ear' in self.baseline_pose:
            right_ear_diff = self.baseline_pose['right_ear']['y'] - current_features['right_ear']['y']
            if abs(right_ear_diff - nose_y_diff) < 0.02:  # 耳朵和鼻子同向移動
                additional_confidence += 0.01
        
        # 降低閾值並加入額外信心度
        adjusted_threshold = DetectionThresholds.NOD_THRESHOLD - additional_confidence
        
        # 檢測向下點頭動作（y值增加）
        return nose_y_diff < -adjusted_threshold * 0.6  # 點頭是向下運動
    
    def _draw_status_info(self, frame: np.ndarray, detection_results: Dict):
        """
        在圖像上繪製狀態信息（優化版本）
        
        Args:
            frame: 圖像幀
            detection_results: 檢測結果
        """
        height, width = frame.shape[:2]
        
        # 檢查是否需要在畫面中間顯示“成功校正”
        import time
        current_time = time.time()
        if (self.calibration_success_display_time > 0 and 
            current_time - self.calibration_success_display_time < self.calibration_success_display_duration):
            # 在畫面中間顯示“成功校正”
            # 使用新的中文顯示方法
            self._draw_center_chinese_text(frame, "成功校正", 48)
        
        # 優化：只在必要時繪製狀態信息
        # 繪製校準狀態
        calibration_status = detection_results.get('calibration_status', False)
        if isinstance(calibration_status, dict):
            # 新的校準結果格式
            if not calibration_status['completed']:
                status_text = calibration_status['status_message']
                self._put_chinese_text(frame, status_text, (10, 30), color=(0, 255, 255))
            else:
                self._put_chinese_text(frame, "已校準", (10, 30), color=(0, 255, 0))
        else:
            # 舊的布爾格式（向後兼容）
            if not calibration_status:
                status_text = f"校準中... {self.calibration_frames}/{DetectionThresholds.CALIBRATION_FRAMES}"
                self._put_chinese_text(frame, status_text, (10, 30), color=(0, 255, 255))
            else:
                self._put_chinese_text(frame, "已校準", (10, 30), color=(0, 255, 0))
        
        # 優化：只繪製最近觸發的動作，減少重複繪製
        if detection_results['actions']:
            triggered_count = 0
            y_offset = 70
            for action, detected in detection_results['actions'].items():
                if detected and triggered_count < 2:  # 最多顯示2個動作
                    action_text = Messages.get_success_message(action)
                    self._put_chinese_text(frame, action_text, (10, y_offset), color=(0, 255, 0))
                    y_offset += 35
                    triggered_count += 1
        
        # 繪製幀率信息（使用中文顯示方法，每5幀更新一次）
        if self.frame_count % 5 == 0:
            frame_text = f"幀數: {self.frame_count}"
            # 使用我們的中文顯示方法
            self._put_chinese_text(frame, frame_text, (width - 150, 30), font_size=18, color=(255, 255, 255))
    
    def reset_calibration(self):
        """重置校準"""
        self.is_calibrated = False
        self.calibration_frames = 0
        self.baseline_pose = None
        
        # 重置語音提示狀態，允許重新播放
        self.last_voice_prompts.clear()
        
        # 重置校準語音旗標 - 允許重新校準時播放語音
        for key in self.calibration_voice_played:
            self.calibration_voice_played[key] = False
        
        action_buffer.reset_all()
        logger.info("校準已重置 - 允許重新播放校準語音")
    
    def get_triggered_actions(self) -> List[str]:
        """
        獲取應該觸發的動作列表（優化版本：只返回最可靠的動作）
        
        Returns:
            List[str]: 應該觸發的動作列表
        """
        triggered_actions = []
        
        # 使用動作緩衝區的穩定性檢查
        for action in Messages.ACTION_KEYS.keys():
            if action_buffer.should_trigger_action(action):
                triggered_actions.append(action)
        
        return triggered_actions
    
    def _check_body_completeness(self, landmarks) -> Dict[str, Any]:
        """
        檢查身體完整性（確保全身在鏡頭範圍內）
        
        Args:
            landmarks: 檢測到的關鍵點
            
        Returns:
            Dict: 包含完整性檢查結果和提示訊息
        """
        required_landmarks = [
            self.mp_pose.PoseLandmark.NOSE,
            self.mp_pose.PoseLandmark.LEFT_SHOULDER,
            self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
            self.mp_pose.PoseLandmark.LEFT_HIP,
            self.mp_pose.PoseLandmark.RIGHT_HIP,
            self.mp_pose.PoseLandmark.LEFT_ANKLE,
            self.mp_pose.PoseLandmark.RIGHT_ANKLE,
            self.mp_pose.PoseLandmark.LEFT_WRIST,
            self.mp_pose.PoseLandmark.RIGHT_WRIST
        ]
        
        # 檢查所有關鍵點是否可見且在畫面內
        for landmark_type in required_landmarks:
            landmark = landmarks.landmark[landmark_type]
            
            # 檢查可見度
            if landmark.visibility < 0.5:
                return {
                    'complete': False,
                    'prompt': Messages.BODY_NOT_COMPLETE,
                    'message': '身體部位不完整'
                }
            
            # 檢查是否在畫面範圍內（留有邊距）
            if (landmark.x < 0.05 or landmark.x > 0.95 or 
                landmark.y < 0.05 or landmark.y > 0.95):
                return {
                    'complete': False,
                    'prompt': Messages.BODY_NOT_COMPLETE,
                    'message': '身體超出畫面範圍'
                }
        
        return {
            'complete': True,
            'prompt': None,
            'message': '身體檢測完整'
        }
    
    def _check_distance(self, landmarks) -> Dict[str, Any]:
        """
        檢查用戶與鏡頭的距離
        
        Args:
            landmarks: 檢測到的關鍵點
            
        Returns:
            Dict: 包含距離檢查結果和提示訊息
        """
        # 使用肩膀寬度來估算距離
        left_shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        
        shoulder_width = abs(left_shoulder.x - right_shoulder.x)
        
        # 根據肩膀寬度判斷距離
        # 這些閾值可能需要根據實際情況調整
        if shoulder_width > 0.25:  # 太近
            return {
                'prompt': Messages.DISTANCE_TOO_CLOSE,
                'message': '距離太近'
            }
        elif shoulder_width < 0.12:  # 太遠
            return {
                'prompt': Messages.DISTANCE_TOO_FAR,
                'message': '距離太遠'
            }
        
        return {
            'prompt': None,
            'message': '距離適中'
        }
    
    def cleanup(self):
        """清理資源"""
        if self.pose:
            self.pose.close()
        logger.info("姿勢檢測器已清理")


class CameraManager:
    """攝影機管理器"""
    
    def __init__(self, camera_index: int = SystemConfig.CAMERA_INDEX):
        """
        初始化攝影機管理器
        
        Args:
            camera_index: 攝影機索引
        """
        self.camera_index = camera_index
        self.cap = None
        self.is_opened = False
        
    def open_camera(self) -> bool:
        """
        開啟攝影機
        
        Returns:
            bool: 是否成功開啟
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                logger.error(f"無法開啟攝影機 {self.camera_index}")
                return False
            
            # 設定攝影機參數
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, SystemConfig.CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, SystemConfig.CAMERA_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, SystemConfig.CAMERA_FPS)
            
            self.is_opened = True
            logger.info(f"攝影機 {self.camera_index} 已開啟")
            return True
            
        except Exception as e:
            logger.error(f"開啟攝影機時發生錯誤: {e}")
            return False
    
    def read_frame(self) -> Optional[np.ndarray]:
        """
        讀取一幀圖像
        
        Returns:
            Optional[np.ndarray]: 圖像幀，如果失敗則返回None
        """
        if not self.is_opened or not self.cap:
            return None
        
        ret, frame = self.cap.read()
        if ret:
            # 水平翻轉圖像（鏡像效果）
            frame = cv2.flip(frame, 1)
            return frame
        
        return None
    
    def close_camera(self):
        """關閉攝影機"""
        if self.cap:
            self.cap.release()
            self.is_opened = False
            logger.info("攝影機已關閉")
    
    def get_camera_info(self) -> Dict:
        """獲取攝影機信息"""
        if not self.is_opened or not self.cap:
            return {}
        
        return {
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': int(self.cap.get(cv2.CAP_PROP_FPS))
        }