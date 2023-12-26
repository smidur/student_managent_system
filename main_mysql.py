from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QGridLayout, QPushButton, QMainWindow, QDialog, QTableWidget,
                             QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar,
                             QStatusBar, QMessageBox)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import sys
import mysql.connector


class DatabaseConnection:
    def __init__(self,
                 host="localhost",
                 user="root",
                 password="pythoncourse", database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host,
                                             user=self.user,
                                             password=self.password,
                                             database=self.database)
        return connection


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
        about_action.triggered.connect(self.about)

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
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()
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

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")

        style = """
            margin-top: 20px;
            text-align: justify;
            padding-right: 16px;
            font-size: 16px;
        """
        self.setStyleSheet(style)

        text = """This app was created during the course "The Python Mega Course"."""
        header = "Feel free to modify and reuse this app."

        self.setInformativeText(header)
        self.setText(text)


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # get and index of the selected cell of the table
        index = main_window.table.currentRow()

        # get id from selected row
        self.student_id = main_window.table.item(index, 0).text()

        # get student name from selected row
        student_name = main_window.table.item(index, 1).text()
        # add student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # get student course from selected row
        course_name = main_window.table.item(index, 2).text()
        # add combo box of courses
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # get student phone number from selected row
        phone = main_window.table.item(index, 3).text()
        # add mobile phone number
        self.phone = QLineEdit(phone)
        self.phone.setPlaceholderText("0123456789")
        layout.addWidget(self.phone)

        # add submit button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()

        name = self.student_name.text()
        course = self.course_name.currentText()
        phone = self.phone.text()

        cursor.execute("UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s",
                       (name, course, phone, self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        # refresh the table
        main_window.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")
        self.setFixedWidth(400)
        self.setFixedHeight(100)

        layout = QGridLayout()

        confirmation = QLabel("Are you sure you want to delete?")
        confirmation.setAlignment(Qt.AlignmentFlag.AlignCenter)
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 3)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 2)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        # get selected tow index and student id
        index = main_window.table.currentRow()
        student_id = main_window.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()

        # refresh the table
        main_window.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

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

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)",
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

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()

        if column_name[:-1] == "Name":
            cursor.execute("SELECT * FROM students WHERE name = %s",
                                    (search_line,))
        elif column_name[:-1] == "Course":
            cursor.execute("SELECT * FROM students WHERE course = %s",
                                    (search_line,))
        elif column_name[:-1] == "Phone":
            cursor.execute("SELECT * FROM students WHERE mobile = %s",
                                    (search_line,))
        elif column_name[:-1] == "ID":
            cursor.execute("SELECT * FROM students WHERE id = %s",
                                    (search_line,))
        result = cursor.fetchall()

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
