# protocols/vnc_simple_connect.py
import subprocess
import platform
import os

def vnc_connect(ip: str, password: str = "", port: int = 5900):
    """Запуск VNC Viewer через полный путь к exe"""
    try:
        vnc_address = f"{ip}:{port}"
        
        if platform.system() == "Windows":
            # Пути к VNC Viewer в Windows
            vnc_paths = [
                r"D:\VNCviewer\vncviewer.exe"
#                r"C:\Program Files (x86)\RealVNC\VNC Viewer\vncviewer.exe",
#                r"C:\Program Files\TigerVNC\vncviewer.exe",
            ]
            
            for path in vnc_paths:
                if os.path.exists(path):
                    subprocess.Popen([path, vnc_address])
                    print(f"VNC Viewer запущен: {path}")
                    print(f"Подключение к {vnc_address}")
                    return True
            
            print("VNC Viewer не найден по стандартным путям")
            return False
            
        else:
            # Для Linux/Mac
            subprocess.Popen(["vncviewer", vnc_address])
            print(f"VNC Viewer запущен: {vnc_address}")
            return True
        
    except Exception as e:
        print(f"Ошибка запуска VNC Viewer: {e}")
        return False