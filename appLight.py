import sys
import json
import paramiko
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QListWidget, QPushButton, QLineEdit, QLabel, QMessageBox, QTextEdit, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# Main Application Class
class MainApp(QMainWindow): 
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bok Database")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()
        self.load_books()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # Left-side menu
        menu_layout = QVBoxLayout()

        # App name/logo with text "Gudenes Bibliotek"
        library_label = QLabel("Gudenes\nBibliotek")
        library_label.setFont(QFont("Arial", 25, QFont.Bold))
        library_label.setAlignment(Qt.AlignTop)
        menu_layout.addWidget(library_label)

        # Menu buttons
        buttons = [
            ("Legg til bok", self.open_add_book_dialog),
            ("Slett bok", self.delete_book),
            ("Rediger bok", self.open_edit_book_dialog),
            ("Detaljer", self.show_book_details),
            ("Sync", self.sync_books)
        ]

        for label, slot in buttons:
            button = QPushButton(label)
            button.clicked.connect(slot)
            
            # Bruk gyldig stilark for QPushButton
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    text-align: left;
                    padding-right: 10px;
                    border: none;
                    font-family: roboto;
                    font-size: 20px;
                    font-weight: semibold;
                }
            """)
            
            menu_layout.addWidget(button)

        menu_layout.addStretch()


        # Create a container for the menu and set its width
        menu_container = QWidget()
        menu_container.setLayout(menu_layout)
        menu_container.setFixedWidth(200)

        # Right-side layout
        right_layout = QVBoxLayout()

        # Search bar and "Sjangere" button
        top_right_layout = QHBoxLayout()
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Søk etter bøker...")
        self.search_bar.textChanged.connect(self.filter_books)
        self.search_bar.setStyleSheet("background-color: #F0F0F0;")  # Grå/hvit bakgrunn for søkefeltet
        top_right_layout.addWidget(self.search_bar)

        genre_button = QPushButton("Sjangere")
        genre_button.setStyleSheet("background-color: #B7C8B5; padding: 10px;")
        top_right_layout.addWidget(genre_button)

        right_layout.addLayout(top_right_layout)

        # Book list
        self.book_list = QListWidget(self)
        right_layout.addWidget(self.book_list)
        self.book_list.setStyleSheet("background-color: #ECD2A3;")  # Bakgrunnsfarge for boklisten

        # Combine left menu and right content
        main_layout.addWidget(menu_container)
        main_layout.addLayout(right_layout)

        # Set the layout to the main widget
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        main_widget.setStyleSheet("background-color: #73A96F;")  # Endre fargen her
        self.setCentralWidget(main_widget)

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
        """Show details of the selected book."""
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

# Book Dialog for adding/editing books
class BookDialog(QMessageBox):
    def __init__(self, parent, title, book_data=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.book_data = book_data

        self.name_field = QLineEdit(self)
        self.name_field.setPlaceholderText("Boknavn")
        self.layout().addWidget(self.name_field)

        self.price_field = QLineEdit(self)
        self.price_field.setPlaceholderText("Pris")
        self.layout().addWidget(self.price_field)

        if book_data:
            self.name_field.setText(book_data['name'])
            self.price_field.setText(str(book_data['price']))

        self.addButton(QMessageBox.Ok)
        self.addButton(QMessageBox.Cancel)

# Book Detail Dialog for showing details of a selected book
class BookDetailDialog(QMessageBox):
    def __init__(self, parent, book_data):
        super().__init__(parent)
        self.setWindowTitle("Detaljer")

        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        self.text_area.setText(f"Navn: {book_data['name']}\nPris: {book_data['price']}")

        self.layout().addWidget(self.text_area)

# Entry point for the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
