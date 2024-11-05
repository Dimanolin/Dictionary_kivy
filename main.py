import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup

class DictionaryApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = None
        self.word_count_label = None

    def build(self):
        self.connect_to_db()
        self.create_table()

        layout = BoxLayout(orientation = 'vertical', padding = 20, spacing = 15)

        #Поле для ввода слова
        self.word_input = TextInput(
            hint_text = "Введите слово", 
            multiline = False, 
            font_size = 18, 
            size_hint_y = None, 
            height = 40, 
            background_color = (0.9, 0.9, 0.9, 1), 
            foreground_color = (0, 0, 0, 1), 
            padding = [10, 10])
        layout.add_widget(self.word_input)

        #Поле для ввода значения
        self.meaning_input = TextInput(
            hint_text = "Введите значение", 
            multiline = True, 
            font_size = 18, 
            size_hint_y = None, 
            height = 100, 
            background_color = (0.9, 0.9, 0.9, 1), 
            foreground_color = (0, 0, 0, 1), 
            padding = [10, 10])
        layout.add_widget(self.meaning_input)

        #Кнопка для добавления записи
        add_button = Button(
            text = "Добавить слово", 
            size_hint_y = None, 
            height = 50, 
            background_color = (0.2, 0.6, 1, 1), 
            color = (1, 1, 1, 1))
        add_button.bind(on_press = self.add_word)
        layout.add_widget(add_button)

        #Поле для ввода слова для поиска
        self.search_input = TextInput(
            hint_text = "Поиск слова", 
            multiline = False, 
            font_size = 18, 
            size_hint_y = None, 
            height = 40, 
            background_color = (0.9, 0.9, 0.9, 1), 
            foreground_color = (0, 0, 0, 1), 
            padding = [10, 10])
        layout.add_widget(self.search_input)

        #Кнопка для поиска
        search_button = Button(
            text = "Найти слово", 
            size_hint_y = None, 
            height = 50, 
            background_color = (0.2, 0.6, 1, 1), 
            color = (1, 1, 1, 1))
        search_button.bind(on_press = self.search_word)
        layout.add_widget(search_button)

        #Поле для ввода слова для удаления
        self.delete_input = TextInput(
            hint_text = "Удалить слово", 
            multiline = False, 
            font_size = 18, 
            size_hint_y = None, 
            height = 40, 
            background_color = (0.9, 0.9, 0.9, 1), 
            foreground_color = (0, 0, 0, 1), 
            padding = [10, 10])
        layout.add_widget(self.delete_input)

        #Кнопка для удаления слова
        delete_button = Button(
            text = "Удалить слово", 
            size_hint_y = None, 
            height = 50, 
            background_color = (0.2, 0.6, 1, 1), 
            color = (1, 1, 1, 1))
        delete_button.bind(on_press = self.delete_word)
        layout.add_widget(delete_button)

        #Кнопка для просмотра всех слов
        view_all_button = Button(
            text = "Посмотреть все слова",
            size_hint_y = None,
            height = 50,
            background_color = (0.2, 0.8, 0.2, 1),
            color = (1, 1, 1, 1)
        )
        view_all_button.bind(on_press = self.view_all_words)
        layout.add_widget(view_all_button)

        #Сообщение для вывода статуса
        self.status_label = Label(text="", font_size = 16, color = (0.2, 0.2, 0.2, 1))
        layout.add_widget(self.status_label)

        #Лейбл для отображения количества слов в словаре
        self.word_count_label = Label(text = f"Количество слов: {self.get_word_count()}", font_size = 16, color = (0.2, 0.2, 0.2, 1))
        layout.add_widget(self.word_count_label)

        return layout
    
    def connect_to_db(self):
        """Подключение к базе данных SQLite."""
        self.conn = sqlite3.connect("dictionary.db")
        self.cursor = self.conn.cursor()

    def create_table(self):
        """Создание таблицы для хранения слов и значений, если её нет."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS words (
                word TEXT PRIMARY KEY,
                meaning TEXT                       
                )
        """)
        self.conn.commit()

    def get_word_count(self):
        """Получение количества слов в словаре."""
        self.cursor.execute("SELECT COUNT(*) FROM words")
        count = self.cursor.fetchone()[0]
        return count
    
    def add_word(self, instanse):

        #Получаем введённые пользователем данные
        word = self.word_input.text.strip()
        meaning = self.meaning_input.text.strip()

        #Проверка на пустоту
        if not word or not meaning:
            self.status_label.text = "Пожалуйста, заполните оба поля!"
        else:
            #Проверка есть ли слово в базе
            self.cursor.execute("SELECT * FROM words WHERE word = ?", (word,))
            result = self.cursor.fetchone()
            if result:
                self.status_label.text = f"Слово '{word} уже существует!'"
                self.word_input.text = ""
                self.meaning_input.text = ""
            else:
                #Добавление нового слова в базу
                self.cursor.execute("INSERT INTO words (word, meaning) VALUES (?, ?)", (word, meaning))
                self.conn.commit()
                self.status_label.text = f"Слово '{word}' добавлено!"
                self.update_word_count()
                #Очищаем поля ввода
                self.word_input.text = ""
                self.meaning_input.text = ""

    def search_word(self, instance):
        """Поиск значения слова в базе данных"""
        search_word = self.search_input.text.strip()

        if not search_word:
            self.status_label.text = "Введите слово для поиска!"
        else:
            #Поиск слова в базе
            self.cursor.execute("SELECT meaning FROM words WHERE word = ?", (search_word,))
            result = self.cursor.fetchone()
            if result:
                self.status_label.text = f"Значение '{search_word}': {result[0]}"
            else:
                self.status_label.text = f"Слово '{search_word}' не найдено."
            #Очищаем поле поиска
            self.search_input.text = ""

    def delete_word(self, instance):
        """Удаление слова из базы данных."""
        delete_word = self.delete_input.text.strip()

        if not delete_word:
            self.status_label.text = "Введите слово для удаления!"
        else:
            #Проверка наличия слова перед удалением
            self.cursor.execute("SELECT * FROM words WHERE word = ?", (delete_word,))
            result = self.cursor.fetchone()
            if result:
                self.cursor.execute("DELETE FROM words WHERE word = ?", (delete_word,))
                self.conn.commit()
                self.status_label.text = f"Слово '{delete_word}' было удалено."
                self.update_word_count()
            else:
                self.status_label.text = f"Слово '{delete_word}' не найденов словаре."
            #Очищаем поле удаления
            self.delete_input.text = ""

    def update_word_count(self):
        """Обновление отображаемого количества слов."""
        self.word_count_label.text = f"Количество слов: {self.get_word_count()}"

    def view_all_words(self, instance):
        """Просмотр всех слов в словаре."""
        self.cursor.execute("SELECT word, meaning FROM words")
        words = self.cursor.fetchall()

        if words:
            content = "\n".join([f"{word}: {meaning}" for word, meaning in words])
        else:
            content = "Словарь пуст."
        
        popup = Popup(title = 'Все слова в словаре', content = Label(text = content, size_hint = (0.8, 0.8)), size_hint = (0.9, 0.9))
        popup.open()
    
    def on_stop(self):
        """Закрываем соединение с базой данных при выходе из приложения"""
        if self.conn:
            self.conn.close()
    
if __name__ == "__main__":
    DictionaryApp().run()