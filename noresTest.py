import paramiko
import json
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QDialog,
    QHBoxLayout,
    QFrame,
    QSplitter,
    QMessageBox,
    QListWidget
)
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

        # Right layout for displaying books
        right_layout = QVBoxLayout()
        self.book_list = QListWidget()
        right_layout.addWidget(self.book_list)

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

        # Load existing books into the list
        self.load_books()

    def load_books(self):
        """Load books from the server and display them in the list."""
        try:
            ssh, remote_file_path = self.connect_to_server()
            sftp = ssh.open_sftp()
            with sftp.open(remote_file_path, 'r') as file:
                books = json.load(file)

            # Clear the current list and add all book names with prices
            self.book_list.clear()
            if isinstance(books, list):  # Ensure books is a list
                for book in books:
                    self.book_list.addItem(f"{book['name']} - {book['price']} NOK")
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke laste bøker: {str(e)}")
        finally:
            sftp.close()
            ssh.close()

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

    def open_add_book_dialog(self):
        """Open a dialog to add a book."""
        add_book_dialog = AddBookDialog(self)  # Pass 'self' as parent
        add_book_dialog.show()  # Show as non-modal

    def open_remove_book_dialog(self):
        """Open a dialog to remove a book."""
        remove_book_dialog = RemoveBookDialog(self)  # Pass 'self' as parent
        remove_book_dialog.show()  # Show as non-modal

    def open_settings_dialog(self):
        """Open dialog for settings."""
        settings_dialog = SettingsDialog(self)  # Pass 'self' as parent
        settings_dialog.show()  # Show as non-modal


# Add Book Dialog Class
class AddBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Legg til Bok (Add Book)")
        self.setMinimumSize(300, 200)  # Set minimum size smaller
        self.setStyleSheet("background-color: #D2B48C;")  # Light brown background color
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)  # Normal dialog window

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
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Feil", "JSON-filen er ugyldig eller kan ikke leses.")
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke lese JSON-filen: {str(e)}")
        else:
            # Ensure books is a list
            if isinstance(books, dict):
                books = []  # Initialize books as an empty list if it's a dict

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
                self.parent().load_books()  # Refresh the book list
                QMessageBox.information(self, "Suksess", "Boken har blitt lagt til.")
                self.book_name_input.clear()
                self.book_price_input.clear()
            except Exception as e:
                QMessageBox.critical(self, "Feil", f"Kunne ikke skrive til JSON-filen: {str(e)}")
                return
        finally:
            sftp.close()
            ssh.close()


# Remove Book Dialog Class
class RemoveBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Fjern Bok (Remove Book)")
        self.setMinimumSize(300, 200)  # Set minimum size smaller
        self.setStyleSheet("background-color: #D2B48C;")  # Light brown background color
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)  # Normal dialog window

        main_layout = QVBoxLayout()

        self.book_name_label = QLabel("Book Name:")
        self.book_name_input = QLineEdit()
        main_layout.addWidget(self.book_name_label)
        main_layout.addWidget(self.book_name_input)

        self.remove_button = QPushButton("Fjern")
        self.remove_button.clicked.connect(self.remove_book)
        main_layout.addWidget(self.remove_button)

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

    def remove_book(self):
        """Remove the book from the server."""
        book_name = self.book_name_input.text()

        if not book_name:
            QMessageBox.warning(self, "Feil", "Vennligst skriv inn boknavn.")
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
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Feil", "JSON-filen er ugyldig eller kan ikke leses.")
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke lese JSON-filen: {str(e)}")
        else:
            # Find the book to remove
            books = [book for book in books if book['name'] != book_name]

            # Write the updated list back to the server
            try:
                with sftp.open(remote_file_path, 'w') as file:
                    json.dump(books, file, indent=4)
                self.parent().load_books()  # Refresh the book list
                QMessageBox.information(self, "Suksess", "Boken har blitt fjernet.")
                self.book_name_input.clear()
            except Exception as e:
                QMessageBox.critical(self, "Feil", f"Kunne ikke skrive til JSON-filen: {str(e)}")
                return
        finally:
            sftp.close()
            ssh.close()


# Settings Dialog Class
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Innstillinger (Settings)")
        self.setMinimumSize(300, 200)  # Set minimum size smaller
        self.setStyleSheet("background-color: #D2B48C;")  # Light brown background color
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)  # Normal dialog window

        main_layout = QVBoxLayout()

        self.server_ip_label = QLabel("Server IP:")
        self.server_ip_input = QLineEdit("192.168.1.218")
        main_layout.addWidget(self.server_ip_label)
        main_layout.addWidget(self.server_ip_input)

        self.username_label = QLabel("Brukernavn (Username):")
        self.username_input = QLineEdit("bok")
        main_layout.addWidget(self.username_label)
        main_layout.addWidget(self.username_input)

        self.password_label = QLabel("Passord (Password):")
        self.password_input = QLineEdit("bok")
        self.password_input.setEchoMode(QLineEdit.Password)  # Hide password input
        main_layout.addWidget(self.password_label)
        main_layout.addWidget(self.password_input)

        self.save_button = QPushButton("Lagre (Save)")
        self.save_button.clicked.connect(self.save_settings)
        main_layout.addWidget(self.save_button)

        self.setLayout(main_layout)

    def save_settings(self):
        """Save settings logic (you can expand this as needed)."""
        server_ip = self.server_ip_input.text()
        username = self.username_input.text()
        password = self.password_input.text()

        # Here, you could save these settings to a config file or similar.
        # For now, just show a message box.
        QMessageBox.information(self, "Innstillinger Lagret", f"IP: {server_ip}\nBrukernavn: {username}\nPassord: {password}")


# Main entry point
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = BookUploader()
    main_window.show()
    sys.exit(app.exec_())
