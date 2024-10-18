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
        self.setMinimumSize(300, 400)  # Set minimum size smaller
        self.setStyleSheet("background-color: #D2B48C;")  # Light brown background color
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)  # Normal dialog window

        main_layout = QVBoxLayout()

        # Creating input fields for all book details
        self.book_name_label = QLabel("Book Name:")
        self.book_name_input = QLineEdit()
        main_layout.addWidget(self.book_name_label)
        main_layout.addWidget(self.book_name_input)

        self.genre_label = QLabel("Genre:")
        self.genre_input = QLineEdit()
        main_layout.addWidget(self.genre_label)
        main_layout.addWidget(self.genre_input)

        self.author_label = QLabel("Author:")
        self.author_input = QLineEdit()
        main_layout.addWidget(self.author_label)
        main_layout.addWidget(self.author_input)

        self.summary_label = QLabel("Summary:")
        self.summary_input = QLineEdit()
        main_layout.addWidget(self.summary_label)
        main_layout.addWidget(self.summary_input)

        self.pages_label = QLabel("Pages:")
        self.pages_input = QLineEdit()
        main_layout.addWidget(self.pages_label)
        main_layout.addWidget(self.pages_input)

        self.stock_label = QLabel("Stock:")
        self.stock_input = QLineEdit()
        main_layout.addWidget(self.stock_label)
        main_layout.addWidget(self.stock_input)

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
        book_name = self.book_name_input.text().strip()
        genre = self.genre_input.text().strip()
        author = self.author_input.text().strip()
        summary = self.summary_input.text().strip()
        
        pages = self.pages_input.text().strip()
        stock = self.stock_input.text().strip()
        book_price = self.book_price_input.text().strip()

        # Check for empty fields
        if not book_name or not genre or not author:
            QMessageBox.warning(self, "Feil", "Vennligst fyll ut boknavn, sjanger, og forfatter.")
            return

        # Validate numeric fields
        if not pages.isdigit() or not stock.isdigit() or not self.is_float(book_price):
            QMessageBox.warning(self, "Feil", "Vennligst skriv inn gyldige tall for sider, lager og pris.")
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
            return
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Feil", "Kunne ikke lese JSON-filen fra serveren.")
            return

        # Add the new book to the list
        new_book = {
            "name": book_name,
            "genre": genre,
            "author": author,
            "summary": summary,
            "pages": int(pages),
            "stock": int(stock),
            "price": float(book_price)
        }
        books.append(new_book)

        # Write the updated list back to the server
        try:
            with sftp.open(remote_file_path, 'w') as file:
                json.dump(books, file, indent=4)
            QMessageBox.information(self, "Suksess", "Boken ble lagt til!")
            self.clear_fields()  # Clear input fields after adding
            self.parent().load_books()  # Refresh the book list in the parent window
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke lagre boken på serveren: {str(e)}")

        finally:
            sftp.close()
            ssh.close()

    def is_float(self, value):
        """Check if a string can be converted to a float."""
        try:
            float(value)
            return True
        except ValueError:
            return False

    def clear_fields(self):
        """Clear input fields after adding a book."""
        self.book_name_input.clear()
        self.genre_input.clear()
        self.author_input.clear()
        self.summary_input.clear()
        self.pages_input.clear()
        self.stock_input.clear()
        self.book_price_input.clear()


# Remove Book Dialog Class
class RemoveBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Fjern Bok (Remove Book)")
        self.setMinimumSize(300, 200)
        self.setStyleSheet("background-color: #D2B48C;")  # Light brown background color
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)  # Normal dialog window

        self.layout = QVBoxLayout()
        self.book_name_label = QLabel("Book Name to Remove:")
        self.book_name_input = QLineEdit()
        self.layout.addWidget(self.book_name_label)
        self.layout.addWidget(self.book_name_input)

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_book)
        self.layout.addWidget(self.remove_button)

        self.setLayout(self.layout)

    def remove_book(self):
        """Remove the book from the server."""
        book_name = self.book_name_input.text().strip()

        if not book_name:
            QMessageBox.warning(self, "Feil", "Vennligst oppgi boknavn for å fjerne.")
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
            return
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Feil", "Kunne ikke lese JSON-filen fra serveren.")
            return

        # Find and remove the book
        for i, book in enumerate(books):
            if book['name'] == book_name:
                books.pop(i)
                break
        else:
            QMessageBox.warning(self, "Feil", "Bok ikke funnet.")
            return

        # Write the updated list back to the server
        try:
            with sftp.open(remote_file_path, 'w') as file:
                json.dump(books, file, indent=4)
            QMessageBox.information(self, "Suksess", "Boken ble fjernet!")
            self.parent().load_books()  # Refresh the book list in the parent window
            self.book_name_input.clear()  # Clear input field after removal
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke lagre oppdateringene på serveren: {str(e)}")

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


# Settings Dialog Class
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Innstillinger (Settings)")
        self.setMinimumSize(300, 200)
        self.setStyleSheet("background-color: #D2B48C;")  # Light brown background color
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)  # Normal dialog window

        layout = QVBoxLayout()
        settings_label = QLabel("Settings options can be added here.")
        layout.addWidget(settings_label)

        self.setLayout(layout)


# Main Application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = BookUploader()
    main_window.show()
    sys.exit(app.exec_())
