import paramiko
import json
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QDialog, QHBoxLayout, QFrame, QSplitter, QMessageBox
from PyQt5.QtCore import Qt

# Main Window Class (Home Page)
class BookUploader(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Library App - Home")
        self.setGeometry(100, 100, 1200, 800)  # Increased main window size

        # Create main horizontal layout
        main_layout = QHBoxLayout()

        # Left side layout for buttons and headline
        left_layout = QVBoxLayout()
        headline = QLabel("Bibliotek")
        headline.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")

        # Create a vertical layout for the buttons
        button_container = QVBoxLayout()

        # Add headline and buttons to the left side
        button_container.addWidget(headline)

        # Buttons for navigation
        add_button = QPushButton("Legg til")  # Add book button
        remove_button = QPushButton("Fjern")  # Remove book button
        settings_button = QPushButton("Innstillinger")  # Settings button

        # Set some styling for the buttons
        button_style = "font-size: 16px; padding: 10px; margin-bottom: 10px;"
        add_button.setStyleSheet(button_style)
        remove_button.setStyleSheet(button_style)
        settings_button.setStyleSheet(button_style)

        # Connect buttons to their respective functions
        add_button.clicked.connect(self.open_add_book_dialog)
        remove_button.clicked.connect(self.open_remove_book_dialog)
        settings_button.clicked.connect(self.open_settings_dialog)

        # Add buttons to the button container layout
        button_container.addWidget(add_button)
        button_container.addWidget(remove_button)
        button_container.addWidget(settings_button)

        # Left container frame for alignment and styling
        left_container = QFrame()
        left_container.setLayout(button_container)
        left_container.setStyleSheet("background-color: #F0EAD6; padding: 20px;")  # Light brown background

        # Add the left container to the left layout
        left_layout.addWidget(left_container)

        # Right layout (placeholder for future objects)
        right_layout = QVBoxLayout()
        right_placeholder = QLabel("Right side content goes here")
        right_placeholder.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(right_placeholder)

        # Create a QSplitter to allow resizing between the left and right sections
        splitter = QSplitter(Qt.Horizontal)

        # Create left and right containers
        left_frame = QFrame()
        left_frame.setLayout(left_layout)
        right_frame = QFrame()
        right_frame.setLayout(right_layout)

        # Add frames to the splitter
        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)

        # Set the relative size (20% for the left, 80% for the right)
        splitter.setSizes([240, 960])  # Adjust size ratio (20% for left, 80% for right)

        # Add the splitter to the main layout
        main_layout.addWidget(splitter)

        # Set the layout for the main window
        self.setLayout(main_layout)

    def open_add_book_dialog(self):
        """Open a dialog to add a book."""
        self.add_book_dialog = AddBookDialog(self)  # Pass 'self' as parent to lock the popup to this window
        self.add_book_dialog.exec_()  # Show dialog as a modal popup

    def open_remove_book_dialog(self):
        """Open a dialog to remove a book."""
        self.remove_book_dialog = RemoveBookDialog(self)  # Pass 'self' as parent
        self.remove_book_dialog.exec_()  # Show dialog as a modal popup

    def open_settings_dialog(self):
        """Open dialog for settings."""
        self.settings_dialog = SettingsDialog(self)  # Pass 'self' as parent
        self.settings_dialog.exec_()  # Show dialog as a modal popup


