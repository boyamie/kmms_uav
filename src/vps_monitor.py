def get_vps_state_text(tello_instance):
    """
    Tello의 하방 센서(VPS) 상태를 읽어 텍스트(T_v)로 반환합니다.
    Tello 매뉴얼에 따르면 VPS는 0.3m ~ 10m 범위에서 작동합니다. 
    """
    try:
        # Tello의 하방 거리 측정 센서(Time-of-Flight) 값(cm)
        tof_distance_cm = tello_instance.get_distance_tof()
        
        # 기압계 기반 고도 값(cm)
        height_cm = tello_instance.get_height()
        
        # Tello 매뉴얼(p.7)에 따르면 VPS는 30cm 이상에서 유효합니다. 
        if tof_distance_cm > 30:
            return f"VPS STABLE. TOF 고도: {tof_distance_cm}cm, 기압계 고도: {height_cm}cm"
        else:
            # 30cm 미만은 VPS가 불안정할 수 있는 저고도 영역입니다.
            return f"VPS WARNING: LOW ALTITUDE. TOF 고도: {tof_distance_cm}cm"
            
    except Exception as e:
        print(f"[오류] VPS 센서 읽기 실패: {e}")
        # 'int' object is not subscriptable 오류는
        # .py 코드 파일에 같은 텍스트 태그가 남아있을 때 발생합니다.
        return "VPS SENSOR READ FAILED"
