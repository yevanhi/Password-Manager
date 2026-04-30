#!/usr/bin/env python3
"""
Password Manager - Графическое приложение для управления паролями
Автор: Иван Иванов
Версия: 2.0.0
"""

import json
import random
import string
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from typing import List, Optional


class PasswordRecord:
    """Модель записи пароля"""
    
    def __init__(self, service: str, username: str, password: str, created_at: Optional[str] = None):
        self._service = service
        self._username = username
        self._password = password
        self._created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @property
    def service(self) -> str:
        return self._service
    
    @service.setter
    def service(self, value: str):
        if not value or not value.strip():
            raise ValueError("Service name cannot be empty")
        self._service = value.strip()
    
    @property
    def username(self) -> str:
        return self._username
    
    @username.setter
    def username(self, value: str):
        if not value or not value.strip():
            raise ValueError("Username cannot be empty")
        self._username = value.strip()
    
    @property
    def password(self) -> str:
        return self._password
    
    @password.setter
    def password(self, value: str):
        if not value or not value.strip():
            raise ValueError("Password cannot be empty")
        self._password = value
    
    @property
    def created_at(self) -> str:
        return self._created_at
    
    def to_dict(self) -> dict:
        return {
            "service": self._service,
            "username": self._username,
            "password": self._password,
            "created_at": self._created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PasswordRecord':
        return cls(
            service=data["service"],
            username=data["username"],
            password=data["password"],
            created_at=data.get("created_at")
        )


class PasswordStorage:
    """Класс для работы с хранилищем паролей"""
    
    def __init__(self, filename: str = "data.json"):
        self._filename = filename
        self._records: List[PasswordRecord] = []
        self.load()
    
    def add(self, record: PasswordRecord) -> None:
        self._records.append(record)
        self.save()
    
    def remove(self, index: int) -> bool:
        if 0 <= index < len(self._records):
            del self._records[index]
            self.save()
            return True
        return False
    
    def update(self, index: int, record: PasswordRecord) -> bool:
        if 0 <= index < len(self._records):
            self._records[index] = record
            self.save()
            return True
        return False
    
    def get_all(self) -> List[PasswordRecord]:
        return self._records.copy()
    
    def get(self, index: int) -> Optional[PasswordRecord]:
        if 0 <= index < len(self._records):
            return self._records[index]
        return None
    
    def save(self) -> None:
        data = [record.to_dict() for record in self._records]
        with open(self._filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self) -> None:
        try:
            with open(self._filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._records = [PasswordRecord.from_dict(item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self._records = []
    
    def __len__(self) -> int:
        return len(self._records)


class PasswordGenerator:
    """Класс для генерации паролей"""
    
    @staticmethod
    def generate(length: int = 12, use_uppercase: bool = True, 
                use_lowercase: bool = True, use_digits: bool = True, 
                use_symbols: bool = True) -> str:
        
        characters = ""
        
        if use_uppercase:
            characters += string.ascii_uppercase
        if use_lowercase:
            characters += string.ascii_lowercase
        if use_digits:
            characters += string.digits
        if use_symbols:
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        if not characters:
            characters = string.ascii_letters
        
        password_chars = []
        
        if use_uppercase:
            password_chars.append(random.choice(string.ascii_uppercase))
        if use_lowercase:
            password_chars.append(random.choice(string.ascii_lowercase))
        if use_digits:
            password_chars.append(random.choice(string.digits))
        if use_symbols:
            password_chars.append(random.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))
        
        remaining_length = length - len(password_chars)
        if remaining_length > 0:
            password_chars.extend(random.choice(characters) for _ in range(remaining_length))
        
        random.shuffle(password_chars)
        return ''.join(password_chars)


class PasswordManagerApp:
    """Главное окно приложения"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Инициализация хранилища
        self.storage = PasswordStorage()
        self.generator = PasswordGenerator()
        
        # Настройка стилей
        self.setup_styles()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка данных
        self.refresh_table()
    
    def setup_styles(self):
        """Настройка стилей интерфейса"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настройка цветов
        self.root.configure(bg='#2b2b2b')
        style.configure('TLabel', background='#2b2b2b', foreground='white')
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TLabelframe', background='#2b2b2b', foreground='white')
        style.configure('TLabelframe.Label', background='#2b2b2b', foreground='white')
        style.configure('TButton', background='#3c3c3c', foreground='white', padding=5)
        style.map('TButton', background=[('active', '#4c4c4c')])
        style.configure('Treeview', background='#3c3c3c', foreground='white', 
                       fieldbackground='#3c3c3c', rowheight=25)
        style.configure('Treeview.Heading', background='#4c4c4c', foreground='white')
        style.map('Treeview', background=[('selected', '#0078d4')])
    
    def create_widgets(self):
        """Создание всех UI элементов"""
        
        # Верхняя панель с кнопками
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(top_frame, text="➕ Добавить", command=self.add_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="✏️ Редактировать", command=self.edit_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="🗑️ Удалить", command=self.delete_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="🔐 Показать пароль", command=self.show_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="🎲 Генератор паролей", command=self.open_generator).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="🔄 Обновить", command=self.refresh_table).pack(side=tk.LEFT, padx=5)
        
        # Таблица с записями
        columns = ('service', 'username', 'created_at')
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings', height=20)
        
        # Настройка колонок
        self.tree.heading('service', text='Сервис')
        self.tree.heading('username', text='Имя пользователя')
        self.tree.heading('created_at', text='Дата создания')
        
        self.tree.column('service', width=250)
        self.tree.column('username', width=250)
        self.tree.column('created_at', width=200)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=(0, 10))
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
    
    def refresh_table(self):
        """Обновление таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Загрузка данных
        records = self.storage.get_all()
        for record in records:
            self.tree.insert('', tk.END, values=(record.service, record.username, record.created_at))
        
        self.status_var.set(f"Загружено записей: {len(records)}")
    
    def get_selected_record(self):
        """Получение выбранной записи"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите запись")
            return None, None
        
        index = self.tree.index(selection[0])
        record = self.storage.get(index)
        return index, record
    
    def add_record(self):
        """Добавление новой записи"""
        dialog = AddEditDialog(self.root, self.generator)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                record = PasswordRecord(
                    dialog.result['service'],
                    dialog.result['username'],
                    dialog.result['password']
                )
                self.storage.add(record)
                self.refresh_table()
                messagebox.showinfo("Успех", f"Запись для сервиса '{dialog.result['service']}' добавлена!")
            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))
    
    def edit_record(self):
        """Редактирование записи"""
        index, record = self.get_selected_record()
        if record is None:
            return
        
        dialog = AddEditDialog(self.root, self.generator, record)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                updated_record = PasswordRecord(
                    dialog.result['service'],
                    dialog.result['username'],
                    dialog.result['password'],
                    record.created_at
                )
                self.storage.update(index, updated_record)
                self.refresh_table()
                messagebox.showinfo("Успех", "Запись обновлена!")
            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))
    
    def delete_record(self):
        """Удаление записи"""
        index, record = self.get_selected_record()
        if record is None:
            return
        
        if messagebox.askyesno("Подтверждение", f"Удалить запись для сервиса '{record.service}'?"):
            self.storage.remove(index)
            self.refresh_table()
            messagebox.showinfo("Успех", "Запись удалена!")
    
    def show_password(self):
        """Показ пароля выбранной записи"""
        index, record = self.get_selected_record()
        if record is None:
            return
        
        messagebox.showinfo("Пароль", 
            f"Сервис: {record.service}\n"
            f"Логин: {record.username}\n"
            f"Пароль: {record.password}",
            parent=self.root)
    
    def open_generator(self):
        """Открытие окна генератора паролей"""
        GeneratorDialog(self.root, self.generator)


