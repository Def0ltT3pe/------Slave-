import socket

def check_port(ip: str, port: int) -> bool:
# Проверка открытых портов
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False


def main():
# Сканирование портов
    ip = input("Введите IP-адрес для сканирования: ").strip()

    ports = [21, 22, 23, 80, 443, 3389, 5900]

#    print(f"Сканируем {ip}...")

# Сканируем и сохраняем открытые порты
    open_ports = []

    for port in ports:
        if check_port(ip, port):
            open_ports.append(port)
            print(f"Порт {port} открыт")
#       else:
#           print(f"Порт {port} закрыт")

    #print(f"\n Открытые порты: {open_ports}")

    return open_ports


if __name__ == "__main__":
    open_ports = main()