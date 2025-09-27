import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import sys
import time
import os
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
        
        self.setup_ui()
        
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Сканер сети и подключение", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Поля ввода с поддержкой вставки
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="IP-адрес:").grid(row=0, column=0, sticky="w", pady=2)
        self.ip_entry = ttk.Entry(input_frame, textvariable=self.ip_var, width=30)
        self.ip_entry.grid(row=0, column=1, sticky="ew", pady=2, padx=5)
        self._enable_paste(self.ip_entry)
        
        ttk.Label(input_frame, text="Логин:").grid(row=1, column=0, sticky="w", pady=2)
        self.login_entry = ttk.Entry(input_frame, textvariable=self.login_var, width=30)
        self.login_entry.grid(row=1, column=1, sticky="ew", pady=2, padx=5)
        self._enable_paste(self.login_entry)
        
        ttk.Label(input_frame, text="Пароль:").grid(row=2, column=0, sticky="w", pady=2)
        self.password_entry = ttk.Entry(input_frame, textvariable=self.password_var, show="*", width=30)
        self.password_entry.grid(row=2, column=1, sticky="ew", pady=2, padx=5)
        self._enable_paste(self.password_entry)
        
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
    
    def _enable_paste(self, widget):
        """Включает поддержку вставки для поля ввода"""
        # Удаляем возможные конфликтующие привязки
        widget.bind("<Control-v>", lambda e: "break")
        widget.bind("<Command-v>", lambda e: "break")  # Для Mac
        widget.bind("<Button-3>", self._show_context_menu)  # Правая кнопка мыши
        
        # Добавляем правильные привязки
        widget.bind("<Control-v>", self._paste_text)
        widget.bind("<Command-v>", self._paste_text)  # Для Mac
        
    def _paste_text(self, event):
        """Обработка вставки текста Ctrl+V"""
        try:
            # Вставляем текст из буфера обмена
            widget = event.widget
            text = widget.clipboard_get()
            if text:
                widget.insert(tk.INSERT, text)
            return "break"  # Предотвращаем стандартное поведение
        except Exception as e:
            print(f"Ошибка вставки: {e}")
            return "break"
            
    def _show_context_menu(self, event):
        """Контекстное меню по правой кнопке мыши"""
        try:
            widget = event.widget
            menu = tk.Menu(self.root, tearoff=0)
            
            menu.add_command(label="Вырезать", command=lambda: self._cut_text(widget))
            menu.add_command(label="Копировать", command=lambda: self._copy_text(widget))
            menu.add_command(label="Вставить", command=lambda: self._paste_from_menu(widget))
            
            menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            print(f"Ошибка меню: {e}")
            
    def _cut_text(self, widget):
        """Вырезать текст"""
        try:
            widget.event_generate("<<Cut>>")
        except:
            pass
            
    def _copy_text(self, widget):
        """Копировать текст"""
        try:
            widget.event_generate("<<Copy>>")
        except:
            pass
            
    def _paste_from_menu(self, widget):
        """Вставить текст из меню"""
        try:
            text = widget.clipboard_get()
            if text:
                widget.insert(tk.INSERT, text)
        except Exception as e:
            print(f"Ошибка вставки из меню: {e}")
        
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
        
        login = self.login_var.get().strip()
        password = self.password_var.get().strip()
        
        self.result_text.insert(tk.END, "Данные для подключения:\n")
        self.result_text.insert(tk.END, f"IP: {ip}\n")
        self.result_text.insert(tk.END, f"Логин: {login}\n")
        self.result_text.insert(tk.END, f"Пароль: {'*' * len(password)}\n\n")
        
        # Проверяем доступные протоколы
        rdp_available = 3389 in open_ports
        ssh_available = 22 in open_ports
        
        if rdp_available:
            self.result_text.insert(tk.END, "✓ Доступен RDP (порт 3389)\n")
        if ssh_available:
            self.result_text.insert(tk.END, "✓ Доступен SSH (порт 22)\n")
            
        if not rdp_available and not ssh_available:
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
        # Приоритет у RDP, если доступны оба протокола
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
        
        thread = threading.Thread(target=self._rdp_connect, args=(ip, login, password))
        thread.daemon = True
        thread.start()
        
    def _rdp_connect(self, ip, login, password):
        try:
            success = simple_rdp(ip, login, password)
            self.root.after(0, self._rdp_result, success)
        except Exception as e:
            self.root.after(0, self._connect_error, "RDP", str(e))
            
    def _rdp_result(self, success):
        if success:
            self.status_var.set("RDP подключен")
            messagebox.showinfo("Успех", "RDP подключение установлено!")
        else:
            self.status_var.set("Ошибка RDP")
            messagebox.showerror("Ошибка", "Не удалось подключиться по RDP")
            
    def connect_ssh(self):
        ip = self.ip_var.get().strip()
        login = self.login_var.get().strip()
        password = self.password_var.get().strip()
        
        if not all([ip, login, password]):
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
            
        self.status_var.set("Запуск SSH...")
        
        thread = threading.Thread(target=self._ssh_connect, args=(ip, login, password))
        thread.daemon = True
        thread.start()
        
    def _ssh_connect(self, ip, login, password):
        try:
            if sys.platform == "win32":
                self._ssh_windows(ip, login, password)
            else:
                self._ssh_linux(ip, login, password)
                
        except Exception as e:
            self.root.after(0, self._connect_error, "SSH", str(e))
            
    def _ssh_windows(self, ip, login, password):
        """SSH для Windows с автоматическим вводом пароля"""
        try:
            # Создаем BAT файл который откроет SSH и введет пароль
            bat_content = f'''@echo off
chcp 65001 > nul
echo Запуск SSH подключения...
echo Логин: {login}@{ip}
echo.
ssh {login}@{ip}
echo.
echo Сессия завершена. Нажмите любую клавишу...
pause
'''
            
            # Сохраняем во временный файл
            with open("ssh_connection.bat", "w", encoding="utf-8") as f:
                f.write(bat_content)
            
            # Запускаем SSH в отдельном окне
            subprocess.Popen(['cmd', '/c', 'start', 'ssh_connection.bat'], shell=True)
            
            # Даем время окну открыться
            time.sleep(3)
            
            # Автоматически вводим пароль
            self._auto_type_password(password)
            
            self.root.after(0, self._ssh_success)
            
        except Exception as e:
            # Резервный способ
            self._ssh_windows_fallback(ip, login, password)
            
    def _auto_type_password(self, password):
        """Автоматический ввод пароля с помощью PowerShell"""
        try:
            ps_script = f'''
Add-Type -AssemblyName System.Windows.Forms
Start-Sleep 2
[System.Windows.Forms.SendKeys]::SendWait("{password}")
Start-Sleep 0.5
[System.Windows.Forms.SendKeys]::SendWait("{{ENTER}}")
'''
            subprocess.Popen(['powershell', '-Command', ps_script], shell=True)
        except:
            pass
            
    def _ssh_windows_fallback(self, ip, login, password):
        """Резервный способ для Windows"""
        try:
            subprocess.Popen(['cmd', '/c', 'start', 'ssh', f'{login}@{ip}'], shell=True)
            self.root.after(0, self._ssh_success_with_password, password)
        except:
            self.root.after(0, self._connect_error, "SSH", "Не удалось запустить SSH")
            
    def _ssh_linux(self, ip, login, password):
        """SSH для Linux/macOS"""
        try:
            # Пробуем разные терминалы
            command = f'ssh {login}@{ip}'
            
            terminals = [
                ['gnome-terminal', '--', 'bash', '-c', f'{command}; exec bash'],
                ['konsole', '-e', command],
                ['xterm', '-e', command],
                ['terminator', '-e', command]
            ]
            
            for terminal_cmd in terminals:
                try:
                    subprocess.Popen(terminal_cmd)
                    break
                except:
                    continue
            else:
                subprocess.Popen(['xterm', '-e', command])
                
            self.root.after(0, self._ssh_success_with_password, password)
            
        except Exception as e:
            self.root.after(0, self._connect_error, "SSH", str(e))
            
    def _ssh_success(self):
        """Успешный запуск SSH с автовводом"""
        self.status_var.set("SSH запущен")
        messagebox.showinfo("Успех", "SSH терминал запущен!\nПароль введен автоматически.")
        
    def _ssh_success_with_password(self, password):
        """Успешный запуск SSH (ручной ввод пароля)"""
        self.status_var.set("SSH запущен")
        messagebox.showinfo("SSH запущен", 
                          f"SSH терминал открыт!\n\n"
                          f"Когда появится запрос пароля, введите:\n{password}")
        
    def _connect_error(self, protocol, error):
        self.status_var.set(f"Ошибка {protocol}")
        messagebox.showerror("Ошибка", f"Ошибка {protocol}: {error}")

def main():
    root = tk.Tk()
    app = NetworkScanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()