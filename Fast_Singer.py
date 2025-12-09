import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import time
import random
from datetime import datetime
import os

class PitchTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("Fast Singer - Тренажер чтения текста песни")
        self.root.geometry("1100x800")
        
        # Темная цветовая схема
        self.colors = {
            'bg': '#2c3e50',
            'fg': '#ecf0f1',
            'accent1': '#e74c3c',  # Красный
            'accent2': '#f39c12',  # Оранжевый
            'accent3': '#27ae60',  # Зеленый
            'accent4': '#3498db',  # Синий
            'card_bg': '#34495e',
            'list_bg': '#1c2833',
            'text_bg': '#1a252f',
            'border': '#7f8c8d'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Данные приложения
        self.pitches = []
        self.current_pitch = None
        self.timer_running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.recording = False
        
        # Создание интерфейса
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        # Настройка стилей
        self.setup_styles()
        
        # Главный контейнер
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Заголовок
        title_frame = tk.Frame(main_container, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(title_frame, text="FAST SINGER", 
                              font=('Arial', 28, 'bold'), 
                              fg=self.colors['accent2'], 
                              bg=self.colors['bg'])
        title_label.pack(side=tk.LEFT)
        
        # Элемент дизайна (пианино)
        piano_frame = tk.Frame(title_frame, bg=self.colors['bg'])
        piano_frame.pack(side=tk.RIGHT)
        
        # Создаем визуализацию клавиш пианино
        piano_keys = tk.Frame(piano_frame, bg=self.colors['bg'])
        piano_keys.pack()
        
        # Черные клавиши
        for i in range(5):
            key = tk.Frame(piano_keys, width=12, height=40, 
                          bg='black', relief=tk.RAISED, bd=1)
            key.pack(side=tk.LEFT, padx=1)
        
        # Основной контент (две колонки)
        content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая колонка - список текстов
        left_column = tk.Frame(content_frame, bg=self.colors['bg'], width=300)
        left_column.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        # Правая колонка - текст и управление
        right_column = tk.Frame(content_frame, bg=self.colors['bg'])
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Панель управления слева
        control_card = tk.Frame(left_column, bg=self.colors['card_bg'], 
                               relief=tk.RIDGE, bd=1)
        control_card.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(control_card, text="Управление текстами", 
                font=('Arial', 12, 'bold'),
                fg=self.colors['accent3'],
                bg=self.colors['card_bg'],
                padx=10, pady=10).pack()
        
        # Кнопки управления
        buttons_frame = tk.Frame(control_card, bg=self.colors['card_bg'])
        buttons_frame.pack(pady=(0, 10), padx=10)
        
        btn_style = {'font': ('Arial', 10), 'padx': 15, 'pady': 8, 
                    'bd': 0, 'cursor': 'hand2'}
        
        self.new_btn = tk.Button(buttons_frame, text="Новый текст", 
                                bg=self.colors['accent3'],
                                fg='white',
                                command=self.create_new_pitch,
                                **btn_style)
        self.new_btn.pack(fill=tk.X, pady=3)
        
        self.edit_btn = tk.Button(buttons_frame, text="Редактировать", 
                                 bg=self.colors['accent4'],
                                 fg='white',
                                 command=self.edit_pitch,
                                 **btn_style)
        self.edit_btn.pack(fill=tk.X, pady=3)
        
        self.delete_btn = tk.Button(buttons_frame, text="Удалить", 
                                   bg=self.colors['accent1'],
                                   fg='white',
                                   command=self.delete_pitch,
                                   **btn_style)
        self.delete_btn.pack(fill=tk.X, pady=3)
        
        # Список текстов
        list_card = tk.Frame(left_column, bg=self.colors['card_bg'], 
                            relief=tk.RIDGE, bd=1)
        list_card.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(list_card, text="Мои тексты", 
                font=('Arial', 12, 'bold'),
                fg=self.colors['accent2'],
                bg=self.colors['card_bg'],
                padx=10, pady=10).pack()
        
        # Поиск текстов
        search_frame = tk.Frame(list_card, bg=self.colors['card_bg'], padx=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, font=('Arial', 10),
                                    bg=self.colors['text_bg'],
                                    fg=self.colors['fg'],
                                    insertbackground=self.colors['accent2'],
                                    textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(search_frame, text="Поиск", 
                 bg=self.colors['accent4'],
                 fg='white',
                 font=('Arial', 9),
                 padx=10,
                 command=lambda: self.search_pitches(self.search_var.get())).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Список с прокруткой
        list_container = tk.Frame(list_card, bg=self.colors['card_bg'])
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.pitch_listbox = tk.Listbox(list_container,
                                       bg=self.colors['text_bg'],
                                       fg=self.colors['fg'],
                                       font=('Arial', 11),
                                       selectbackground=self.colors['accent4'],
                                       selectforeground='white',
                                       yscrollcommand=scrollbar.set,
                                       activestyle='none',
                                       height=15)
        self.pitch_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.pitch_listbox.yview)
        
        self.pitch_listbox.bind('<<ListboxSelect>>', self.on_pitch_select)
        self.pitch_listbox.bind('<Double-Button-1>', lambda e: self.start_practice())
        
        # Панель таймера и записи справа
        timer_card = tk.Frame(right_column, bg=self.colors['card_bg'],
                             relief=tk.RIDGE, bd=1)
        timer_card.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(timer_card, text="Таймер тренировки", 
                font=('Arial', 12, 'bold'),
                fg=self.colors['accent2'],
                bg=self.colors['card_bg'],
                padx=10, pady=10).pack()
        
        # Дисплей таймера
        timer_display = tk.Frame(timer_card, bg=self.colors['text_bg'])
        timer_display.pack(padx=20, pady=10, fill=tk.X)
        
        self.timer_label = tk.Label(timer_display, text="00:00:00", 
                                   font=('Arial', 36, 'bold'),
                                   fg=self.colors['accent1'],
                                   bg=self.colors['text_bg'])
        self.timer_label.pack(pady=10)
        
        # Кнопки таймера
        timer_buttons = tk.Frame(timer_card, bg=self.colors['card_bg'], padx=10)
        timer_buttons.pack(pady=(0, 15))
        
        self.start_btn = tk.Button(timer_buttons, text="Старт",
                                  bg=self.colors['accent3'],
                                  fg='white',
                                  font=('Arial', 10),
                                  padx=20, pady=8,
                                  command=self.start_timer)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(timer_buttons, text="Стоп",
                                 bg=self.colors['accent2'],
                                 fg='white',
                                 font=('Arial', 10),
                                 padx=20, pady=8,
                                 command=self.stop_timer)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = tk.Button(timer_buttons, text="Сброс",
                                  bg=self.colors['accent4'],
                                  fg='white',
                                  font=('Arial', 10),
                                  padx=20, pady=8,
                                  command=self.reset_timer)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка записи
        self.record_btn = tk.Button(timer_buttons, text="Запись",
                                   bg=self.colors['accent1'],
                                   fg='white',
                                   font=('Arial', 10),
                                   padx=20, pady=8,
                                   command=self.toggle_recording)
        self.record_btn.pack(side=tk.LEFT, padx=5)
        
        # Область текста
        text_card = tk.Frame(right_column, bg=self.colors['card_bg'],
                            relief=tk.RIDGE, bd=1)
        text_card.pack(fill=tk.BOTH, expand=True)
        
        text_header = tk.Frame(text_card, bg=self.colors['card_bg'])
        text_header.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        self.current_title = tk.Label(text_header, text="Выберите текст", 
                                     font=('Arial', 14, 'bold'),
                                     fg=self.colors['accent3'],
                                     bg=self.colors['card_bg'])
        self.current_title.pack(side=tk.LEFT)
        
        # Информация о тексте
        self.pitch_info = tk.Label(text_header, text="", 
                                  font=('Arial', 10),
                                  fg=self.colors['fg'],
                                  bg=self.colors['card_bg'])
        self.pitch_info.pack(side=tk.RIGHT)
        
        # Текст с прокруткой
        text_frame = tk.Frame(text_card, bg=self.colors['card_bg'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar_y = tk.Scrollbar(text_frame)
        scrollbar_x = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        
        self.pitch_text = tk.Text(text_frame,
                                 bg=self.colors['text_bg'],
                                 fg=self.colors['fg'],
                                 font=('Arial', 12),
                                 wrap=tk.WORD,
                                 padx=15, pady=15,
                                 insertbackground=self.colors['accent2'],
                                 yscrollcommand=scrollbar_y.set,
                                 xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.config(command=self.pitch_text.yview)
        scrollbar_x.config(command=self.pitch_text.xview)
        
        self.pitch_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Статистика внизу
        stats_frame = tk.Frame(main_container, bg=self.colors['card_bg'],
                              relief=tk.RIDGE, bd=1)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_label = tk.Label(stats_frame, 
                                   text="Статистика: 0 текстов | 0 тренировок | Общее время: 00:00",
                                   font=('Arial', 10),
                                   fg=self.colors['accent2'],
                                   bg=self.colors['card_bg'],
                                   padx=10, pady=10)
        self.stats_label.pack()
        
    def setup_styles(self):
        """Настройка стилей для виджетов"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настраиваем цвета для ttk виджетов
        style.configure('TButton',
                       background=self.colors['accent4'],
                       foreground='white',
                       borderwidth=0,
                       focusthickness=3,
                       focuscolor='none')
        style.map('TButton',
                 background=[('active', self.colors['accent3'])])
    
    def create_new_pitch(self):
        """Создание нового текста"""
        dialog = PitchDialog(self.root, "Создание нового текста", 
                           self.colors)
        if dialog.result:
            pitch_data = {
                'id': len(self.pitches) + 1,
                'title': dialog.result['title'],
                'content': dialog.result['content'],
                'created': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'last_practiced': '',
                'practice_count': 0,
                'best_time': 0,
                'tags': dialog.result.get('tags', '')
            }
            self.pitches.append(pitch_data)
            self.save_data()
            self.update_pitch_list()
            self.pitch_listbox.selection_set(len(self.pitches) - 1)
            self.on_pitch_select(None)
            messagebox.showinfo("Успех", "Текст успешно создан!")
    
    def edit_pitch(self):
        """Редактирование выбранного текста"""
        selected = self.pitch_listbox.curselection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите текст для редактирования")
            return
            
        pitch_index = selected[0]
        pitch = self.pitches[pitch_index]
        
        dialog = PitchDialog(self.root, "Редактирование текста", 
                           self.colors, pitch['title'], pitch['content'],
                           pitch.get('tags', ''))
        if dialog.result:
            pitch['title'] = dialog.result['title']
            pitch['content'] = dialog.result['content']
            pitch['tags'] = dialog.result.get('tags', '')
            self.save_data()
            self.update_pitch_list()
            self.on_pitch_select(None)
            messagebox.showinfo("Успех", "Текст успешно обновлен!")
    
    def delete_pitch(self):
        """Удаление выбранного текста"""
        selected = self.pitch_listbox.curselection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите текст для удаления")
            return
            
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот текст?"):
            del self.pitches[selected[0]]
            self.save_data()
            self.update_pitch_list()
            self.pitch_text.delete(1.0, tk.END)
            self.current_title.config(text="Выберите текст")
            self.pitch_info.config(text="")
    
    def on_pitch_select(self, event):
        """Обработка выбора текста из списка"""
        selected = self.pitch_listbox.curselection()
        if selected:
            pitch = self.pitches[selected[0]]
            self.current_pitch = pitch
            self.pitch_text.delete(1.0, tk.END)
            self.pitch_text.insert(1.0, pitch['content'])
            self.current_title.config(text=pitch['title'])
            
            # Отображаем информацию о тексте
            info_text = f"Создан: {pitch['created']}"
            if pitch['last_practiced']:
                info_text += f" | Последняя тренировка: {pitch['last_practiced']}"
            info_text += f" | Тренировок: {pitch['practice_count']}"
            
            if pitch['best_time'] > 0:
                minutes = int(pitch['best_time'] // 60)
                seconds = int(pitch['best_time'] % 60)
                info_text += f" | Лучшее время: {minutes:02d}:{seconds:02d}"
            
            self.pitch_info.config(text=info_text)
    
    def start_practice(self):
        """Начать тренировку с выбранным текстом"""
        self.on_pitch_select(None)
        self.start_timer()
    
    def start_timer(self):
        """Запуск таймера"""
        if not self.current_pitch:
            messagebox.showwarning("Внимание", "Сначала выберите текст!")
            return
            
        if not self.timer_running:
            self.timer_running = True
            self.start_time = time.time() - self.elapsed_time
            self.start_btn.config(state='disabled')
            self.update_timer()
    
    def stop_timer(self):
        """Остановка таймера"""
        if self.timer_running:
            self.timer_running = False
            self.start_btn.config(state='normal')
            
            # Обновление статистики
            if self.current_pitch:
                self.current_pitch['practice_count'] += 1
                self.current_pitch['last_practiced'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                if self.current_pitch['best_time'] == 0 or self.elapsed_time < self.current_pitch['best_time']:
                    self.current_pitch['best_time'] = self.elapsed_time
                self.save_data()
                self.update_stats()
                self.on_pitch_select(None)
    
    def toggle_recording(self):
        """Включение/выключение записи"""
        if not self.recording:
            self.recording = True
            self.record_btn.config(text="Остановить запись", bg=self.colors['accent1'])
            # Здесь будет код для начала записи
            messagebox.showinfo("Запись", "Запись начата!")
        else:
            self.recording = False
            self.record_btn.config(text="Запись", bg=self.colors['accent1'])
            # Здесь будет код для остановки записи
            messagebox.showinfo("Запись", "Запись остановлена!")
    
    def reset_timer(self):
        """Сброс таймера"""
        self.timer_running = False
        self.elapsed_time = 0
        self.start_btn.config(state='normal')
        self.timer_label.config(text="00:00:00")
    
    def update_timer(self):
        """Обновление отображения таймера"""
        if self.timer_running:
            self.elapsed_time = time.time() - self.start_time
            hours = int(self.elapsed_time // 3600)
            minutes = int((self.elapsed_time % 3600) // 60)
            seconds = int(self.elapsed_time % 60)
            self.timer_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer)
    
    def search_pitches(self, query):
        """Поиск текстов по запросу"""
        if not query:
            self.update_pitch_list()
            return
            
        self.pitch_listbox.delete(0, tk.END)
        for pitch in self.pitches:
            if (query.lower() in pitch['title'].lower() or 
                query.lower() in pitch['content'].lower() or
                query.lower() in pitch.get('tags', '').lower()):
                practice_info = f" ({pitch['practice_count']} тренировок)"
                self.pitch_listbox.insert(tk.END, pitch['title'] + practice_info)
    
    def update_pitch_list(self):
        """Обновление списка текстов"""
        self.pitch_listbox.delete(0, tk.END)
        for pitch in sorted(self.pitches, key=lambda x: x['title'].lower()):
            practice_info = f" ({pitch['practice_count']} тренировок)"
            if pitch.get('tags'):
                practice_info += f" [{pitch['tags']}]"
            self.pitch_listbox.insert(tk.END, pitch['title'] + practice_info)
        self.update_stats()
    
    def update_stats(self):
        """Обновление статистики"""
        total_pitches = len(self.pitches)
        total_practices = sum(pitch['practice_count'] for pitch in self.pitches)
        total_time = sum(pitch['best_time'] for pitch in self.pitches if pitch['best_time'] > 0)
        
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        
        self.stats_label.config(
            text=f"Статистика: {total_pitches} текстов | {total_practices} тренировок | Общее время: {hours:02d}:{minutes:02d}"
        )
    
    def save_data(self):
        """Сохранение данных в файл"""
        try:
            with open('pitches.json', 'w', encoding='utf-8') as f:
                json.dump(self.pitches, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def load_data(self):
        """Загрузка данных из файла"""
        try:
            if os.path.exists('pitches.json'):
                with open('pitches.json', 'r', encoding='utf-8') as f:
                    self.pitches = json.load(f)
                self.update_pitch_list()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")


class PitchDialog:
    """Диалог для создания/редактирования текста"""
    def __init__(self, parent, title, colors, current_title="", current_content="", current_tags=""):
        self.result = None
        self.colors = colors
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("700x600")
        self.dialog.configure(bg=colors['bg'])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Добавляем возможность сворачивания
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Центрирование диалога
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (700 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (600 // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Основной фрейм
        main_frame = tk.Frame(self.dialog, bg=colors['bg'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        tk.Label(main_frame, text=title, 
                font=('Arial', 16, 'bold'),
                fg=colors['accent2'],
                bg=colors['bg']).pack(anchor=tk.W, pady=(0, 20))
        
        # Поле названия
        tk.Label(main_frame, text="Название текста:", 
                font=('Arial', 11, 'bold'),
                fg=colors['fg'],
                bg=colors['bg']).pack(anchor=tk.W, pady=(0, 5))
        
        self.title_entry = tk.Entry(main_frame, 
                                   font=('Arial', 11),
                                   bg=colors['text_bg'],
                                   fg=colors['fg'],
                                   insertbackground=colors['accent2'])
        self.title_entry.pack(fill=tk.X, pady=(0, 15))
        self.title_entry.insert(0, current_title)
        
        # Поле тегов
        tk.Label(main_frame, text="Теги:", 
                font=('Arial', 11, 'bold'),
                fg=colors['fg'],
                bg=colors['bg']).pack(anchor=tk.W, pady=(0, 5))
        
        self.tags_entry = tk.Entry(main_frame, 
                                  font=('Arial', 11),
                                  bg=colors['text_bg'],
                                  fg=colors['fg'],
                                  insertbackground=colors['accent2'])
        self.tags_entry.pack(fill=tk.X, pady=(0, 15))
        self.tags_entry.insert(0, current_tags)
        
        # Подсказка к тегам
        tk.Label(main_frame, text="(разделяйте теги запятыми)", 
                font=('Arial', 9),
                fg=colors['accent4'],
                bg=colors['bg']).pack(anchor=tk.W, pady=(0, 15))
        
        # Поле текста
        tk.Label(main_frame, text="Текст песни:", 
                font=('Arial', 11, 'bold'),
                fg=colors['fg'],
                bg=colors['bg']).pack(anchor=tk.W, pady=(0, 5))
        
        text_frame = tk.Frame(main_frame, bg=colors['bg'])
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.content_text = tk.Text(text_frame,
                                   font=('Arial', 11),
                                   bg=colors['text_bg'],
                                   fg=colors['fg'],
                                   wrap=tk.WORD,
                                   padx=10, pady=10,
                                   insertbackground=colors['accent2'],
                                   yscrollcommand=scrollbar.set)
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.content_text.yview)
        
        self.content_text.insert(1.0, current_content)
        
        # Кнопки
        button_frame = tk.Frame(main_frame, bg=colors['bg'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        btn_style = {'font': ('Arial', 10), 'padx': 20, 'pady': 8, 
                    'bd': 0, 'cursor': 'hand2'}
        
        # Кнопка подтвердить
        self.confirm_btn = tk.Button(button_frame, text="Подтвердить", 
                 bg=colors['accent3'],
                 fg='white',
                 command=self.save,
                 **btn_style)
        self.confirm_btn.pack(side=tk.RIGHT, padx=5)
        
        # Кнопка отмены
        self.cancel_btn = tk.Button(button_frame, text="Отмена", 
                 bg=colors['accent1'],
                 fg='white',
                 command=self.on_closing,
                 **btn_style)
        self.cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Кнопка свернуть
        self.minimize_btn = tk.Button(button_frame, text="Свернуть", 
                 bg=colors['accent4'],
                 fg='white',
                 command=self.minimize_window,
                 **btn_style)
        self.minimize_btn.pack(side=tk.LEFT, padx=5)
        
        # Обработка нажатия Enter для подтверждения
        self.title_entry.bind('<Return>', lambda e: self.save())
        self.tags_entry.bind('<Return>', lambda e: self.save())
        
        self.dialog.wait_window()
    
    def minimize_window(self):
        """Свернуть окно"""
        self.dialog.iconify()
    
    def on_closing(self):
        """Обработка закрытия окна"""
        self.result = None
        self.dialog.destroy()
    
    def save(self):
        """Сохранение данных из диалога"""
        title = self.title_entry.get().strip()
        content = self.content_text.get(1.0, tk.END).strip()
        tags = self.tags_entry.get().strip()
        
        if not title:
            messagebox.showwarning("Внимание", "Введите название текста")
            return
        
        if not content:
            messagebox.showwarning("Внимание", "Введите текст песни!")
            return
        
        self.result = {
            'title': title,
            'content': content,
            'tags': tags
        }
        self.dialog.destroy()


def main():
    root = tk.Tk()
    app = PitchTrainer(root)
    root.mainloop()

if __name__ == "__main__":
    main()