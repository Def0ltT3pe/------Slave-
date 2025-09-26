# ssh_handler.py
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
            
            self.client.connect(
                hostname=host,
                username=username,
                password=password,
                port=port
            )
            
            self.is_connected = True
            print(f"Успешное подключение к {username}@{host}:{port}")
            return True
            
        except paramiko.AuthenticationException:
            print("Ошибка аутентификации. Проверьте логин/пароль")
        except paramiko.SSHException as e:
            print(f"SSH ошибка: {e}")
        except Exception as e:
            print(f"Ошибка подключения: {e}")
        return False
    
    def execute_command(self, command: str) -> dict:
        """Выполнение команды на сервере"""
        if not self.is_connected:
            return {"error": "Не подключено к серверу"}
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
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
    
    def disconnect(self):
        """Отключение от сервера"""
        if self.client:
            self.client.close()
        self.is_connected = False
        print("🔌 Отключено от сервера")

def get_open_ports(ip: str) -> list:
    """
    Функция для сканирования открытых портов
    (заглушка - нужно реализовать или импортировать реальную функцию)
    """
    # Заглушка - возвращаем стандартные SSH порты
    # В реальности здесь должно быть сканирование портов
    return [22, 80, 443, 8080]  # Пример открытых портов

def ssh_connect_and_scan(ip: str, login: str, password: str):
    """
    Основная функция для подключения по SSH и выполнения команд
    """
    # Получаем открытые порты
    open_ports = get_open_ports(ip)
    
    print(f"\nДанные для подключения:")
    print(f"IP: {ip}")
    print(f"Логин: {login}")
    print(f"Пароль: {password}")
    print(f"Открытые порты: {open_ports}")
    
    # Создаем SSH хендлер
    ssh_handler = FixedSSHHandler()
    
    # Пытаемся подключиться к стандартному SSH порту (22)
    if ssh_handler.connect(ip, login, password, 22):
        print("\nПодключение установлено! Выполняем базовые команды...")
        
        # Выполняем системные команды для сбора информации
        commands = [
            "uname -a",
            "whoami",
            "pwd",
            "ls -la",
            "cat /etc/os-release || lsb_release -a || uname -o"
        ]
        
        for cmd in commands:
            print(f"\n--- Выполняем: {cmd} ---")
            result = ssh_handler.execute_command(cmd)
            
            if result.get("output"):
                print(result["output"])
            if result.get("error"):
                print(f"Ошибка: {result['error']}")
        
        # Предлагаем интерактивный режим
        response = input("\nПерейти в интерактивный режим? (y/n): ").strip().lower()
        if response == 'y':
            start_interactive_session(ssh_handler)
    
    else:
        print("❌ Не удалось подключиться по SSH")
    
    # Закрываем соединение
    ssh_handler.disconnect()

def start_interactive_session(ssh_handler):
    """Запуск интерактивной SSH сессии"""
    print("\n🎮 Интерактивная SSH сессия")
    print("Команды: help - справка, exit - выход")
    print("-" * 50)
    
    while ssh_handler.is_connected:
        try:
            command = input("\nssh> ").strip()
            
            if not command:
                continue
            
            if command.lower() == 'exit':
                break
            elif command.lower() == 'help':
                print_help()
            else:
                result = ssh_handler.execute_command(command)
                print_result(result)
                
        except KeyboardInterrupt:
            print("\nСессия прервана")
            break
        except Exception as e:
            print(f"Ошибка: {e}")

def print_help():
    """Показать справку по командам"""
    help_text = """
Доступные команды:
• Любые Linux команды: ls, cd, pwd, cat, grep, find, ps, etc.
• help - показать справку
• exit - выйти из сессии

Примеры:
  ls -la /home
  cat /etc/passwd
  ps aux | grep ssh
  df -h
  free -m
  netstat -tuln
    """
    print(help_text)

def print_result(result: dict):
    """Печать результата выполнения команды"""
    if "error" in result:
        print(f"❌ Ошибка: {result['error']}")
    else:
        if result.get("output"):
            print("Результат:")
            print(result["output"].strip())
        if result.get("error"):
            print("Ошибки:")
            print(result["error"].strip())
        if result.get("exit_status") != 0:
            print(f"Код выхода: {result['exit_status']}")