import cv2
import numpy as np
from src.config import SYSTEM_PROMPT 

BLUE_LOWER = np.array()
BLUE_UPPER = np.array()

def get_vlm_analysis_local(frame):
    try:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, BLUE_LOWER, BLUE_UPPER)

        blue_pixel_count = cv2.countNonZero(mask)

        total_pixels = frame.shape * frame.shape[1]
        blue_ratio = (blue_pixel_count / total_pixels) * 100

        if blue_ratio > 10:
            print(f"[VLM Local] 파란색 감지 (비율: {blue_ratio:.2f}%)")
            return "VLM ($T_s$): '파란색 천(blue tarp)'이 감지됨." # 
        else:
            return "VLM ($T_s$): 경로 깨끗함. (파란색 천 없음)"
            
    except Exception as e:
        print(f" VLM(OpenCV) 오류: {e}")
        return "VLM ($T_s$): 분석 실패"

def get_llm_decision_local(vlm_text, vps_text):

    is_blue_tarp_detected = "파란색 천" in vlm_text

    is_vps_unstable = "WARNING" in vps_text or "FAILED" in vps_text

    if is_blue_tarp_detected:
        print("[LLM Local] 결정: VLM이 '파란색 천' 감지! -> STOP")
        return "STOP"
        
    if is_vps_unstable:
        print("[LLM Local] 결정: VPS 센서 불안정! -> STOP")
        return "STOP"
        
    print("[LLM Local] 결정: 모든 시스템 정상. -> FORWARD")
    return "FORWARD"

# --- 아래 함수는 인터넷 연결 시에 사용 ---
def encode_image_frame(frame):
    """OpenCV 프레임을 Base64로 인코딩"""
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')