import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
from scanner.scanner import get_open_ports
from protocols.rdp_simple_handler import simple_rdp

class SimpleNetworkScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Сканер сети")
        self.root.geometry("400x300")
        
        self.ip_var = tk.StringVar()
        self.login_var = tk.StringVar()
        self.password_var = tk.StringVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Подключение к серверу", font=("Arial", 12, "bold"))
        title_label.pack(pady=10)
        
        # Поля ввода с возможностью вставки
        self.create_input_field(main_frame, "IP-адрес:", self.ip_var, 0)
        self.create_input_field(main_frame, "Логин:", self.login_var, 1)
        self.create_input_field(main_frame, "Пароль:", self.password_var, 2, show="*")
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Подключиться по RDP", 
                  command=self.connect_rdp).pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="Подключиться по SSH", 
                  command=self.connect_ssh).pack(side="left", padx=5)
        
        # Статус
        self.status_label = ttk.Label(main_frame, text="Готов к работе", relief="sunken")
        self.status_label.pack(fill=tk.X, pady=5)
        
    def create_input_field(self, parent, label, variable, row, show=None):
        """Создает поле ввода с поддержкой вставки"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(frame, text=label, width=10).pack(side="left")
        entry = ttk.Entry(frame, textvariable=variable, show=show, width=30)
        entry.pack(side="left", fill=tk.X, expand=True, padx=5)
        
        # Включаем поддержку вставки
        entry.bind("<Control-v>", self.paste_text)
        entry.bind("<Button-3>", self.show_context_menu)  # Правая кнопка мыши
        
    def paste_text(self, event):
        """Обработка вставки текста"""
        try:
            event.widget.insert(tk.INSERT, event.widget.clipboard_get())
            return "break"  # Предотвращаем стандартное поведение
        except:
            pass
            
    def show_context_menu(self, event):
        """Контекстное меню для вставки"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Вставить", command=lambda: self.paste_from_menu(event.widget))
        menu.tk_popup(event.x_root, event.y_root)
        
    def paste_from_menu(self, widget):
        """Вставка из контекстного меню"""
        try:
            widget.insert(tk.INSERT, widget.clipboard_get())
        except:
            pass
    
    def connect_rdp(self):
        ip = self.ip_var.get().strip()
        login = self.login_var.get().strip()
        password = self.password_var.get().strip()
        
        if not ip or not login or not password:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
            
        self.status_label.config(text="Подключение RDP...")
        
        try:
            success = simple_rdp(ip, login, password)
            if success:
                self.status_label.config(text="RDP подключен")
                messagebox.showinfo("Успех", "RDP подключение установлено!")
            else:
                self.status_label.config(text="Ошибка RDP")
                messagebox.showerror("Ошибка", "Не удалось подключиться по RDP")
        except Exception as e:
            self.status_label.config(text="Ошибка RDP")
            messagebox.showerror("Ошибка", f"Ошибка RDP: {e}")
    
    def connect_ssh(self):
        ip = self.ip_var.get().strip()
        login = self.login_var.get().strip()
        password = self.password_var.get().strip()
        
        if not ip or not login or not password:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
            
        self.status_label.config(text="Запуск SSH...")
        
        try:
            if sys.platform == "win32":
                # Для Windows - открываем SSH в командной строке
                subprocess.Popen(['cmd', '/k', 'ssh', f'{login}@{ip}'], shell=True)
            else:
                # Для Linux/macOS - открываем в терминале
                subprocess.Popen(['xterm', '-e', f'ssh {login}@{ip}'])
                
            self.status_label.config(text="SSH запущен")
            messagebox.showinfo("Успех", 
                              f"SSH терминал открыт!\n\n"
                              f"Пароль для входа: {password}")
                              
        except Exception as e:
            self.status_label.config(text="Ошибка SSH")
            messagebox.showerror("Ошибка", f"Не удалось запустить SSH: {e}")

def main():
    root = tk.Tk()
    app = SimpleNetworkScanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()