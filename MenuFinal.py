import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import paramiko
from scanner.scanner import get_open_ports
from protocols.rdp_simple_handler import simple_rdp

class NetworkScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Сканер сети и подключение")
        self.root.geometry("600x500")
        
        self.ip_var = tk.StringVar()
        self.login_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.open_ports = []
        self.ssh_client = None
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="Сканер сети и подключение", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Поля ввода
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="IP-адрес:").grid(row=0, column=0, sticky="w", pady=2)
        self.ip_entry = ttk.Entry(input_frame, textvariable=self.ip_var, width=30)
        self.ip_entry.grid(row=0, column=1, sticky="ew", pady=2, padx=5)
        
        ttk.Label(input_frame, text="Логин:").grid(row=1, column=0, sticky="w", pady=2)
        self.login_entry = ttk.Entry(input_frame, textvariable=self.login_var, width=30)
        self.login_entry.grid(row=1, column=1, sticky="ew", pady=2, padx=5)
        
        ttk.Label(input_frame, text="Пароль:").grid(row=2, column=0, sticky="w", pady=2)
        self.password_entry = ttk.Entry(input_frame, textvariable=self.password_var, show="*", width=30)
        self.password_entry.grid(row=2, column=1, sticky="ew", pady=2, padx=5)
        
        input_frame.columnconfigure(1, weight=1)
        
        # Кнопка сканирования
        self.scan_button = ttk.Button(main_frame, text="Сканировать порты", command=self.start_scanning)
        self.scan_button.pack(pady=10)
        
        # Область результатов
        self.result_text = scrolledtext.ScrolledText(main_frame, height=8)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Кнопки подключения
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.rdp_button = ttk.Button(button_frame, text="Подключиться по RDP", 
                                   command=self.connect_rdp, state="disabled")
        self.rdp_button.pack(side="left", padx=5)
        
        self.ssh_button = ttk.Button(button_frame, text="Подключиться по SSH", 
                                   command=self.connect_ssh, state="disabled")
        self.ssh_button.pack(side="left", padx=5)
        
        # Статус
        self.status_var = tk.StringVar(value="Готов к работе")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, relief="sunken")
        status_label.pack(fill=tk.X, pady=5)
        
    def start_scanning(self):
        ip = self.ip_var.get().strip()
        if not ip:
            messagebox.showerror("Ошибка", "Введите IP-адрес")
            return
            
        self.status_var.set("Сканирование портов...")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Сканируем {ip}...\n")
        self.scan_button.config(state="disabled")
        
        thread = threading.Thread(target=self.scan_ports, args=(ip,))
        thread.daemon = True
        thread.start()
        
    def scan_ports(self, ip):
        try:
            open_ports = get_open_ports(ip)
            self.open_ports = open_ports
            self.root.after(0, self.show_results, ip, open_ports)
        except Exception as e:
            self.root.after(0, self.scan_error, str(e))
            
    def show_results(self, ip, open_ports):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Результаты сканирования {ip}:\n")
        self.result_text.insert(tk.END, f"Открытые порты: {open_ports}\n\n")
        
        # Проверяем доступные протоколы
        if 3389 in open_ports:
            self.result_text.insert(tk.END, "✓ Доступен RDP (порт 3389)\n")
        if 22 in open_ports:
            self.result_text.insert(tk.END, "✓ Доступен SSH (порт 22)\n")
            
        if not (3389 in open_ports or 22 in open_ports):
            self.result_text.insert(tk.END, "✗ Нет доступных протоколов\n")
            
        self.status_var.set("Сканирование завершено")
        self.scan_button.config(state="normal")
        self.update_buttons()
        
    def scan_error(self, error):
        self.result_text.insert(tk.END, f"Ошибка сканирования: {error}\n")
        self.status_var.set("Ошибка сканирования")
        self.scan_button.config(state="normal")
        messagebox.showerror("Ошибка", f"Не удалось просканировать порты: {error}")
        
    def update_buttons(self):
        if 3389 in self.open_ports:
            self.rdp_button.config(state="normal")
            self.ssh_button.config(state="normal")
        elif 22 in self.open_ports:
            self.rdp_button.config(state="disabled")
            self.ssh_button.config(state="normal")
        else:
            self.rdp_button.config(state="disabled")
            self.ssh_button.config(state="disabled")
            
    def connect_rdp(self):
        ip = self.ip_var.get().strip()
        login = self.login_var.get().strip()
        password = self.password_var.get().strip()
        
        if not all([ip, login, password]):
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
            
        self.status_var.set("Подключение RDP...")
        
        try:
            success = simple_rdp(ip, login, password)
            if success:
                self.status_var.set("RDP подключен")
                messagebox.showinfo("Успех", "RDP подключение установлено!")
            else:
                self.status_var.set("Ошибка RDP")
                messagebox.showerror("Ошибка", "Не удалось подключиться по RDP")
        except Exception as e:
            self.status_var.set("Ошибка RDP")
            messagebox.showerror("Ошибка", f"Ошибка RDP: {e}")
            
    def connect_ssh(self):
        ip = self.ip_var.get().strip()
        login = self.login_var.get().strip()
        password = self.password_var.get().strip()
        
        if not all([ip, login, password]):
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
            
        self.status_var.set("Подключение SSH...")
        self.create_ssh_window(ip, login, password)
        
    def create_ssh_window(self, ip, login, password):
        ssh_window = tk.Toplevel(self.root)
        ssh_window.title(f"SSH сессия - {login}@{ip}")
        ssh_window.geometry("700x500")
        
        main_frame = ttk.Frame(ssh_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text=f"SSH сессия: {login}@{ip}", font=("Arial", 12, "bold"))
        title_label.pack(pady=5)
        
        # Терминал
        self.ssh_text = scrolledtext.ScrolledText(main_frame, font=("Courier New", 10))
        self.ssh_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Поле для ввода команд
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text="Команда:").pack(side=tk.LEFT)
        self.command_var = tk.StringVar()
        command_entry = ttk.Entry(input_frame, textvariable=self.command_var, width=40)
        command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        command_entry.bind('<Return>', lambda e: self.send_ssh_command())
        
        ttk.Button(input_frame, text="Отправить", command=self.send_ssh_command).pack(side=tk.RIGHT)
        
        # Запускаем SSH сессию
        self.ssh_output(f"Подключаемся к {login}@{ip}...\n")
        thread = threading.Thread(target=self.start_ssh_session, args=(ip, login, password))
        thread.daemon = True
        thread.start()
        
        command_entry.focus_set()
        self.ssh_window = ssh_window
    
    def start_ssh_session(self, ip, login, password):
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(ip, username=login, password=password, port=22, timeout=10)
            
            self.ssh_output("✓ SSH соединение установлено!\n\n")
            
            # Базовые команды при подключении
            commands = ["uname -a", "whoami", "pwd"]
            for cmd in commands:
                result = self.execute_ssh_command(cmd)
                self.ssh_output(f"$ {cmd}\n{result}\n")
            
            self.ssh_output("Готов к работе. Вводите команды...\n")
            
        except Exception as e:
            self.ssh_output(f"✗ Ошибка подключения: {str(e)}\n")
            self.ssh_client = None
    
    def execute_ssh_command(self, command):
        if not self.ssh_client:
            return "Соединение не установлено"
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            return output if output else error
        except Exception as e:
            return f"Ошибка выполнения: {str(e)}"
    
    def send_ssh_command(self):
        if not self.ssh_client:
            self.ssh_output("Соединение не установлено\n")
            return
            
        command = self.command_var.get().strip()
        if command:
            self.ssh_output(f"$ {command}\n")
            self.command_var.set("")
            
            thread = threading.Thread(target=self._execute_command, args=(command,))
            thread.daemon = True
            thread.start()
    
    def _execute_command(self, command):
        result = self.execute_ssh_command(command)
        self.root.after(0, lambda: self.ssh_output(f"{result}\n"))
    
    def ssh_output(self, text):
        self.ssh_text.insert(tk.END, text)
        self.ssh_text.see(tk.END)

def main():
    root = tk.Tk()
    app = NetworkScanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()