import cv2
import time
import os
from src.tello_controller import TelloController
from src.vps_monitor import get_vps_state_text
from src.ai_gateway import get_vlm_analysis_local, get_llm_decision_local

DECISION_INTERVAL = 1.0 

OUTPUT_DIR = "experiment_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    tello = TelloController()
    if not tello.connect():
        print("[메인] 드론 연결 실패. 프로그램을 종료합니다.")
        return

    try:
        tello.streamon()
        frame_read = tello.get_frame_read()
        
        print("\n[메인] 이륙 준비... (5초 후 이륙)")
        time.sleep(5)
        tello.takeoff() 
        
        last_decision_time = time.time()
        current_command = "STOP" 
        last_command = "STOP"

        while True:
            img = frame_read.frame
            if img is None:
                continue
                
            display_img = cv2.resize(img, (720, 480)) 
            
            current_time = time.time()
            
            if current_time - last_decision_time > DECISION_INTERVAL:
                print("\n--- AI 의사결정 시작 ---")
                
                vlm_text = get_vlm_analysis_local(img) 
                print(f": {vlm_text}")
                
                vps_text = get_vps_state_text(tello.drone)
                print(f": {vps_text}")

                current_command = get_llm_decision_local(vlm_text, vps_text) 
                print(f"[LLM $A_t$]: {current_command}")
                
                last_decision_time = current_time

                if current_command!= last_command:
                    filename = f"{OUTPUT_DIR}/{time.strftime('%Y%m%d_%H%M%S')}_{current_command}.jpg"
                    cv2.imwrite(filename, img) 
                    print(f"*** 결정적 순간 캡처: {filename} ***")
                    last_command = current_command

            tello.execute_command(current_command) [1]

            cv2.putText(display_img, f"Battery: {tello.get_battery()}%", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(display_img, f"COMMAND: {current_command}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("Tello VLM-VPS Fusion (Press 'q' to land)", display_img) [1]

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("'q' 입력 감지. 착륙합니다.")
                break

    except Exception as e:
        print(f"[오류] 메인 루프 오류: {e}")
    
    finally:
        print("--- 비행 종료 ---")
        tello.land()
        tello.streamoff()
        tello.end()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()