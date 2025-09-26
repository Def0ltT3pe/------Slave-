from scanner.scanner import get_open_ports
from protocols.ssh_handler import ssh_connect_and_scan
from protocols.rdp_simple_handler import simple_rdp

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

    if 3389 in open_ports:
        print("\nЗапускаем RDP подключение...")
        if simple_rdp(ip, login, password):
            print("RDP запущен!")
        else:
            print("Ошибка RDP")
    elif 22 in open_ports:
        print("\nЗапускаем SSH подключение...")
        from protocols.ssh_handler import ssh_connect_and_scan
        ssh_connect_and_scan(ip, login, password)
    else:
        print("\nНет доступных протоколов")

if __name__ == "__main__":
    main()