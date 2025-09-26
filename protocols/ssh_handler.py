import paramiko
import sys
import time
import os

class FixedSSHHandler:
    def __init__(self):
        self.client = None
        self.is_connected = False
    
    def connect(self, host: str, username: str, password: str, port: int = 22) -> bool:
        """Подключение к SSH серверу (исправленная версия)"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # ПРАВИЛЬНЫЙ ВЫЗОВ - передаем параметры как именованные аргументы
            self.client.connect(
                hostname=host,      # явно указываем hostname
                username=username,  # явно указываем username  
                password=password,  # явно указываем password
                port=port           # явно указываем port
            )
            
            self.is_connected = True
            print(f"✅ Успешное подключение к {username}@{host}:{port}")
            return True
            
        except paramiko.AuthenticationException:
            print("❌ Ошибка аутентификации. Проверьте логин/пароль")
        except paramiko.SSHException as e:
            print(f"❌ SSH ошибка: {e}")
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
        return False
    
    def execute_command(self, command: str) -> dict:
        """Выполнение команды на сервере"""
        if not self.is_connected:
            return {"error": "Не подключено к серверу"}
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            
            # Ждем завершения команды
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            
            return {
                "output": output,
                "error": error,
                "exit_status": exit_status,
                "command": command
            }
            
        except Exception as e:
            return {"error": f"Ошибка выполнения: {e}"}
    
    def interactive_session(self):
        """Интерактивная сессия"""
        if not self.is_connected:
            print("❌ Сначала подключитесь к серверу")
            return
        
        print("\n🎮 Интерактивная SSH сессия")
        print("Команды:")
        print("  help - показать справку")
        print("  exit - выйти")
        print("  download <remote> <local> - скачать файл")
        print("  upload <local> <remote> - загрузить файл")
        print("-" * 50)
        
        while self.is_connected:
            try:
                command = input("\nssh> ").strip()
                
                if not command:
                    continue
                
                if command.lower() == 'exit':
                    break
                elif command.lower() == 'help':
                    self.show_help()
                elif command.lower().startswith('download '):
                    self.handle_download(command)
                elif command.lower().startswith('upload '):
                    self.handle_upload(command)
                else:
                    result = self.execute_command(command)
                    self.print_result(result)
                    
            except KeyboardInterrupt:
                print("\n⏹️ Сессия прервана")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
    
    def show_help(self):
        """Показать справку"""
        help_text = """
📋 Доступные команды:
• Любые Linux команды: ls, cd, pwd, cat, grep, find, etc.
• help - показать эту справку
• exit - выйти из сессии
• download <remote_path> <local_path> - скачать файл
• upload <local_path> <remote_path> - загрузить файл

Примеры:
  ls -la /home
  cat /etc/passwd
  ps aux | grep ssh
  download /var/log/syslog ./syslog.txt
  upload script.sh /tmp/script.sh
        """
        print(help_text)
    
    def handle_download(self, command: str):
        """Скачивание файла с сервера"""
        try:
            parts = command.split()
            if len(parts) != 3:
                print("❌ Использование: download <remote_path> <local_path>")
                return
            
            remote_path, local_path = parts[1], parts[2]
            sftp = self.client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            print(f"✅ Файл {remote_path} скачан как {local_path}")
        except Exception as e:
            print(f"❌ Ошибка скачивания: {e}")
    
    def handle_upload(self, command: str):
        """Загрузка файла на сервер"""
        try:
            parts = command.split()
            if len(parts) != 3:
                print("❌ Использование: upload <local_path> <remote_path>")
                return
            
            local_path, remote_path = parts[1], parts[2]
            if not os.path.exists(local_path):
                print(f"❌ Локальный файл не найден: {local_path}")
                return
            
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            print(f"✅ Файл {local_path} загружен как {remote_path}")
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
    
    def print_result(self, result: dict):
        """Печать результата выполнения команды"""
        if "error" in result:
            print(f"❌ Ошибка: {result['error']}")
        else:
            if result.get("output"):
                print("📋 Результат:")
                print(result["output"].strip())
            if result.get("error"):
                print("⚠️  Ошибки:")
                print(result["error"].strip())
            if result.get("exit_status") != 0:
                print(f"🔚 Код выхода: {result['exit_status']}")
    
    def disconnect(self):
        """Отключение от сервера"""
        if self.client:
            self.client.close()
        self.is_connected = False
        print("🔌 Отключено от сервера")

# Упрощенная версия для тестирования
class SimpleSSHHandler:
    def __init__(self):
        self.client = None
    
    def connect(self, host: str, username: str, password: str, port: int = 22) -> bool:
        """Простое подключение"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # ПРАВИЛЬНЫЙ ВЫЗОВ
            self.client.connect(
                hostname=host,
                username=username, 
                password=password,
                port=port
            )
            
            print(f"✅ Подключено к {host}:{port}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def test_connection(self):
        """Тестирование подключения"""
        stdin, stdout, stderr = self.client.exec_command('uname -a && whoami && pwd')
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        print("📊 Информация о сервере:")
        print(output)
        if error:
            print("Ошибки:", error)
    
    def disconnect(self):
        """Отключение"""
        if self.client:
            self.client.close()
        print("🔌 Отключено")

# Функция для получения данных подключения
def get_connection_info():
    """Запрос данных для подключения"""
    print("=== SSH Подключение ===")
    
    host = input("Введите IP адрес или hostname: ").strip()
    if not host:
        host = "localhost"  # значение по умолчанию
    
    username = input("Введите имя пользователя: ").strip()
    if not username:
        username = "root"  # значение по умолчанию
    
    password = input("Введите пароль: ").strip()
    
    port_str = input("Введите порт (по умолчанию 22): ").strip()
    port = int(port_str) if port_str else 22
    
    return host, username, password, port

# Основная функция
def main():
    print("🔧 Исправленный SSH клиент")
    
    # Выбор режима
    print("\nВыберите режим:")
    print("1. Простой тест подключения")
    print("2. Интерактивная сессия")
    
    choice = input("Ваш выбор (1-2): ").strip()
    
    # Получаем данные подключения
    host, username, password, port = get_connection_info()
    
    if choice == "1":
        # Простой тест
        ssh = SimpleSSHHandler()
        if ssh.connect(host, username, password, port):
            ssh.test_connection()
            ssh.disconnect()
    else:
        # Интерактивная сессия
        ssh = FixedSSHHandler()
        if ssh.connect(host, username, password, port):
            ssh.interactive_session()
            ssh.disconnect()

if __name__ == "__main__":
    main()