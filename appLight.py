import sys
import json
import paramiko
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QListWidget, QPushButton, QDialog, QLineEdit, QLabel, QMessageBox
)

# Base Dialog Class for Book Actions
class BookDialog(QDialog):
    def __init__(self, parent, title, book_data=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 400, 300)  # Set size for the dialog
        self.init_ui(book_data)

    def init_ui(self, book_data):
        layout = QVBoxLayout()
        self.inputs = {
            'name': QLineEdit(self),
            'author': QLineEdit(self),
            'pages': QLineEdit(self),
            'genre': QLineEdit(self),
            'summary': QLineEdit(self),
            'stock': QLineEdit(self),
            'price': QLineEdit(self)
        }
        
        for key, input_field in self.inputs.items():
            input_field.setPlaceholderText(key.capitalize())
            layout.addWidget(input_field)

        save_button = QPushButton("Lagre")
        save_button.clicked.connect(lambda: self.save_book(book_data))
        cancel_button = QPushButton("Avbryt")
        cancel_button.clicked.connect(self.reject)

        layout.addWidget(save_button)
        layout.addWidget(cancel_button)
        self.setLayout(layout)

        if book_data:  # Load existing book data if provided
            for key, value in book_data.items():
                self.inputs[key].setText(value)

    def save_book(self, book_data):
        new_data = {key: input_field.text() for key, input_field in self.inputs.items()}
        if not all(new_data.values()):
            QMessageBox.warning(self, "Advarsel", "Alle feltene må fylles ut.")
            return

        try:
            ssh, remote_file_path = self.connect_to_server()
            sftp = ssh.open_sftp()
            books = self.load_books_from_file(sftp, remote_file_path)

            if book_data:  # Editing an existing book
                for i, book in enumerate(books):
                    if book['name'] == book_data['name']:
                        books[i] = new_data
                        break
            else:  # Adding a new book
                books.append(new_data)

            self.save_books_to_file(sftp, remote_file_path, books)
            QMessageBox.information(self, "Suksess", "Boken ble lagret!")
            self.parent().load_books()  # Refresh book list
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Feil", str(e))

    def connect_to_server(self):
        """Connect to the server."""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('192.168.1.218', username='bok', password='bok')
        return ssh, '/home/bok/books.json'

    def load_books_from_file(self, sftp, remote_file_path):
        with sftp.open(remote_file_path, 'r') as file:
            return json.load(file)

    def save_books_to_file(self, sftp, remote_file_path, books):
        with sftp.open(remote_file_path, 'w') as file:
            json.dump(books, file, indent=4)

# Main Application Class
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bok Database")
        self.setGeometry(100, 100, 600, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.book_list = QListWidget(self)
        layout.addWidget(self.book_list)

        buttons = [
            ("Legg til bok", self.open_add_book_dialog),
            ("Rediger bok", self.open_edit_book_dialog),
            ("Slett bok", self.delete_book)
        ]

        for label, slot in buttons:
            button = QPushButton(label)
            button.clicked.connect(slot)
            layout.addWidget(button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.load_books()

    def load_books(self):
        try:
            ssh, remote_file_path = self.connect_to_server()
            sftp = ssh.open_sftp()
            books = self.load_books_from_file(sftp, remote_file_path)
            self.book_list.clear()
            for book in books:
                self.book_list.addItem(book['name'])
        except Exception as e:
            QMessageBox.critical(self, "Feil", str(e))

    def open_add_book_dialog(self):
        dialog = BookDialog(self, "Legg til bok")
        dialog.exec_()

    def open_edit_book_dialog(self):
        selected_items = self.book_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Advarsel", "Ingen bok er valgt.")
            return

        book_name = selected_items[0].text()
        dialog = BookDialog(self, "Rediger bok", self.get_book_data(book_name))
        dialog.exec_()

    def delete_book(self):
        selected_items = self.book_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Advarsel", "Ingen bok er valgt.")
            return

        book_name = selected_items[0].text()
        try:
            ssh, remote_file_path = self.connect_to_server()
            sftp = ssh.open_sftp()
            books = self.load_books_from_file(sftp, remote_file_path)
            books = [book for book in books if book['name'] != book_name]
            self.save_books_to_file(sftp, remote_file_path, books)
            QMessageBox.information(self, "Suksess", "Boken ble slettet.")
            self.load_books()
        except Exception as e:
            QMessageBox.critical(self, "Feil", str(e))

    def get_book_data(self, book_name):
        try:
            ssh, remote_file_path = self.connect_to_server()
            sftp = ssh.open_sftp()
            books = self.load_books_from_file(sftp, remote_file_path)
            for book in books:
                if book['name'] == book_name:
                    return book
        except Exception as e:
            QMessageBox.critical(self, "Feil", str(e))
        return None

    def connect_to_server(self):
        """Connect to the server."""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('192.168.1.218', username='bok', password='bok')
        return ssh, '/home/bok/books.json'

    def load_books_from_file(self, sftp, remote_file_path):
        with sftp.open(remote_file_path, 'r') as file:
            return json.load(file)

    def save_books_to_file(self, sftp, remote_file_path, books):
        with sftp.open(remote_file_path, 'w') as file:
            json.dump(books, file, indent=4)

# Entry point for the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
