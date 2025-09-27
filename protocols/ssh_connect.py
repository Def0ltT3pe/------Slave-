# ssh_handler.py
import paramiko

class SSHHandler:
    def __init__(self):
        self.client = None
        self.is_connected = False
    
    def connect(self, host: str, username: str, password: str, port: int = 22) -> bool:
        # Подключение к SSH серверу
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(hostname=host, username=username, password=password, port=port)
            self.is_connected = True
            print(f"Подключено к {username}@{host}:{port}")
            return True
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False
    
    def execute_command(self, command: str) -> str:
        # Выполнение команды на сервере
        if not self.is_connected:
            return "Не подключено к серверу"
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            return output if output else error
        except Exception as e:
            return f"Ошибка выполнения: {e}"
    
    def disconnect(self):
        # Отключение
        if self.client:
            self.client.close()
        self.is_connected = False

def ssh_connect(ip: str, login: str, password: str):
    # Основная функция
    ssh = SSHHandler()
    
    if ssh.connect(ip, login, password, 22):
        # Выполняем базовые команды
        commands = [
            "uname -a",
            "whoami", 
            "pwd",
            "ls -la",
            "cat /etc/os-release || echo 'Нет информации о ОС'"
        ]
        
        for cmd in commands:
            print(f"\n--- {cmd} ---")
            result = ssh.execute_command(cmd)
            print(result)
        
        # Интерактивный режим
        print("\nИнтерактивный режим (exit для выхода):")
        while ssh.is_connected:
            cmd = input("ssh> ").strip()
            if cmd.lower() == 'exit':
                break
            if cmd:
                result = ssh.execute_command(cmd)
                print(result)
    
    ssh.disconnect()