import subprocess
import sys


class LinuxRDPClient:
    def __init__(self):
        self.server = ""
        self.username = ""
        self.password = ""
        self.port = "3389"

    def input_credentials(self):
        """Ручной ввод учетных данных"""
        print("\nВведите данные для подключения:")
        self.server = input("Адрес сервера: ")
        self.username = input("Имя пользователя: ")
        self.password = input("Пароль: ")  # Видимый пароль
        self.port = input("Порт [3389]: ") or "3389"

    def test_connection(self):
        """Проверяет доступность сервера"""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', self.server],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def connect_simple(self):
        """Простое подключение"""
        cmd = [
            'xfreerdp',
            f'/v:{self.server}:{self.port}',
            f'/u:{self.username}',
            f'/p:{self.password}',
            '/size:1024x768',
            '+fonts',
            '+clipboard'
        ]

        print(f"\nПодключаемся к {self.server}...")
        subprocess.run(cmd)

    def connect_fullscreen(self):
        """Полноэкранное подключение"""
        cmd = [
            'xfreerdp',
            f'/v:{self.server}:{self.port}',
            f'/u:{self.username}',
            f'/p:{self.password}',
            '/f',
            '+fonts',
            '+clipboard',
            '+auto-reconnect'
        ]

        print(f"\nПодключаемся к {self.server} (полный экран)...")
        subprocess.run(cmd)

    def connect_with_terminal(self):
        """Подключение с запуском терминала"""
        cmd = [
            'xfreerdp',
            f'/v:{self.server}:{self.port}',
            f'/u:{self.username}',
            f'/p:{self.password}',
            '/size:1024x768',
            '/shell:xterm',
            '/shell-dir:/home',
            '+fonts'
        ]

        print(f"\nПодключаемся к {self.server} с терминалом...")
        subprocess.run(cmd)

    def run(self):
        """Основной цикл программы"""

        print("RDP клиент для Linux серверов")
        print("Пароль будет отображаться при вводе")

        while True:
            print("\n" + "=" * 40)
            print("1. Ввести данные подключения")
            print("2. Простое подключение")
            print("3. Полноэкранное подключение")
            print("4. Подключение с терминалом")
            print("5. Выход")

            choice = input("Выберите действие: ")

            if choice == "1":
                self.input_credentials()
            elif choice == "2":
                if not self.server:
                    print("Сначала введите данные подключения!")
                    self.input_credentials()
                self.connect_simple()
            elif choice == "3":
                if not self.server:
                    print("Сначала введите данные подключения!")
                    self.input_credentials()
                self.connect_fullscreen()
            elif choice == "4":
                if not self.server:
                    print("Сначала введите данные подключения!")
                    self.input_credentials()
                self.connect_with_terminal()
            elif choice == "5":
                print("Выход...")
                break
            else:
                print("Неверный выбор!")


if __name__ == "__main__":
    client = LinuxRDPClient()
    client.run()