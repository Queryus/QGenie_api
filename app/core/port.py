# app/core/port.py

import os
import socket


def get_available_port(default: int = 8000) -> int:
    """
    환경변수 'PORT'가 존재하면 해당 포트를 사용하고,
    없다면 시스템이 할당한 사용 가능한 포트를 반환합니다.
    """
    port_from_env = os.getenv("PORT")

    if port_from_env:
        print(f"Using port from environment variable: {port_from_env}")
        return int(port_from_env)

    # 포트 0 바인딩 → 시스템이 사용 가능한 포트 할당
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 0))
        assigned_port = s.getsockname()[1]
        print(f"Dynamically assigned port: {assigned_port}")
        return assigned_port