class AddEditDialog:
    """Диалоговое окно для добавления/редактирования записи"""
    
    def __init__(self, parent, generator, record=None):
        self.parent = parent
        self.generator = generator
        self.record = record
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавить/Редактировать запись" if not record else "Редактировать запись")
        self.dialog.geometry("500x450")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg='#2b2b2b')
        
        self.create_widgets()
        
        if record:
            self.load_record_data()
    
    def create_widgets(self):
        """Создание элементов диалога"""
        # Основной фрейм
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Поле Сервис
        ttk.Label(main_frame, text="Название сервиса:*").pack(anchor=tk.W, pady=(0, 5))
        self.service_entry = ttk.Entry(main_frame, width=50)
        self.service_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Поле Имя пользователя
        ttk.Label(main_frame, text="Имя пользователя/логин:*").pack(anchor=tk.W, pady=(0, 5))
        self.username_entry = ttk.Entry(main_frame, width=50)
        self.username_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Поле Пароль с кнопкой генерации
        ttk.Label(main_frame, text="Пароль:*").pack(anchor=tk.W, pady=(0, 5))
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.password_entry = ttk.Entry(password_frame, width=40, show="*")
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(password_frame, text="🎲", width=3, 
                  command=self.generate_password).pack(side=tk.LEFT, padx=(5, 0))
        
        # Чекбокс для показа пароля
        self.show_password_var = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Показать пароль", 
                       variable=self.show_password_var,
                       command=self.toggle_password_visibility).pack(anchor=tk.W, pady=(0, 15))
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.cancel).pack(side=tk.LEFT, padx=5)
    
    def load_record_data(self):
        """Загрузка данных для редактирования"""
        self.service_entry.insert(0, self.record.service)
        self.username_entry.insert(0, self.record.username)
        self.password_entry.insert(0, self.record.password)
    
    def generate_password(self):
        """Открытие окна генерации пароля"""
        dialog = GeneratorDialog(self.dialog, self.generator, for_record=True)
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.generated_password:
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, dialog.generated_password)
    
    def toggle_password_visibility(self):
        """Переключение видимости пароля"""
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
    
    def save(self):
        """Сохранение записи"""
        service = self.service_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not service:
            messagebox.showerror("Ошибка", "Название сервиса не может быть пустым")
            return
        
        if not username:
            messagebox.showerror("Ошибка", "Имя пользователя не может быть пустым")
            return
        
        if not password:
            messagebox.showerror("Ошибка", "Пароль не может быть пустым")
            return
        
        self.result = {
            'service': service,
            'username': username,
            'password': password
        }
        self.dialog.destroy()
    
    def cancel(self):
        """Отмена"""
        self.dialog.destroy()


