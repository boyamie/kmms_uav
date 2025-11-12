from djitellopy import Tello
import time

# Tello 객체 생성
tello = Tello()

try:
    # 드론에 연결
    tello.connect()
    
    # 배터리 잔량 확인
    battery = tello.get_battery()
    print(f"--- 드론 연결 성공 ---")
    print(f"배터리 잔량: {battery}%")
    
    # 배터리가 20% 미만이면 경고
    if battery < 20:
        print("경고: 배터리가 너무 낮습니다. 충전 후 시도하세요.")
    else:
        print("배터리 양호. 다음 단계를 진행할 수 있습니다.")

except Exception as e:
    print(f"드론 연결 실패: {e}")
    print("PC가 Tello Wi-Fi에 연결되었는지 확인하세요.")

finally:
    # 연결 종료 (실제 비행 시에는 이륙/착륙 후 end() 호출)
    # 여기서는 상태만 확인하므로 바로 end()를 사용하지 않을 수 있습니다.
    # tello.end() # 실제 비행 코드에서는 land() 후에 호출
    pass