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
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f8ff')
        
        # Данные приложения
        self.pitches = []
        self.current_pitch = None
        self.timer_running = False
        self.start_time = 0
        self.elapsed_time = 0
        
        # Создание интерфейса
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        # Стили
        style = ttk.Style()
        style.configure('TFrame', background='#f0f8ff')
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('TLabel', background='#f0f8ff', font=('Arial', 10))
        
        # Главный фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок
        title_label = tk.Label(main_frame, text="Fast Singer", 
                              font=('Arial', 24, 'bold'), 
                              fg='#2c3e50', bg='#f0f8ff')
        title_label.pack(pady=10)
        
        # Фрейм управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        # Кнопки управления
        ttk.Button(control_frame, text="Новый текст", 
                  command=self.create_new_pitch).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Редактировать", 
                  command=self.edit_pitch).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Удалить", 
                  command=self.delete_pitch).pack(side=tk.LEFT, padx=5)
        
        # Список питчей
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(list_frame, text="Мои тексты:", 
                font=('Arial', 12, 'bold'), bg='#f0f8ff').pack(anchor=tk.W)
        
        self.pitch_listbox = tk.Listbox(list_frame, height=8, 
                                       font=('Arial', 10),
                                       selectbackground='#3498db')
        self.pitch_listbox.pack(fill=tk.BOTH, expand=True)
        self.pitch_listbox.bind('<<ListboxSelect>>', self.on_pitch_select)
        
        # Фрейм таймера и тренировки
        training_frame = ttk.Frame(main_frame)
        training_frame.pack(fill=tk.X, pady=10)
        
        # Таймер
        timer_frame = ttk.LabelFrame(training_frame, text="Таймер")
        timer_frame.pack(fill=tk.X, pady=5)
        
        self.timer_label = tk.Label(timer_frame, text="00:00", 
                                   font=('Arial', 20, 'bold'),
                                   fg='#e74c3c', bg='white')
        self.timer_label.pack(pady=10)
        
        timer_buttons = ttk.Frame(timer_frame)
        timer_buttons.pack(pady=5)
        
        self.start_button = ttk.Button(timer_buttons, text="Старт", 
                                      command=self.start_timer)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(timer_buttons, text="Стоп", 
                  command=self.stop_timer).pack(side=tk.LEFT, padx=5)
        ttk.Button(timer_buttons, text="Сброс", 
                  command=self.reset_timer).pack(side=tk.LEFT, padx=5)
        
        # Область отображения питча
        pitch_frame = ttk.LabelFrame(training_frame, text="Текст")
        pitch_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.pitch_text = tk.Text(pitch_frame, height=12, 
                                 font=('Arial', 11), wrap=tk.WORD,
                                 padx=10, pady=10)
        self.pitch_text.pack(fill=tk.BOTH, expand=True)
        
        # Статистика
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_label = tk.Label(stats_frame, text="Статистика: 0 текстов", 
                                   font=('Arial', 10), bg='#f0f8ff')
        self.stats_label.pack(anchor=tk.W)
        
    def create_new_pitch(self):
        """Создание нового текста"""
        dialog = PitchDialog(self.root, "Создание нового текста")
        if dialog.result:
            pitch_data = {
                'id': len(self.pitches) + 1,
                'title': dialog.result['title'],
                'content': dialog.result['content'],
                'created': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'practice_count': 0,
                'best_time': 0
            }
            self.pitches.append(pitch_data)
            self.save_data()
            self.update_pitch_list()
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
                           pitch['title'], pitch['content'])
        if dialog.result:
            pitch['title'] = dialog.result['title']
            pitch['content'] = dialog.result['content']
            self.save_data()
            self.update_pitch_list()
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
    
    def on_pitch_select(self, event):
        """Обработка выбора текста из списка"""
        selected = self.pitch_listbox.curselection()
        if selected:
            pitch = self.pitches[selected[0]]
            self.current_pitch = pitch
            self.pitch_text.delete(1.0, tk.END)
            self.pitch_text.insert(1.0, pitch['content'])
    
    def start_timer(self):
        """Запуск таймера"""
        if not self.current_pitch:
            messagebox.showwarning("Внимание", "Сначала выберите текст!")
            return
            
        if not self.timer_running:
            self.timer_running = True
            self.start_time = time.time() - self.elapsed_time
            self.start_button.config(state='disabled')
            self.update_timer()
    
    def stop_timer(self):
        """Остановка таймера"""
        if self.timer_running:
            self.timer_running = False
            self.start_button.config(state='normal')
            
            # Обновление статистики
            if self.current_pitch:
                self.current_pitch['practice_count'] += 1
                if self.current_pitch['best_time'] == 0 or self.elapsed_time < self.current_pitch['best_time']:
                    self.current_pitch['best_time'] = self.elapsed_time
                self.save_data()
                self.update_stats()
    
    def reset_timer(self):
        """Сброс таймера"""
        self.timer_running = False
        self.elapsed_time = 0
        self.start_button.config(state='normal')
        self.timer_label.config(text="00:00")
    
    def update_timer(self):
        """Обновление отображения таймера"""
        if self.timer_running:
            self.elapsed_time = time.time() - self.start_time
            minutes = int(self.elapsed_time // 60)
            seconds = int(self.elapsed_time % 60)
            self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer)
    
    def update_pitch_list(self):
        """Обновление списка текстов"""
        self.pitch_listbox.delete(0, tk.END)
        for pitch in self.pitches:
            practice_info = f" (тренировок: {pitch['practice_count']})"
            self.pitch_listbox.insert(tk.END, pitch['title'] + practice_info)
        self.update_stats()
    
    def update_stats(self):
        """Обновление статистики"""
        total_pitches = len(self.pitches)
        total_practices = sum(pitch['practice_count'] for pitch in self.pitches)
        self.stats_label.config(
            text=f"Статистика: {total_pitches} текстов, {total_practices} тренировок"
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
    def __init__(self, parent, title, current_title="", current_content=""):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.configure(bg='#f0f8ff')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Заголовок
        tk.Label(self.dialog, text="Название текста:", 
                font=('Arial', 11, 'bold'), bg='#f0f8ff').pack(anchor=tk.W, pady=(10, 5))
        
        self.title_entry = tk.Entry(self.dialog, font=('Arial', 11), width=50)
        self.title_entry.pack(padx=10, pady=5, fill=tk.X)
        self.title_entry.insert(0, current_title)
        
        # Текст питча
        tk.Label(self.dialog, text="Текст:", 
                font=('Arial', 11, 'bold'), bg='#f0f8ff').pack(anchor=tk.W, pady=(10, 5))
        
        self.content_text = tk.Text(self.dialog, font=('Arial', 11), 
                                   wrap=tk.WORD, height=15)
        self.content_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.content_text.insert(1.0, current_content)
        
        # Кнопки
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Сохранить", 
                  command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", 
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        self.dialog.wait_window()
    
    def save(self):
        """Сохранение данных из диалога"""
        title = self.title_entry.get().strip()
        content = self.content_text.get(1.0, tk.END).strip()
        
        if not title:
            messagebox.showwarning("Внимание", "Введите название текста")
            return
        
        if not content:
            messagebox.showwarning("Внимание", "Введите текст !")
            return
        
        self.result = {
            'title': title,
            'content': content
        }
        self.dialog.destroy()


def main():
    root = tk.Tk()
    app = PitchTrainer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
