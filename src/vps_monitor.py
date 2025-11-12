def get_vps_state_text(tello_instance):
    """VPS 관련 센서 데이터 읽기 (T_v) """
    try:
        # Tello의 하방 적외선 센서(Time-of-Flight)는 30cm~1000cm 범위에서 작동 
        tof_distance_cm = tello_instance.get_distance_tof() [1]
        height_cm = tello_instance.get_height() # 기압계 기반 고도 
        
        if tof_distance_cm > 30:
            return f"VPS STABLE. TOF 고도: {tof_distance_cm}cm, 기압계 고도: {height_cm}cm"
        else:
            return f"VPS WARNING: LOW ALTITUDE. TOF 고도: {tof_distance_cm}cm"
            
    except Exception as e:
        print(f"VPS 센서 오류: {e}")
        return "VPS SENSOR READ FAILED"