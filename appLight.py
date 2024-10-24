import sys
import json
import paramiko
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QListWidget, QPushButton, QLineEdit, QLabel, QMessageBox, QTextEdit, QDialog
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer

# Main Application Class
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bok Database")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()
        # Timer to refresh book list
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_books)
        self.timer.start(5000)
        self.load_books()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # Left-side menu
        menu_layout = QVBoxLayout()

        # App name/logo with text "Gudenes Bibliotek"
        self.create_library_label(menu_layout)

        # Menu buttons
        self.create_menu_buttons(menu_layout)

        menu_layout.addStretch()

        # Create a container for the menu and set its width
        menu_container = QWidget()
        menu_container.setLayout(menu_layout)
        menu_container.setFixedWidth(240)
        menu_container.setStyleSheet("background-color: #73A96F; padding: 20px;")

        # Right-side layout
        right_layout = QVBoxLayout()

        # Search bar and "Sjangere" button
        self.create_search_bar(right_layout)

        # Book list
        self.book_list = QListWidget(self)
        self.book_list.setStyleSheet("background-color: #ECD2A3;")
        self.book_list.itemClicked.connect(self.on_book_clicked)
        right_layout.addWidget(self.book_list)

        # Create a splitter to separate left and right content
        splitter = QSplitter(Qt.Horizontal)
        left_frame = menu_container
        right_frame = QFrame()
        right_frame.setLayout(right_layout)

        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([240, 960])

        main_layout.addWidget(splitter)
        self.load_books()

        # Set the layout to the main widget
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def create_library_label(self, layout):
        library_label = QLabel("Gudenes\nBibliotek")
        library_label.setFont(QFont("Roboto", 25, QFont.Bold))
        library_label.setAlignment(Qt.AlignTop)
        layout.addWidget(library_label)

    def create_menu_buttons(self, layout):
        buttons = [
            ("Legg til bok", self.open_add_book_dialog),
            ("Slett bok", self.delete_book),
            ("Rediger bok", self.open_edit_book_dialog),
            ("Detaljer", self.show_book_details),
            ("Sync", self.sync_books)
        ]

        button_font = QFont("Roboto", 20, QFont.Bold)
        button_style = "background-color: transparent; text-align: left; padding: 10px; border: none; font-family: Roboto; font-size: 20px; font-weight: bold;"

        for label, slot in buttons:
            button = QPushButton(label)
            button.clicked.connect(slot)
            button.setFont(button_font)
            button.setStyleSheet(button_style)
            layout.addWidget(button)

    def create_search_bar(self, layout):
        top_right_layout = QHBoxLayout()
        
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Søk etter bøker...")
        self.search_bar.textChanged.connect(self.filter_books)
        self.search_bar.setStyleSheet("background-color: #F0F0F0;")
        top_right_layout.addWidget(self.search_bar)

        genre_button = QPushButton("Sjangere")
        genre_button.setFont(QFont("Roboto", 20, QFont.Bold))
        genre_button.setStyleSheet("background-color: #B7C8B5; padding: 10px;")
        top_right_layout.addWidget(genre_button)

        layout.addLayout(top_right_layout)

    def load_books(self):
        """Load books from the server and display them in the list."""
        try:
            ssh, remote_file_path = self.connect_to_server()
            sftp = ssh.open_sftp()
            self.books = self.load_books_from_file(sftp, remote_file_path)
            self.update_book_list(self.books)
        except Exception as e:
            QMessageBox.critical(self, "Feil", str(e))
        finally:
            if 'sftp' in locals():
                sftp.close()
            if 'ssh' in locals():
                ssh.close()

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
            self.book_list.addItem(f"{book['name']} - {book['price']} NOK")

    def open_add_book_dialog(self):
        dialog = BookDialog(self, "Legg til bok")
        if dialog.exec_() == QDialog.Accepted:
            new_book = dialog.get_book_data()
            if new_book:
                self.add_book_to_server(new_book)

    def add_book_to_server(self, book_data):
        """Add a new book to the server."""
        try:
            ssh, remote_file_path = self.connect_to_server()
            sftp = ssh.open_sftp()
            self.books.append(book_data)
            self.save_books_to_file(sftp, remote_file_path, self.books)
            QMessageBox.information(self, "Suksess", "Boken ble lagt til.")
            self.load_books()  # Refresh the book list
        except Exception as e:
            QMessageBox.critical(self, "Feil", str(e))
        finally:
            sftp.close()
            ssh.close()

    def delete_book(self):
        selected_items = self.book_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Advarsel", "Ingen bok er valgt.")
            return

        book_name = selected_items[0].text().split(" - ")[0]
        try:
            ssh, remote_file_path = self.connect_to_server()
            sftp = ssh.open_sftp()
            self.books = [book for book in self.books if book['name'] != book_name]
            self.save_books_to_file(sftp, remote_file_path, self.books)
            QMessageBox.information(self, "Suksess", "Boken ble slettet.")
            self.load_books()
        except Exception as e:
            QMessageBox.critical(self, "Feil", str(e))
        finally:
            sftp.close()
            ssh.close()

    def show_book_details(self):
        """Show details of the selected book."""
        selected_items = self.book_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Advarsel", "Ingen bok er valgt.")
            return

        book_name = selected_items[0].text().split(" - ")[0]
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
        finally:
            sftp.close()
            ssh.close()
        return None

    def connect_to_server(self):
        """Connect to the server."""
        server_ip = '192.168.1.218'
        username = 'bok'
        password = 'bok'
        remote_file_path = '/home/bok/books.json'

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_ip, username=username, password=password)

        return ssh, remote_file_path
