import sys
import json
import paramiko
import base64
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QListWidget, QPushButton, QDialog, QLineEdit, QLabel, QMessageBox, QTextEdit, QFileDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# Dialog class to show book details
class BookDetailDialog(QDialog):
    def __init__(self, parent, book_data):
        super().__init__(parent)
        self.setWindowTitle("Book Details")
        self.setGeometry(100, 100, 400, 300)
        self.init_ui(book_data)

    def init_ui(self, book_data):
        layout = QVBoxLayout()

        if book_data:
            for key, value in book_data.items():
                if key == 'image':
                    label = QLabel(self)
                    pixmap = QPixmap()
                    pixmap.loadFromData(base64.b64decode(value))
                    label.setPixmap(pixmap)
                    layout.addWidget(label)
                else:
                    label = QLabel(f"{key.capitalize()}: {value}")
                    if key == 'summary':
                        label.setWordWrap(True)
                        label.setMaximumHeight(100)
                    layout.addWidget(label)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)

# Base Dialog Class for Book Actions
class BookDialog(QDialog):
    def __init__(self, parent, title, book_data=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 400, 300)
        self.init_ui(book_data)

    def init_ui(self, book_data):
        layout = QVBoxLayout()
        self.inputs = {
            'name': QLineEdit(self),
            'author': QLineEdit(self),
            'pages': QLineEdit(self),
            'genre': QLineEdit(self),
            'summary': QTextEdit(self),
            'stock': QLineEdit(self),
            'price': QLineEdit(self)
        }

        self.inputs['summary'].setMaximumHeight(100)

        for key, input_field in self.inputs.items():
            input_field.setPlaceholderText(key.capitalize())
            layout.addWidget(input_field)

        self.image_path = None
        upload_image_button = QPushButton("Upload Image")
        upload_image_button.clicked.connect(self.upload_image)
        layout.addWidget(upload_image_button)

        save_button = QPushButton("Lagre")
        save_button.clicked.connect(lambda: self.save_book(book_data))

        cancel_button = QPushButton("Avbryt")
        cancel_button.clicked.connect(self.accept)

        layout.addWidget(save_button)
        layout.addWidget(cancel_button)
        self.setLayout(layout)

        if book_data:
            for key, value in book_data.items():
                if key != 'image':
                    self.inputs[key].setText(value)

    def upload_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)", options=options)
        if file_name:
            self.image_path = file_name

    def save_book(self, book_data):
        new_data = {key: input_field.toPlainText() if isinstance(input_field, QTextEdit) else input_field.text()
                    for key, input_field in self.inputs.items()}
        if not all(new_data.values()):
            QMessageBox.warning(self, "Advarsel", "Alle feltene må fylles ut.")
            return

        if self.image_path:
            with open(self.image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                new_data['image'] = encoded_string

        try:
            ssh, remote_file_path = self.connect_to_server()
            sftp = ssh.open_sftp()
            books = self.load_books_from_file(sftp, remote_file_path)

            if book_data:
                for i, book in enumerate(books):
                    if book['name'] == book_data['name']:
                        books[i] = new_data
                        break
            else:
                books.append(new_data)

            self.save_books_to_file(sftp, remote_file_path, books)
            self.parent().load_books()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Feil", str(e))

    def connect_to_server(self):
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
        self.setGeometry(100, 100, 800, 600)  # Increased size for layout adjustments
        self.init_ui()
        self.load_books()

    def init_ui(self):
        # Main layout divided into 2 sections: menu and content
        main_layout = QHBoxLayout()

        # Left menu
        menu_widget = QWidget()
        menu_layout = QVBoxLayout()

        # Add logo/name label
        logo_label = QLabel("Gudenes Bibliotek")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        menu_layout.addWidget(logo_label)

        # Buttons for menu
        buttons = [
            ("Legg til bok", self.open_add_book_dialog),
            ("Slett bok", self.delete_book),
            ("Rediger bok", self.open_edit_book_dialog),
            ("Detaljer", self.show_book_details),
            ("Sync", self.sync_books)
        ]

        for label, slot in buttons:
            button = QPushButton(label)
            button.setStyleSheet("color: white;")  # Make buttons' text white
            button.clicked.connect(slot)
            menu_layout.addWidget(button)

        menu_layout.addStretch()  # Add stretch to push buttons to the top
        menu_widget.setLayout(menu_layout)
        menu_widget.setStyleSheet("background-color: #73A96F; padding: 10px;")

        # Right content section
        content_widget = QWidget()
        content_layout = QVBoxLayout()

        # Create the search bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Søk etter bøker...")
        self.search_bar.textChanged.connect(self.filter_books)
        content_layout.addWidget(self.search_bar)

        # Create the book list
        self.book_list = QListWidget(self)
        content_layout.addWidget(self.book_list)

        content_widget.setLayout(content_layout)
        content_widget.setStyleSheet("background-color: #ECD2A3; padding: 10px;")

        # Add both sections to main layout
        main_layout.addWidget(menu_widget, 1)  # Menu takes up 1/4th of the window width
        main_layout.addWidget(content_widget, 3)  # Content takes up 3/4ths of the window width

        # Set the main layout in a container widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_books(self):
        """Load books from the server and display them in the list."""
        try:
            ssh, remote_file_path = self.connect_to_server()
            sftp = ssh.open_sftp()
            self.books = self.load_books_from_file(sftp, remote_file_path)
            self.update_book_list(self.books)
        except Exception as e:
            QMessageBox.critical(self, "Feil", str(e))

    def sync_books(self):
        """Sync books from the server and refresh the list."""
        self.load_books()

    def filter_books(self):
        """Filter books based on the search input."""
        search_text = self.search_bar.text().lower()
        filtered_books = [book for book in self.books if search_text in book['name'].lower()]
        self.update_book_list(filtered_books)

    def update_book_list(self, books):
        """Update the displayed list of books."""
        self.book_list.clear()
        for book in books:
            self.book_list.addItem(book['name'])

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
            self.books = [book for book in self.books if book['name'] != book_name]
            self.save_books_to_file(sftp, remote_file_path, self.books)
            QMessageBox.information(self, "Suksess", "Boken ble slettet.")
            self.load_books()
        except Exception as e:
            QMessageBox.critical(self, "Feil", str(e))

    def show_book_details(self):
        selected_items = self.book_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Advarsel", "Ingen bok er valgt.")
            return

        book_name = selected_items[0].text()
        book_data = self.get_book_data(book_name)
        if book_data:
            dialog = BookDetailDialog(self, book_data)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Advarsel", "Kunne ikke finne detaljer for denne boken.")

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
