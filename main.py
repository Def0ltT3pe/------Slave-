import socket

def check_port(ip: str, port: int) -> bool:
    """Проверка открытых портов"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def get_open_ports(ip: str) -> list:
    """Создает переменную с открытыми портами IP"""
    ports = [21, 22, 23, 80, 443, 3389, 5900]
    
#    print(f"Сканируем {ip}...")
    
    open_ports = []
    
    for port in ports:
        if check_port(ip, port):
            open_ports.append(port)
    
    return open_ports

from protocols.ssh_handler import ssh_connect_and_scan

def main():
    # Ввод данных для подключения
    ip = input("Введите IP-адрес для сканирования: ").strip()
    login = input("Введите логин: ").strip()
    password = input("Введите пароль: ").strip()
    
    # Создаем переменную с открытыми портами
    open_ports = get_open_ports(ip)
    
    # Выводим информацию о подключении
    print(f"\nДанные для подключения:")
    print(f"IP: {ip}")
    print(f"Логин: {login}")
    print(f"Пароль: {password}")
    print(f"Открытые порты: {open_ports}")

    ssh_connect_and_scan(ip, login, password)

if __name__ == "__main__":
    main()