class GeneratorDialog:
    """Диалоговое окно генератора паролей"""
    
    def __init__(self, parent, generator, for_record=False):
        self.parent = parent
        self.generator = generator
        self.for_record = for_record
        self.generated_password = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Генератор паролей")
        self.dialog.geometry("450x500")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg='#2b2b2b')
        
        self.create_widgets()
    
    def create_widgets(self):
        """Создание элементов диалога"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Длина пароля
        ttk.Label(main_frame, text="Длина пароля (8-32):").pack(anchor=tk.W, pady=(0, 5))
        self.length_var = tk.IntVar(value=12)
        length_scale = ttk.Scale(main_frame, from_=8, to=32, variable=self.length_var,
                                 orient=tk.HORIZONTAL, command=self.update_length_label)
        length_scale.pack(fill=tk.X, pady=(0, 5))
        
        self.length_label = ttk.Label(main_frame, text="12")
        self.length_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Чекбоксы для типов символов
        self.use_uppercase = tk.BooleanVar(value=True)
        self.use_lowercase = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(main_frame, text="Заглавные буквы (A-Z)", 
                       variable=self.use_uppercase).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(main_frame, text="Строчные буквы (a-z)", 
                       variable=self.use_lowercase).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(main_frame, text="Цифры (0-9)", 
                       variable=self.use_digits).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(main_frame, text="Спецсимволы (!@#$%^&*)", 
                       variable=self.use_symbols).pack(anchor=tk.W, pady=2)
        
        # Кнопка генерации
        ttk.Button(main_frame, text="Сгенерировать пароль", 
                  command=self.generate).pack(pady=(20, 10))
        
        # Поле для отображения пароля
        ttk.Label(main_frame, text="Сгенерированный пароль:").pack(anchor=tk.W, pady=(10, 5))
        self.password_text = tk.Text(main_frame, height=3, wrap=tk.WORD, bg='#3c3c3c', 
                                     fg='white', insertbackground='white')
        self.password_text.pack(fill=tk.X, pady=(0, 15))
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        if not self.for_record:
            ttk.Button(button_frame, text="Копировать", 
                      command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Закрыть", 
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Генерация первого пароля
        self.generate()
    
    def update_length_label(self, value):
        """Обновление метки длины"""
        self.length_label.config(text=str(int(float(value))))
    
    def generate(self):
        """Генерация пароля"""
        length = self.length_var.get()
        use_uppercase = self.use_uppercase.get()
        use_lowercase = self.use_lowercase.get()
        use_digits = self.use_digits.get()
        use_symbols = self.use_symbols.get()
        
        if not (use_uppercase or use_lowercase or use_digits or use_symbols):
            messagebox.showwarning("Предупреждение", "Выберите хотя бы один тип символов!")
            return
        
        password = self.generator.generate(length, use_uppercase, use_lowercase, use_digits, use_symbols)
        
        self.password_text.delete(1.0, tk.END)
        self.password_text.insert(1.0, password)
        
        if self.for_record:
            self.generated_password = password
    
    def copy_to_clipboard(self):
        """Копирование пароля в буфер обмена"""
        password = self.password_text.get(1.0, tk.END).strip()
        if password:
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")


def main():
    """Главная функция"""
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()