# Add Book Dialog Class
class AddBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Legg til Bok (Add Book)")
        self.setMinimumSize(300, 200)  # Set a minimum size
        self.setStyleSheet("background-color: #D2B48C;")  # Light brown background color

        main_layout = QVBoxLayout()

        self.book_name_label = QLabel("Book Name:")
        self.book_name_input = QLineEdit()
        main_layout.addWidget(self.book_name_label)
        main_layout.addWidget(self.book_name_input)

        self.book_price_label = QLabel("Book Price:")
        self.book_price_input = QLineEdit()
        main_layout.addWidget(self.book_price_label)
        main_layout.addWidget(self.book_price_input)

        self.upload_button = QPushButton("OK")
        self.upload_button.clicked.connect(self.upload_book)
        main_layout.addWidget(self.upload_button)

        self.setLayout(main_layout)

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
            QMessageBox.warning(self, "Feil", "Vennligst skriv inn både navn og pris.")
            return

        # Attempt to connect to the server
        try:
            ssh, remote_file_path = self.connect_to_server()
            sftp = ssh.open_sftp()
        except Exception as e:
            QMessageBox.critical(self, "Serverfeil", f"Kunne ikke koble til serveren: {str(e)}")
            return

        # Read the JSON file from the server
        try:
            with sftp.open(remote_file_path, 'r') as file:
                books = json.load(file)
        except FileNotFoundError:
            QMessageBox.critical(self, "Feil", "JSON-filen finnes ikke på serveren.")
            sftp.close()
            ssh.close()
            return
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Feil", "JSON-filen er ugyldig eller kan ikke leses.")
            sftp.close()
            ssh.close()
            return
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke lese JSON-filen: {str(e)}")
            sftp.close()
            ssh.close()
            return

        # Create a new book entry
        new_book = {
            "name": book_name,
            "price": book_price
        }
        books.append(new_book)

        # Write the updated list back to the server
        try:
            with sftp.open(remote_file_path, 'w') as file:
                json.dump(books, file, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke skrive til JSON-filen: {str(e)}")
            sftp.close()
            ssh.close()
            return

        sftp.close()
        ssh.close()

        print("Oppdaterte bøker:", books)
        self.book_name_input.clear()
        self.book_price_input.clear()
        QMessageBox.information(self, "Suksess", "Boken har blitt lagt til.")


# Remove Book Dialog Class
class RemoveBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_books()  # Load the books from the server

    def init_ui(self):
        self.setWindowTitle("Fjern Bok (Remove Book)")
        self.setMinimumSize(300, 200)  # Set a minimum size
        self.setStyleSheet("background-color: #D2B48C;")  # Light brown background color

        main_layout = QVBoxLayout()

        self.book_list_label = QLabel("Select a book to remove:")
        main_layout.addWidget(self.book_list_label)

        self.book_name_input = QLineEdit()  # Input field to type the book name
        main_layout.addWidget(self.book_name_input)

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_book)
        main_layout.addWidget(self.remove_button)

        self.setLayout(main_layout)

    def load_books(self):
        """Load books from the server."""
        try:
            ssh, remote_file_path = self.connect_to_server()
            sftp = ssh.open_sftp()
            with sftp.open(remote_file_path, 'r') as file:
                self.books = json.load(file)
            sftp.close()
            ssh.close()
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke laste bøker: {str(e)}")
            self.books = []

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

    def remove_book(self):
        """Remove a book from the server."""
        book_name = self.book_name_input.text()

        if not book_name:
            QMessageBox.warning(self, "Feil", "Vennligst skriv inn navnet på boken som skal fjernes.")
            return

        if book_name not in [book['name'] for book in self.books]:
            QMessageBox.warning(self, "Feil", "Boken ble ikke funnet.")
            return

        # Remove the book
        self.books = [book for book in self.books if book['name'] != book_name]

        try:
            ssh, remote_file_path = self.connect_to_server()
            sftp = ssh.open_sftp()
            with sftp.open(remote_file_path, 'w') as file:
                json.dump(self.books, file, indent=4)
            sftp.close()
            ssh.close()
            QMessageBox.information(self, "Suksess", "Boken har blitt fjernet.")
            self.book_name_input.clear()  # Clear input field
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke oppdatere JSON-filen: {str(e)}")


# Settings Dialog Class (optional)
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Innstillinger (Settings)")
        self.setMinimumSize(300, 200)  # Set a minimum size
        self.setStyleSheet("background-color: #D2B48C;")  # Light brown background color

        main_layout = QVBoxLayout()

        # Add settings options here
        self.settings_label = QLabel("Settings will be implemented here.")
        main_layout.addWidget(self.settings_label)

        self.setLayout(main_layout)


# Main entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = BookUploader()
    main_window.show()
    sys.exit(app.exec_())
