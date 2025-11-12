import cv2
import time
import base64
from openai import OpenAI
from djitellopy import Tello

# --- 1. 설정 (Configuration) ---
OPENAI_API_KEY = "여기에_자신의_OpenAI_API_키를_입력하세요"
client = OpenAI(api_key=OPENAI_API_KEY)

# LLM이 중재를 위해 사용할 시스템 프롬프트 (논문의 핵심 로직)
SYSTEM_PROMPT = """
당신은 Tello 드론의 자율 비행을 제어하는 AI 두뇌입니다.
당신은 두 가지 정보를 받습니다: [VLM 시각 분석]과.

**[매우 중요한 안전 규칙]**
Tello 드론의 하방 비전 포지셔닝 시스템(VPS)은 '단색 표면' (예: 파란색 천, 완전한 흰색 바닥)이나 '반사 표면' 위에서 패턴을 인식하지 못해 심각한 오류를 일으킵니다. 
이 경우, 드론은 '자세 모드(ATTI mode)'로 전환되어 통제 불가능하게 표류(drift)할 수 있습니다. 

**[당신의 임무]**
VLM이 시각적으로 "파란색 천"이나 "단색 바닥"을 감지하면, 이는 '물리적 함정'입니다.
즉시 비행을 중단하고 위험을 회피해야 합니다. 

**[명령 형식]**
당신의 결정은 다음 4가지 중 하나여야 합니다:
'FORWARD' (경로 안전, 전진)
'STOP' (경로 위험, 즉시 정지)
'BACKWARD' (위험 회피, 후진)
'LAND' (착륙)
"""

# --- 2. VLM/LLM 헬퍼 함수 ---

def encode_image_frame(frame):
    """OpenCV 프레임을 Base64로 인코딩"""
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')

def get_vlm_analysis(base64_image):
    """VLM(GPT-4o)을 호출하여 전방 장면 분석 (Ts)"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "이 드론의 전방 카메라에 보이는 것을 설명해. 특히 바닥에 '파란색 천'이나 '단색 표면'이 보이는지 알려줘."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=100
        )
        return response.choices.message.content
    except Exception as e:
        print(f"VLM API 오류: {e}")
        return "VLM 분석 실패"

def get_vps_state(tello):
    """VPS 관련 센서 데이터 읽기 (Tv)"""
    try:
        # Tello의 하방 적외선 센서(TOF)는 0.3m ~ 10m 범위에서 작동 
        tof_distance = tello.get_distance_tof() # cm 단위 
        height = tello.get_height() # cm 단위 
        return f"현재 TOF(하방) 고도: {tof_distance}cm, 기압계 고도: {height}cm"
    except Exception:
        return "센서 데이터 읽기 실패"

def get_llm_decision(vlm_text, vps_text):
    """LLM을 호출하여 두 정보를 융합하고 최종 결정 (At)"""
    try:
        user_prompt = f"""
       : "{vlm_text}"
       : "{vps_text}"
        
        [현재 임무]: "복도를 따라 안전하게 전진하라."
        
        [안전 규칙 상기]: '파란색 천'이나 '단색 표면'은 VPS 고장을 유발하는가?
        
        [결론]: 위의 모든 정보를 바탕으로 다음 행동 명령을 하나만 선택하라:
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=,
            max_tokens=10
        )
        decision = response.choices.message.content.upper().strip()
        
        # 유효한 명령인지 확인
        if "FORWARD" in decision: return "FORWARD"
        if "STOP" in decision: return "STOP"
        if "BACKWARD" in decision: return "BACKWARD"
        if "LAND" in decision: return "LAND"
        
        return "STOP" # 기본 안전값
        
    except Exception as e:
        print(f"LLM API 오류: {e}")
        return "STOP" # 오류 발생 시 안전하게 정지

# --- 3. 메인 비행 로직 ---

def main():
    tello = Tello()
    
    try:
        tello.connect()
        print(f"배터리: {tello.get_battery()}%")
        
        tello.streamon()
        frame_read = tello.get_frame_read()
        
        print("이륙합니다!")
        tello.takeoff()
        time.sleep(2) # 안정화 대기
        
        # 3초마다 한 번씩 VLM/LLM 판단 수행 (API 지연 시간 고려)
        last_decision_time = time.time()
        current_command = "STOP" # 초기 상태

        while True:
            img = frame_read.frame
            display_img = cv2.resize(img, (720, 480))
            
            current_time = time.time()
            
            # 3초마다 의사결정 갱신
            if current_time - last_decision_time > 3:
                print("--- AI 의사결정 시작 ---")
                
                # 1. 이미지 인코딩
                b64_img = encode_image_frame(img)
                
                # 2. VLM (시각) 분석
                vlm_text = get_vlm_analysis(b64_img)
                print(f"[VLM 분석]: {vlm_text}")
                
                # 3. VPS (센서) 상태
                vps_text = get_vps_state(tello)
                print(f": {vps_text}")
                
                # 4. LLM (융합) 결정
                current_command = get_llm_decision(vlm_text, vps_text)
                print(f"[LLM 결정]: {current_command}")
                
                last_decision_time = current_time

            # LLM의 결정에 따라 드론 제어
            if current_command == "FORWARD":
                tello.send_rc_control(0, 20, 0, 0) # 약한 속도로 전진
            elif current_command == "STOP":
                tello.send_rc_control(0, 0, 0, 0) # 정지
            elif current_command == "BACKWARD":
                tello.send_rc_control(0, -20, 0, 0) # 후진
            elif current_command == "LAND":
                break # 루프 탈출 후 착륙

            # 화면에 현재 상태 표시
            cv2.putText(display_img, f"COMMAND: {current_command}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("Tello VLM-VPS Fusion", display_img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"메인 루프 오류: {e}")
    
    finally:
        print("모든 작업을 종료하고 착륙합니다.")
        tello.land()
        tello.streamoff()
        tello.end()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()