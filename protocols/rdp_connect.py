import os
import platform
import subprocess

def rdp_connect(ip: str, username: str, password: str) -> bool:
    try:
        if platform.system() == "Windows":
            # Для Windows
            subprocess.Popen(f'mstsc /v:{ip}', shell=True)
#       else:
#           # Для Linux/Mac (?)
#           subprocess.Popen([
#               'xfreerdp', f'/v:{ip}', f'/u:{username}', 
#               f'/p:{password}', '/cert-ignore'
#           ])
        return True
    except Exception as e:
        print(f"RDP ошибка: {e}")
        return False