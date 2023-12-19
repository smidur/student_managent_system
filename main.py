from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QGridLayout, QPushButton, QMainWindow, QDialog, QTableWidget,
                             QTableWidgetItem, QDialog, QVBoxLayout, QComboBox)
from PyQt6.QtGui import QAction
import sys
import sqlite3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")

        add_student_action = QAction("Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)

        # the next srting is for MacOS only!
        # about_action.setMenuRole(QAction.MenuRole.NoRole)

        search_action = QAction("Search", self)
        search_action.triggered.connect(self.search)
        help_menu_item.addAction(search_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Phone"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

    def load_data(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("SELECT * FROM students ")
        self.table.setRowCount(0)
        for row_num, row_data in enumerate(result):
            self.table.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        search = SearchDialog()
        search.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setFixedWidth(400)
        self.setFixedHeight(200)

        layout = QVBoxLayout()

        # add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # add combo box of courses
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # add mobile phone number
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("0123456789")
        layout.addWidget(self.phone)

        # add submit button
        button = QPushButton("Submit")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        phone = self.phone.text()

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                       (name, course, phone))
        connection.commit()
        cursor.close()
        connection.close()
        stu_man_sys.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setFixedWidth(400)
        self.setFixedHeight(100)

        grid = QGridLayout()

        # add search field
        search_line_edit = QLineEdit()
        search_line_edit.setPlaceholderText("Search...")
        grid.addWidget(search_line_edit, 0, 0)

        columns_options = ["IDs", "Names", "Courses", "Phones"]
        columns_combo = QComboBox()
        columns_combo.addItems(columns_options)
        grid.addWidget(columns_combo, 0, 1)

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search)
        search_button.pressed.connect(self.search)
        grid.addWidget(search_button, 1, 1)

        self.setLayout(grid)

    def search(self):
        pass


app = QApplication(sys.argv)
stu_man_sys = MainWindow()
stu_man_sys.show()
stu_man_sys.load_data()
sys.exit(app.exec())
