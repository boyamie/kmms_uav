import base64
from openai import OpenAI
from src.config import OPENAI_API_KEY, SYSTEM_PROMPT

client = OpenAI(api_key=OPENAI_API_KEY)

def encode_image_frame(frame):
    """OpenCV 프레임을 Base64로 인코딩"""
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')

def get_vlm_analysis(base64_image):
    """VLM(GPT-4o)을 호출하여 전방 장면 분석 (T_s) """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "이 드론의 전방 카메라에 보이는 것을 설명해. 특히 바닥에 '파란색 천(blue tarp)'이나 '단색 표면'이 보이는지 알려줘."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
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

def get_llm_decision(vlm_text, vps_text):
    """LLM을 호출하여 두 정보를 융합하고 최종 결정 (A_t) """
    try:
        user_prompt = f"""
       : "{vlm_text}"
       : "{vps_text}"
        
        [현재 임무]: "복도를 따라 안전하게 전진하라."
        
        [안전 규칙 상기]: '파란색 천'은 VPS 고장을 유발하는가?
        
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