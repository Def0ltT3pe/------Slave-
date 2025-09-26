import os
import platform
import subprocess

class SimpleRDP:
    def __init__(self):
        self.is_connected = False
    
    def connect(self, ip: str, username: str, password: str, domain: str = ""):
        """Простое подключение по RDP"""
        try:
            system = platform.system().lower()
            
            if system == "windows":
                # Windows - используем mstsc
                cmd = f'cmdkey /generic:{ip} /user:{username} /pass:"{password}"'
                os.system(cmd)
                
                cmd = f'mstsc /v:{ip}'
                subprocess.Popen(cmd, shell=True)
                
            else:
                # Linux/Mac - используем xfreerdp
                cmd = [
                    'xfreerdp',
                    f'/v:{ip}',
                    f'/u:{username}',
                    f'/p:{password}',
                    '/cert-ignore',
                    '+fonts',
                    '/clipboard',
                    '/gdi:sw'
                ]
                
                if domain:
                    cmd.append(f'/d:{domain}')
                
                subprocess.Popen(cmd)
            
            self.is_connected = True
            print(f"Подключаемся к {ip}...")
            print("RDP клиент запущен в отдельном окне")
            
        except Exception as e:
            print(f"Ошибка: {e}")

def quick_rdp_connect():
    """Быстрое подключение по RDP"""
    print("Быстрое подключение по RDP")
    print("-" * 30)
    
    ip = input("Введите IP адрес: ").strip()
    username = input("Введите логин: ").strip()
    password = input("Введите пароль: ").strip()
    domain = input("Введите домен (если есть, или Enter): ").strip()
    
    rdp = SimpleRDP()
    rdp.connect(ip, username, password, domain)
    
    if rdp.is_connected:
        print("\n RDP сессия запущена!")
        print("Закройте RDP окно для завершения")
    else:
        print("Не удалось запустить RDP")

# Самый простой вариант - одна функция
def ultra_simple_rdp(ip, username, password):
    """Ультра-простой RDP"""
    if platform.system() == "Windows":
        os.system(f'start mstsc /v:{ip}')
    else:
        os.system(f'xfreerdp /v:{ip} /u:{username} /p:{password} /cert-ignore')

# Пример использования
if __name__ == "__main__":
    quick_rdp_connect()