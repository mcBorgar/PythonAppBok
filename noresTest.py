import paramiko
import json
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QDialog
from PyQt5.QtCore import Qt

# Main Window Class (Home Page)
class BookUploader(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Library App - Home")
        self.setGeometry(100, 100, 300, 200)  # Set the main window size

        # Main layout
        self.layout = QVBoxLayout()

        # Initialize all the different pages (Add, Remove, Settings)
        self.init_home_page()

        # Buttons for navigation
        add_button = QPushButton("Legg til")  # Add book button
        remove_button = QPushButton("Fjern")  # Remove book button
        settings_button = QPushButton("Innstillinger")  # Settings button

        # Connect buttons to their respective functions
        add_button.clicked.connect(self.open_add_book_dialog)
        remove_button.clicked.connect(self.open_remove_book_dialog)
        settings_button.clicked.connect(self.open_settings_dialog)

        # Add buttons to the layout
        self.layout.addWidget(add_button)
        self.layout.addWidget(remove_button)
        self.layout.addWidget(settings_button)

        # Set the layout to the main widget
        self.setLayout(self.layout)

    def init_home_page(self):
        """Initialize the home page layout."""
        home_label = QLabel("Welcome to the Library App!")
        self.layout.addWidget(home_label)  # Add home label to the layout

    def open_add_book_dialog(self):
        """Open a dialog to add a book."""
        self.add_book_dialog = AddBookDialog()  # Create an instance of AddBookDialog
        self.add_book_dialog.exec_()  # Show dialog as a modal popup

    def open_remove_book_dialog(self):
        """Open a dialog to remove a book."""
        self.remove_book_dialog = RemoveBookDialog()  # Create an instance of RemoveBookDialog
        self.remove_book_dialog.exec_()  # Show dialog as a modal popup

    def open_settings_dialog(self):
        """Open a dialog for settings."""
        self.settings_dialog = SettingsDialog()  # Create an instance of SettingsDialog
        self.settings_dialog.exec_()  # Show dialog as a modal popup


# Add Book Dialog Class
class AddBookDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Legg til Bok (Add Book)")
        self.setGeometry(150, 150, 300, 200)  # Set the dialog size
        self.setStyleSheet("background-color: #D2B48C;")  # Light brown background color
        self.setModal(True)  # Make this dialog modal

        layout = QVBoxLayout()

        # Book Name Input
        self.book_name_label = QLabel("Book Name:")
        self.book_name_input = QLineEdit()
        layout.addWidget(self.book_name_label)
        layout.addWidget(self.book_name_input)

        # Book Price Input
        self.book_price_label = QLabel("Book Price:")
        self.book_price_input = QLineEdit()
        layout.addWidget(self.book_price_label)
        layout.addWidget(self.book_price_input)

        # Upload Button
        self.upload_button = QPushButton("OK")
        self.upload_button.clicked.connect(self.upload_book)
        layout.addWidget(self.upload_button)

        # Set the layout for the dialog
        self.setLayout(layout)

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

    def upload_book(self):
        """Upload the book to the server."""
        book_name = self.book_name_input.text()
        book_price = self.book_price_input.text()

        if not book_name or not book_price:
            print("Please enter both name and price.")
            return

        # Connect to the server
        ssh, remote_file_path = self.connect_to_server()
        sftp = ssh.open_sftp()

        # Read the JSON file from the server
        with sftp.open(remote_file_path, 'r') as file:
            books = json.load(file)

        # Create a new book entry
        new_book = {
            "name": book_name,
            "price": book_price
        }
        books.append(new_book)

        # Write the updated list back to the server
        with sftp.open(remote_file_path, 'w') as file:
            json.dump(books, file, indent=4)

        sftp.close()
        ssh.close()

        print("Updated books:", books)
        self.book_name_input.clear()
        self.book_price_input.clear()


# Remove Book Dialog Class
class RemoveBookDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Fjern Bok (Remove Book)")
        self.setGeometry(150, 150, 300, 200)  # Set the dialog size
        self.setStyleSheet("background-color: #D2B48C;")  # Light brown background color
        self.setModal(True)  # Make this dialog modal

        layout = QVBoxLayout()

        # Placeholder label for removing books functionality
        self.remove_label = QLabel("Remove Book Functionality - Coming Soon!")
        layout.addWidget(self.remove_label)

        # Set the layout for the dialog
        self.setLayout(layout)


# Settings Dialog Class
class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Innstillinger (Settings)")
        self.setGeometry(150, 150, 300, 200)  # Set the dialog size
        self.setStyleSheet("background-color: #D2B48C;")  # Light brown background color
        self.setModal(True)  # Make this dialog modal

        layout = QVBoxLayout()

        # Placeholder label for settings functionality
        self.settings_label = QLabel("Settings Functionality - Coming Soon!")
        layout.addWidget(self.settings_label)

        # Set the layout for the dialog
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    uploader = BookUploader()
    uploader.show()
    sys.exit(app.exec_())