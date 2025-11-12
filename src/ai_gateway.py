import cv2
import numpy as np
from src.config import SYSTEM_PROMPT # LLM 시뮬레이션을 위해 프롬프트(규칙)는 계속 사용

# --- VLM(OpenCV)을 위한 설정 ---
# 포스터의 '파란색 천' 을 감지하기 위한 HSV 색상 범위
# (H: 90-130, S: 50-255, V: 50-255)가 일반적인 파란색 범위입니다.
BLUE_LOWER = np.array()
BLUE_UPPER = np.array()

def get_vlm_analysis_local(frame):
    """
    [VLM 시뮬레이션] OpenCV를 사용해 '파란색 천'을 감지하고 텍스트(T_s)를 반환합니다.
    인터넷 연결이 필요 없습니다.
    """
    try:
        # 1. 이미지를 BGR에서 HSV 색상 공간으로 변환 
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 2. '파란색' 범위에 해당하는 마스크 생성
        mask = cv2.inRange(hsv, BLUE_LOWER, BLUE_UPPER)
        
        # 3. 마스크에서 '파란색' 영역의 픽셀 수 계산
        blue_pixel_count = cv2.countNonZero(mask)
        
        # 4. 이미지 전체 픽셀 대비 파란색 픽셀의 비율 계산
        total_pixels = frame.shape * frame.shape[1]
        blue_ratio = (blue_pixel_count / total_pixels) * 100
        
        # 5. VLM 텍스트(T_s) 생성
        if blue_ratio > 10: # 임계값: 이미지의 10% 이상이 파란색이면
            print(f"[VLM Local] 파란색 감지 (비율: {blue_ratio:.2f}%)")
            return "VLM ($T_s$): '파란색 천(blue tarp)'이 감지됨." # 
        else:
            return "VLM ($T_s$): 경로 깨끗함. (파란색 천 없음)"
            
    except Exception as e:
        print(f" VLM(OpenCV) 오류: {e}")
        return "VLM ($T_s$): 분석 실패"

def get_llm_decision_local(vlm_text, vps_text):
    """
    [LLM 시뮬레이션] Python 'if'문을 사용해 안전 규칙을 추론하고 행동(A_t)을 결정합니다.
    SYSTEM_PROMPT의 규칙을 코드로 구현한 것입니다. 
    인터넷 연결이 필요 없습니다.
    """
    
    # 포스터의 핵심 규칙: 
    # 1. VLM이 '파란색 천'을 감지했는가?
    is_blue_tarp_detected = "파란색 천" in vlm_text
    
    # 2. VPS가 불안정한가? (Tello 매뉴얼의 단색/저고도 위험) 
    is_vps_unstable = "WARNING" in vps_text or "FAILED" in vps_text
    
    # 3. LLM의 최종 결정 (A_t)
    if is_blue_tarp_detected:
        # VLM이 '파란색 천'(물리적 함정) 을 감지하면, VPS 상태와 상관없이 즉시 정지/후진
        print("[LLM Local] 결정: VLM이 '파란색 천' 감지! -> STOP")
        return "STOP" # 또는 "BACKWARD"
        
    if is_vps_unstable:
        # VLM은 괜찮다고 했지만, VPS 센서가 위험을 감지하면 정지
        print("[LLM Local] 결정: VPS 센서 불안정! -> STOP")
        return "STOP"
        
    # VLM과 VPS가 모두 안전하다고 판단
    print("[LLM Local] 결정: 모든 시스템 정상. -> FORWARD")
    return "FORWARD"

# --- 아래 함수는 인터넷 연결 시에만 사용 ---
# (참고용으로 남겨둡니다)
def encode_image_frame(frame):
    """OpenCV 프레임을 Base64로 인코딩"""
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')