from djitellopy import Tello
import time

class TelloController:
    """
    Tello 드론의 연결, 제어, 상태 모니터링을 담당하는 메인 컨트롤러 클래스입니다.
    djitellopy의 Tello 객체를 래핑(wrapping)하여 사용합니다.
    """
    def __init__(self):
        self.drone = Tello()
        self.is_connected = False
        print("[INFO] TelloController 객체 생성 완료.")

    def connect(self):
        """드론에 연결합니다."""
        try:
            self.drone.connect()
            print("[INFO] --- 드론 연결 성공 ---")
            
            battery = self.drone.get_battery()
            print(f"[INFO] 배터리 잔량: {battery}%")
            
            if battery < 20:
                print(f"[경고] 배터리가 {battery}%로 너무 낮습니다. 비행을 권장하지 않습니다.")
                # (참고) 실제 비행 시 여기서 False를 반환하여 중단할 수 있습니다.
                # return False 
                
            self.is_connected = True
            return True
            
        # 'Exception as e'는 모든 오류(TypeError 포함)를 잡습니다.
        except Exception as e: 
            print(f"\n[오류] TelloController.connect() 도중 오류 발생: {e}")
            print(">>> 1. 맥북이 Tello Wi-Fi에 연결되었는지 확인하세요.")
            print(">>> 2. 맥북/스마트폰의 다른 Tello 앱이 완전히 종료되었는지 확인하세요.")
            print(">>> 3. src/tello_controller.py 같은.py 파일 내에  같은 텍스트 태그가 남아있는지 확인하세요.\n")
            return False

    def takeoff(self):
        """드론을 이륙시킵니다."""
        if self.is_connected and not self.drone.is_flying:
            try:
                print("[INFO] 이륙 (Takeoff)...")
                self.drone.takeoff()
                time.sleep(3) # 안정화를 위한 대기
            except Exception as e:
                print(f"[오류] 이륙 실패: {e}")

    def land(self):
        """드론을 착륙시킵니다."""
        if self.is_connected and self.drone.is_flying:
            try:
                print("[INFO] 착륙 (Landing)...")
                self.drone.land()
            except Exception as e:
                print(f"[오류] 착륙 실패: {e}")

    def streamon(self):
        """카메라 비디오 스트림을 켭니다."""
        if self.is_connected:
            try:
                self.drone.streamon()
                print("[INFO] 카메라 스트림 ON")
            except Exception as e:
                print(f"[오류] 스트림 켜기 실패: {e}")

    def streamoff(self):
        """카메라 비디오 스트림을 끕니다."""
        if self.is_connected:
            try:
                self.drone.streamoff()
                print("[INFO] 카메라 스트림 OFF")
            except Exception as e:
                print(f"[오류] 스트림 끄기 실패: {e}")
            
    def get_frame_read(self):
        """비디오 프레임 리더 객체를 반환합니다."""
        if self.is_connected:
            return self.drone.get_frame_read()
        return None
        
    def end(self):
        """모든 연결을 종료합니다."""
        if self.is_connected:
            print("[INFO] 드론 연결 종료.")
            self.drone.end()

    def execute_command(self, command: str):
        """
        LLM이 생성한 'FORWARD', 'STOP' 등의 상위 레벨 명령어를
        Tello의 send_rc_control 명령어로 변환하여 실행합니다.
        """
        if not self.is_connected or not self.drone.is_flying:
            return
            
        try:
            if command == "FORWARD":
                # (left_right, forward_backward, up_down, yaw)
                # 20% 속도로 전진
                self.drone.send_rc_control(0, 20, 0, 0)
            elif command == "STOP":
                # 모든 속도를 0으로 하여 정지 (호버링)
                self.drone.send_rc_control(0, 0, 0, 0)
            elif command == "BACKWARD":
                # 20% 속도로 후진
                self.drone.send_rc_control(0, -20, 0, 0)
            elif command == "LAND":
                self.land()
            # Image 2(사무실)  환경을 위한 'ASCEND' 명령
            elif command == "ASCEND":
                self.drone.send_rc_control(0, 0, 20, 0) # 20% 속도로 상승
                
        except Exception as e:
            print(f"[오류] RC 제어 명령({command}) 실패: {e}")
            self.land() # 제어 실패 시 안전을 위해 즉시 착륙

    def get_battery(self):
        """배터리 잔량을 반환합니다."""
        if self.is_connected:
            return self.drone.get_battery()
        return 0