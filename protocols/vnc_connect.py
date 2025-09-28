# protocols/vnc_simple_connect.py
import subprocess
import platform
import os
import tkinter as tk
from tkinter import filedialog

def vnc_connect(ip: str, password: str = "", port: int = 5900):
    try:
        vnc_address = f"{ip}:{port}"
        
        if platform.system() == "Windows":
            # Пути к VNC Viewer в Windows
            vnc_paths = [
                r"D:\VNCviewer\vncviewer.exe"
            ]
            
            # Проверка на стандартные стандартные пути
            vnc_path = None
            for path in vnc_paths:
                if os.path.exists(path):
                    vnc_path = path
                    break
            
            # Запрос у пользователя
            if not vnc_path:
                root = tk.Tk()
                root.withdraw()  # Скрываем основное окно (?)
                
                print("VNC Viewer не найден по стандартным путям. Пожалуйста, укажите путь к vncviewer.exe")
                vnc_path = filedialog.askopenfilename(
                    title="Выберите VNC Viewer (vncviewer.exe)",
                    filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
                )
                root.destroy()
                
                if not vnc_path:  # Пользователь отменил выбор
                    print("Путь к VNC Viewer не указан")
                    return False
            
            # Запускаем VNC Viewer
            subprocess.Popen([vnc_path, vnc_address])
            print(f"VNC Viewer запущен: {vnc_path}")
            print(f"Подключение к {vnc_address}")
            return True
            
#       else:
#           # Для Linux/Mac
#           subprocess.Popen(["vncviewer", vnc_address])
#           print(f"VNC Viewer запущен: {vnc_address}")
#           return True
        
    except Exception as e:
        print(f"Ошибка запуска VNC Viewer: {e}")
        return False