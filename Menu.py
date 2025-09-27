import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from scanner.scanner import get_open_ports
from protocols.ssh_simple_handler import ssh_connect
from protocols.rdp_simple_handler import simple_rdp

class NetworkScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Сканер сети и подключение")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Переменные для хранения данных
        self.ip_var = tk.StringVar()
        self.login_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.open_ports = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # Создаем основную рамку с отступами
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов для адаптивности
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Сканер сети и подключение", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Поле для ввода IP-адреса
        ttk.Label(main_frame, text="IP-адрес:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ip_entry = ttk.Entry(main_frame, textvariable=self.ip_var, width=30)
        ip_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Поле для логина
        ttk.Label(main_frame, text="Логин:").grid(row=2, column=0, sticky=tk.W, pady=5)
        login_entry = ttk.Entry(main_frame, textvariable=self.login_var, width=30)
        login_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Поле для пароля
        ttk.Label(main_frame, text="Пароль:").grid(row=3, column=0, sticky=tk.W, pady=5)
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var, 
                                  show="*", width=30)
        password_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Кнопка сканирования
        scan_button = ttk.Button(main_frame, text="Сканировать порты", 
                                command=self.start_scanning)
        scan_button.grid(row=4, column=0, columnspan=2, pady=15)
        
        # Область для вывода результатов
        ttk.Label(main_frame, text="Результаты сканирования:").grid(row=5, column=0, 
                                                                   sticky=tk.W, pady=(10, 5))
        
        self.result_text = scrolledtext.ScrolledText(main_frame, height=10, width=50)
        self.result_text.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), 
                             pady=(0, 10))
        
        # Фрейм для кнопок подключения
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Кнопки подключения
        self.rdp_button = ttk.Button(button_frame, text="Подключиться по RDP", 
                                    command=self.connect_rdp, state="disabled")
        self.rdp_button.grid(row=0, column=0, padx=5)
        
        self.ssh_button = ttk.Button(button_frame, text="Подключиться по SSH", 
                                    command=self.connect_ssh, state="disabled")
        self.ssh_button.grid(row=0, column=1, padx=5)
        
        # Прогресс-бар
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Настройка весов строк для адаптивности
        main_frame.rowconfigure(6, weight=1)
        
    def start_scanning(self):
        """Запуск сканирования в отдельном потоке"""
        ip = self.ip_var.get().strip()
        login = self.login_var.get().strip()
        password = self.password_var.get().strip()
        
        if not ip:
            messagebox.showerror("Ошибка", "Введите IP-адрес для сканирования")
            return
            
        # Очистка предыдущих результатов
        self.result_text.delete(1.0, tk.END)
        self.open_ports = []
        self.update_connection_buttons()
        
        # Запуск сканирования в отдельном потоке
        self.status_var.set("Сканирование портов...")
        self.progress.start()
        self.disable_inputs()
        
        thread = threading.Thread(target=self.scan_ports, args=(ip, login, password))
        thread.daemon = True
        thread.start()
        
    def scan_ports(self, ip, login, password):
        """Сканирование портов в фоновом потоке"""
        try:
            open_ports = get_open_ports(ip)
            self.open_ports = open_ports
            
            # Обновление UI в основном потоке
            self.root.after(0, self.update_results, ip, login, password, open_ports)
            
        except Exception as e:
            self.root.after(0, self.scanning_error, str(e))
            
    def update_results(self, ip, login, password, open_ports):
        """Обновление результатов сканирования в UI"""
        self.progress.stop()
        self.enable_inputs()
        
        # Вывод результатов в текстовое поле
        self.result_text.insert(tk.END, f"Результаты сканирования {ip}:\n")
        self.result_text.insert(tk.END, f"Открытые порты: {open_ports}\n\n")
        
        self.result_text.insert(tk.END, "Данные для подключения:\n")
        self.result_text.insert(tk.END, f"IP: {ip}\n")
        self.result_text.insert(tk.END, f"Логин: {login}\n")
        self.result_text.insert(tk.END, f"Пароль: {'*' * len(password)}\n\n")
        
        # Анализ доступных протоколов
        if 3389 in open_ports:
            self.result_text.insert(tk.END, "✓ Доступен RDP (порт 3389)\n")
        if 22 in open_ports:
            self.result_text.insert(tk.END, "✓ Доступен SSH (порт 22)\n")
            
        if not (3389 in open_ports or 22 in open_ports):
            self.result_text.insert(tk.END, "✗ Нет доступных протоколов\n")
        
        self.status_var.set("Сканирование завершено")
        self.update_connection_buttons()
        
    def scanning_error(self, error_message):
        """Обработка ошибок сканирования"""
        self.progress.stop()
        self.enable_inputs()
        self.status_var.set("Ошибка сканирования")
        
        self.result_text.insert(tk.END, f"Ошибка при сканировании: {error_message}\n")
        messagebox.showerror("Ошибка", f"Не удалось выполнить сканирование:\n{error_message}")
        
    def update_connection_buttons(self):
        """Обновление состояния кнопок подключения"""
        if 3389 in self.open_ports:
            self.rdp_button.config(state="normal")
        else:
            self.rdp_button.config(state="disabled")
            
        if 22 in self.open_ports:
            self.ssh_button.config(state="normal")
        else:
            self.ssh_button.config(state="disabled")
            
    def connect_rdp(self):
        """Подключение по RDP"""
        ip = self.ip_var.get().strip()
        login = self.login_var.get().strip()
        password = self.password_var.get().strip()
        
        if not all([ip, login, password]):
            messagebox.showerror("Ошибка", "Заполните все поля для подключения")
            return
            
        self.status_var.set("Подключение по RDP...")
        
        # Запуск в отдельном потоке
        thread = threading.Thread(target=self._rdp_connection, args=(ip, login, password))
        thread.daemon = True
        thread.start()
        
    def _rdp_connection(self, ip, login, password):
        """RDP подключение в фоновом потоке"""
        try:
            success = simple_rdp(ip, login, password)
            self.root.after(0, self._connection_result, "RDP", success)
        except Exception as e:
            self.root.after(0, self._connection_error, "RDP", str(e))
            
    def connect_ssh(self):
        """Подключение по SSH"""
        ip = self.ip_var.get().strip()
        login = self.login_var.get().strip()
        password = self.password_var.get().strip()
        
        if not all([ip, login, password]):
            messagebox.showerror("Ошибка", "Заполните все поля для подключения")
            return
            
        self.status_var.set("Подключение по SSH...")
        
        # Запуск в отдельном потоке
        thread = threading.Thread(target=self._ssh_connection, args=(ip, login, password))
        thread.daemon = True
        thread.start()
        
    def _ssh_connection(self, ip, login, password):
        """SSH подключение в фоновом потоке"""
        try:
            ssh_connect(ip, login, password)
            self.root.after(0, self._connection_result, "SSH", True)
        except Exception as e:
            self.root.after(0, self._connection_error, "SSH", str(e))
            
    def _connection_result(self, protocol, success):
        """Обработка результата подключения"""
        if success:
            self.status_var.set(f"{protocol} подключение установлено")
            messagebox.showinfo("Успех", f"{protocol} подключение успешно установлено!")
        else:
            self.status_var.set(f"Ошибка {protocol} подключения")
            messagebox.showerror("Ошибка", f"Не удалось установить {protocol} подключение")
            
    def _connection_error(self, protocol, error_message):
        """Обработка ошибки подключения"""
        self.status_var.set(f"Ошибка {protocol} подключения")
        messagebox.showerror("Ошибка", 
                           f"Ошибка при {protocol} подключении:\n{error_message}")
        
    def disable_inputs(self):
        """Отключение элементов ввода во время сканирования"""
        for widget in self.root.winfo_children():
            if isinstance(widget, (ttk.Entry, ttk.Button)):
                widget.config(state="disabled")
                
    def enable_inputs(self):
        """Включение элементов ввода после сканирования"""
        for widget in self.root.winfo_children():
            if isinstance(widget, (ttk.Entry, ttk.Button)):
                widget.config(state="normal")
        self.update_connection_buttons()

def main():
    root = tk.Tk()
    app = NetworkScannerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()