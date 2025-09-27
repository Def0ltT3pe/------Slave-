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