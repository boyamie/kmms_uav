import cv2
import time
import os
from src.tello_controller import TelloController
from src.vps_monitor import get_vps_state_text
from src.ai_gateway import get_vlm_analysis, get_llm_decision, encode_image_frame

# AI 의사결정 주기 (초) - API 지연 시간 고려
DECISION_INTERVAL = 3.0 # 3초마다 한 번씩 VLM/LLM 판단

# 포스터 Fig2. 용 이미지 저장 폴더
OUTPUT_DIR = "experiment_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    tello = TelloController()
    if not tello.connect():
        return

    try:
        tello.streamon()
        frame_read = tello.get_frame_read()
        
        tello.takeoff()
        
        last_decision_time = time.time()
        current_command = "STOP" # 초기 상태
        last_command = "STOP"

        while True:
            # 1. Tello 프레임 읽기 
            img = frame_read.frame
            display_img = cv2.resize(img, (720, 480)) [1]
            
            current_time = time.time()
            
            # 2. AI 의사결정 주기 확인
            if current_time - last_decision_time > DECISION_INTERVAL:
                print("\n--- AI 의사결정 시작 ---")
                
                # 3. VLM (시각) 분석 (T_s) 
                b64_img = encode_image_frame(img)
                vlm_text = get_vlm_analysis(b64_img)
                print(f": {vlm_text}")
                
                # 4. VPS (센서) 상태 (T_v) 
                vps_text = get_vps_state_text(tello.drone)
                print(f": {vps_text}")
                
                # 5. LLM (융합) 결정 (A_t) 
                current_command = get_llm_decision(vlm_text, vps_text)
                print(f"[LLM $A_t$]: {current_command}")
                
                last_decision_time = current_time

                # 6. (중요) 포스터 Fig2. 용 이미지 캡처 
                # 명령이 변경되는 '결정적 순간'에만 이미지 저장
                if current_command!= last_command:
                    filename = f"{OUTPUT_DIR}/{time.strftime('%Y%m%d_%H%M%S')}_{current_command}.jpg"
                    cv2.imwrite(filename, img)
                    print(f"*** 결정적 순간 캡처: {filename} ***")
                    last_command = current_command

            # 7. 드론 제어 실행
            tello.execute_command(current_command)

            # 8. 화면에 현재 상태 표시
            cv2.putText(display_img, f"Battery: {tello.get_battery()}%", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(display_img, f"COMMAND: {current_command}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("Tello VLM-VPS Fusion (Press 'q' to land)", display_img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("'q' 입력 감지. 착륙합니다.")
                break

    except Exception as e:
        print(f"메인 루프 오류: {e}")
    
    finally:
        print("--- 비행 종료 ---")
        tello.land()
        tello.streamoff()
        tello.end()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()