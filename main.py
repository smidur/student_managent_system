from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QGridLayout, QPushButton, QMainWindow, QDialog, QTableWidget,
                             QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar,
                             QStatusBar)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import sys
import sqlite3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(777, 707)

        file_menu_item = self.menuBar().addMenu("&File")
        edit_menu_item = self.menuBar().addMenu("&Edit")
        help_menu_item = self.menuBar().addMenu("&Help")

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)

        # the next srting is for MacOS only!
        # about_action.setMenuRole(QAction.MenuRole.NoRole)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        refresh_action = QAction("Reload Table", self)
        refresh_action.triggered.connect(self.load_data)
        edit_menu_item.addAction(refresh_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Phone"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # create toolbar and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # create status bar and add status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)
        edit_button.pressed.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)
        delete_button.pressed.connect(self.delete)

        children = self.findChildren(QPushButton)

        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

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

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()


class EditDialog(QDialog):
    pass


class DeleteDialog(QDialog):
    pass


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
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
        main_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search data")
        self.setFixedWidth(400)
        self.setFixedHeight(100)

        grid = QGridLayout()

        # add search field
        self.search_line_edit = QLineEdit()
        self.search_line_edit.setPlaceholderText("Search...")
        grid.addWidget(self.search_line_edit, 0, 0)

        columns_options = ["IDs", "Names", "Courses", "Phones"]
        self.columns_combo = QComboBox()
        self.columns_combo.addItems(columns_options)
        self.columns_combo.setCurrentIndex(1)
        grid.addWidget(self.columns_combo, 0, 1)

        refresh_table_button = QPushButton("Refresh")
        refresh_table_button.setFixedWidth(100)
        refresh_table_button.clicked.connect(main_window.load_data)
        refresh_table_button.pressed.connect(main_window.load_data)
        grid.addWidget(refresh_table_button, 1, 0)

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search)
        search_button.pressed.connect(self.search)
        grid.addWidget(search_button, 1, 1)

        self.setLayout(grid)

    def search(self):
        column_name = self.columns_combo.currentText()
        search_line = self.search_line_edit.text()

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        result = ""

        if column_name[:-1] == "Name":
            result = cursor.execute("SELECT * FROM students WHERE name = ?",
                                    (search_line,))
        elif column_name[:-1] == "Course":
            result = cursor.execute("SELECT * FROM students WHERE course = ?",
                                    (search_line,))
        elif column_name[:-1] == "Phone":
            result = cursor.execute("SELECT * FROM students WHERE mobile = ?",
                                    (search_line,))
        elif column_name[:-1] == "ID":
            result = cursor.execute("SELECT * FROM students WHERE id = ?",
                                    (search_line,))

        items = main_window.table.findItems(search_line, Qt.MatchFlag.MatchFixedString)

        for item in items:
            main_window.table.item(item.row(), 1).setSelected(True)
            main_window.table.item(item.row(), 2).setSelected(True)
            main_window.table.item(item.row(), 3).setSelected(True)

        cursor.close()
        connection.close()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
