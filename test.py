import subprocess
import platform


def simple_test():
    """Простой тест доступности хостов"""
    test_hosts = [
        "198.18.200.55", "198.18.200.54", "198.18.200.189", "198.18.200.216"
    ]

    for host in test_hosts:
        try:
            # Команда ping в зависимости от ОС
            param = "-n" if platform.system().lower() == "windows" else "-c"
            command = ["ping", param, "2", host]

            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ {host} - ДОСТУПЕН")
            else:
                print(f"❌ {host} - НЕДОСТУПЕН")

        except Exception as e:
            print(f"⚠️ {host} - ОШИБКА: {e}")


# Запустите этот тест сначала
simple_test()