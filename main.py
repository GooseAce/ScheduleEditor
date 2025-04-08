import sys
import os
from datetime import date
import time as timer
import sqlite3
from ui import Ui_MainWindow
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon, QPixmap
days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(self.resource_path('icon.ico')))
        self.day = None
        self.reminder_timer = QTimer()
        self.init_ui()
        self.setWindowTitle('Schedules')
        # Задняя картинка
        self.label.setPixmap(QPixmap(self.resource_path('background.jpg')))

    def init_ui(self):
        # Создаю БД
        self.creating_db()
        # Это кнопка Add
        self.pushButton.clicked.connect(self.add)
        # Это кнопка Delete
        self.pushButton_2.clicked.connect(self.delete)
        self.output_list()
        # Группа слотов
        self.Monday.clicked.connect(self.output_list)
        self.Tuesday.clicked.connect(self.output_list)
        self.Wednesday.clicked.connect(self.output_list)
        self.Thursday.clicked.connect(self.output_list)
        self.Friday.clicked.connect(self.output_list)
        self.Saturday.clicked.connect(self.output_list)
        self.Sunday.clicked.connect(self.output_list)
        # Метод напоминания
        self.reminder_timer.timeout.connect(self.reminder)
        self.reminder_timer.start(60000)

    def add(self):
        con = sqlite3.connect('week.db')
        task = self.lineEdit.text()
        time_str = self.timeEdit.time().toString("HH:mm")
        self.show_selected()
        if not task:
            QMessageBox.critical(self, "Error", "Task cannot be empty")
            return
        with con:
            cur = con.cursor()
            cur.execute(f"SELECT time FROM {self.day} WHERE time = ?", (time_str,))
            existing_record = cur.fetchone()
            if existing_record is None:
                cur.execute(f"INSERT INTO {self.day}(time, task) VALUES(?, ?)", (time_str, task))
            else:
                cur.execute(f"UPDATE {self.day} SET task = ? WHERE time = ?", (task, time_str))
        self.output_list()

    def delete(self):
        con = sqlite3.connect('week.db')
        with con:
            self.show_selected()
            cur = con.cursor()
            time_str = self.timeEdit.time().toString("HH:mm")
            cur.execute(f"SELECT time FROM {self.day} WHERE time = ?", (time_str,))
            existing_record = cur.fetchone()
            if existing_record is None:
                QMessageBox.critical(self, "Error", "There is no such time in the list")
                return
            else:
                cur.execute(f"DELETE FROM {self.day} WHERE time = ?", (time_str,))
        self.output_list()

    def show_selected(self):
        if self.Monday.isChecked():
            self.day = "monday"
        elif self.Tuesday.isChecked():
            self.day = "tuesday"
        elif self.Wednesday.isChecked():
            self.day = "wednesday"
        elif self.Thursday.isChecked():
            self.day = "thursday"
        elif self.Friday.isChecked():
            self.day = "friday"
        elif self.Saturday.isChecked():
            self.day = "saturday"
        elif self.Sunday.isChecked():
            self.day = "sunday"
        else:
            self.day = days[date.today().weekday()]

    def output_list(self):
        con = sqlite3.connect('week.db')
        self.show_selected()
        self.listWidget.clear()
        with con:
            cur = con.cursor()
            cur.execute(f"SELECT time, task FROM {self.day} ORDER BY time")
            rows = cur.fetchall()
            for time, task in rows:
                item_text = f"{time} - {task}"
                self.listWidget.addItem(item_text)

    def reminder(self):
        con = sqlite3.connect('week.db')
        cur = con.cursor()
        current_day = days[date.today().weekday()]
        current_time = timer.strftime("%H:%M")
        query = f"SELECT task FROM {current_day} WHERE time = ?"
        cur.execute(query, (current_time,))
        result = cur.fetchone()
        if result:
            task = result[0]
            QMessageBox.information(self, "Reminder", task)

    @staticmethod
    # Метод для того, чтобы картинки показывались в exe
    def resource_path(relative_path):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    @staticmethod
    def creating_db():
        con = sqlite3.connect('week.db')
        cur = con.cursor()
        for day in days:
            cur.execute(f'''
                            CREATE TABLE IF NOT EXISTS {day} (
                                time TEXT PRIMARY KEY,
                                task TEXT NOT NULL
                            )''')
        con.commit()
        con.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
