# run_mission.py
import cv2
import time
import os
from src.tello_controller import TelloController
from src.vps_monitor import get_vps_state_text
# API 함수 대신 Local 함수를 임포트
from src.ai_gateway import get_vlm_analysis_local, get_llm_decision_local

# AI 의사결정 주기 (초) - 로컬 처리는 매우 빠름
DECISION_INTERVAL = 1.0 # 1초마다 한 번씩 VLM/LLM 판단

# 포스터 Fig2. 용 이미지 저장 폴더 
OUTPUT_DIR = "experiment_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    tello = TelloController()
    if not tello.connect():
        print("[메인] 드론 연결 실패. 프로그램을 종료합니다.")
        return

    try:
        tello.streamon() # 수업자료 실습 5-2 
        frame_read = tello.get_frame_read() # 수업자료 실습 5-2 
        
        print("\n[메인] 이륙 준비... (5초 후 이륙)")
        time.sleep(5)
        tello.takeoff() # 수업자료 실습 5-2 
        
        last_decision_time = time.time()
        current_command = "STOP" # 초기 상태
        last_command = "STOP"

        while True:
            # 1. Tello 프레임 읽기 (수업자료 실습 5-2) 
            img = frame_read.frame
            if img is None:
                continue
                
            display_img = cv2.resize(img, (720, 480)) # 
            
            current_time = time.time()
            
            # 2. AI 의사결정 주기 확인
            if current_time - last_decision_time > DECISION_INTERVAL:
                print("\n--- AI 의사결정 시작 ---")
                
                # 3. VLM (시각) 분석 (T_s) 
                # API 대신 로컬 함수 호출 (Base64 인코딩 불필요)
                vlm_text = get_vlm_analysis_local(img) 
                print(f": {vlm_text}")
                
                # 4. VPS (센서) 상태 (T_v) 
                vps_text = get_vps_state_text(tello.drone)
                print(f": {vps_text}")
                
                # 5. LLM (융합) 결정 (A_t) 
                # API 대신 로컬 함수 호출
                current_command = get_llm_decision_local(vlm_text, vps_text) 
                print(f"[LLM $A_t$]: {current_command}")
                
                last_decision_time = current_time

                # 6. (중요) 포스터 Fig2. 용 이미지 캡처 
                # 명령이 변경되는 '결정적 순간'에만 이미지 저장
                if current_command!= last_command:
                    filename = f"{OUTPUT_DIR}/{time.strftime('%Y%m%d_%H%M%S')}_{current_command}.jpg"
                    cv2.imwrite(filename, img) # 수업자료 실습 5-1 
                    print(f"*** 결정적 순간 캡처: {filename} ***")
                    last_command = current_command

            # 7. 드론 제어 실행 (수업자료 send_rc_control) 
            tello.execute_command(current_command) [1]

            # 8. 화면에 현재 상태 표시 (수업자료 실습 5-2) 
            cv2.putText(display_img, f"Battery: {tello.get_battery()}%", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(display_img, f"COMMAND: {current_command}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("Tello VLM-VPS Fusion (Press 'q' to land)", display_img) [1]

            if cv2.waitKey(1) & 0xFF == ord('q'): # 수업자료 실습 5-2 
                print("'q' 입력 감지. 착륙합니다.")
                break

    except Exception as e:
        print(f"[오류] 메인 루프 오류: {e}")
    
    finally:
        print("--- 비행 종료 ---")
        tello.land() # 수업자료 실습 5-2 
        tello.streamoff() # 수업자료 실습 5-2 
        tello.end()
        cv2.destroyAllWindows() # 수업자료 실습 5-2 

if __name__ == "__main__":
    main()