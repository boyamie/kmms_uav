import cv2
import time
from src.tello_controller import TelloController
from src.vps_monitor import get_vps_state_text
from src.ai_gateway import get_vlm_analysis, get_llm_decision, encode_image_frame
from src.config import OPENAI_API_KEY # (사용되진 않지만 로드 확인용)

# AI 의사결정 주기 (초)
DECISION_INTERVAL = 3

def main():
    tello = TelloController()
    
    try:
        tello.connect()
        print(f"배터리: {tello.get_battery()}%")
        
        tello.streamon() [1]
        frame_read = tello.get_frame_read() [1]
        
        print("이륙합니다! (3초 후)")
        tello.takeoff() [1, 1]
        time.sleep(3) # 안정화 대기
        
        last_decision_time = time.time()
        current_command = "STOP" # 초기 상태

        while True:
            img = frame_read.frame
            display_img = cv2.resize(img, (720, 480)) [1]
            
            current_time = time.time()
            
            # 3초마다 AI 의사결정 갱신
            if current_time - last_decision_time > DECISION_INTERVAL:
                print("\n--- AI 의사결정 시작 ---")
                
                # 1. 이미지 인코딩
                b64_img = encode_image_frame(img)
                
                # 2. VLM (시각) 분석 (T_s) 
                vlm_text = get_vlm_analysis(b64_img)
                print(f"[VLM 분석]: {vlm_text}")
                
                # 3. VPS (센서) 상태 (T_v) 
                vps_text = get_vps_state_text(tello.drone) # djitellopy 객체 직접 전달
                print(f": {vps_text}")
                
                # 4. LLM (융합) 결정 (A_t) 
                current_command = get_llm_decision(vlm_text, vps_text)
                print(f"[LLM 결정]: {current_command}")
                
                last_decision_time = current_time

            # LLM의 결정에 따라 드론 제어
            tello.execute_command(current_command)

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