from djitellopy import Tello
import cv2
import time

# Tello 객체 생성
tello = Tello()

# 연결 및 스트림 켜기
tello.connect()
tello.streamon() [1]
frame_read = tello.get_frame_read() [1]

# 이륙
# tello.takeoff() # 안전을 위해 실제 이륙은 주석 처리

print("--- 카메라 스트림 시작 ---")
print("q: 종료 | t: 이륙 | l: 착륙")
print("w: 전진 | s: 후진 | a: 좌 | d: 우")

try:
    while True:
        # 프레임 읽기
        img = frame_read.frame
        # 이미지 크기 조절 (선택 사항)
        img = cv2.resize(img, (720, 480)) [1]
        
        # 화면에 영상 표시
        cv2.imshow("Tello Stream", img) [1]
        
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('t'):
            print("이륙!")
            tello.takeoff() [1]
        elif key == ord('l'):
            print("착륙!")
            tello.land() [1]
        elif key == ord('w'):
            tello.move_forward(30) [1]
        elif key == ord('s'):
            tello.move_back(30) [1]
        elif key == ord('a'):
            tello.move_left(30) [1]
        elif key == ord('d'):
            tello.move_right(30) [1]
        
        # (중요) RC 컨트롤을 사용하지 않을 때의 호버링 유지
        # tello.send_rc_control(0, 0, 0, 0) # 키보드 입력이 없을 때 제자리 유지

except Exception as e:
    print(f"비행 중 오류 발생: {e}")

finally:
    print("--- 비행 종료 ---")
    tello.land()
    tello.streamoff()
    cv2.destroyAllWindows()