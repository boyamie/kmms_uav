def get_vps_state_text(tello_instance):

    try: 
        tof_distance_cm = tello_instance.get_distance_tof()
        
        height_cm = tello_instance.get_height()

        if tof_distance_cm > 30:
            return f"VPS STABLE. TOF 고도: {tof_distance_cm}cm, 기압계 고도: {height_cm}cm"
        else:
            return f"VPS WARNING: LOW ALTITUDE. TOF 고도: {tof_distance_cm}cm"
            
    except Exception as e:
        print(f"[오류] VPS 센서 읽기 실패: {e}")
        return "VPS SENSOR READ FAILED"