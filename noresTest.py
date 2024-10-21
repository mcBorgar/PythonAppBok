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
    QListWidget,
    QMenu,
    QAction,
    QTextEdit

    
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor

#Background color var:







#####




# Main Window Class (Home Page)
class BookUploader(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.timer = QTimer(self)  # Create a QTimer instance
        self.timer.timeout.connect(self.load_books)  # Connect to the load_books method
        self.timer.start(5000)  # Check for updates every 5 seconds

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
        settings_button = QPushButton("Innstillinger")  # Settings button

        # Set some styling for the buttons
        button_style = "font-size: 16px; padding: 10px; margin-bottom: 10px;"
        add_button.setStyleSheet(button_style)
        settings_button.setStyleSheet(button_style)

        # Connect buttons to their respective functions
        add_button.clicked.connect(self.open_add_book_dialog)
        settings_button.clicked.connect(self.open_settings_dialog)

        # Add buttons to the button container layout
        button_container.addWidget(add_button)
        button_container.addWidget(settings_button)

        # Left container frame for alignment and styling
        left_container = QFrame()
        left_container.setLayout(button_container)
        left_container.setStyleSheet(f"{left_side_bc_L} padding: 20px;")  # Light brown background

        # Add the left container to the left layout
        left_layout.addWidget(left_container)

        # Right layout for displaying books
        right_layout = QVBoxLayout()
        self.book_list = QListWidget()
        self.book_list.itemClicked.connect(self.on_book_clicked)  # Connect item clicked signal
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

        # Context menu for book list
        self.book_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.book_list.customContextMenuRequested.connect(self.show_context_menu)

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

    def open_settings_dialog(self):
        """Open dialog for settings."""
        settings_dialog = SettingsDialog(self)  # Pass 'self' as parent
        settings_dialog.show()  # Show as non-modal

    def on_book_clicked(self, item):
        """Handle book selection from the list."""
        # Extract the book name from the item text (before the price)
        book_name = item.text().split(" - ")[0]
        self.open_edit_book_dialog(book_name)  # Open edit dialog directly on click

    def show_context_menu(self, pos):
        """Show the context menu for the book list."""
        item = self.book_list.itemAt(pos)
        if item:
            menu = QMenu(self)

            edit_action = QAction("Edit", self)
            edit_action.triggered.connect(lambda: self.open_edit_book_dialog(item.text().split(" - ")[0]))
            menu.addAction(edit_action)

            remove_action = QAction("Remove", self)
            remove_action.triggered.connect(lambda: self.remove_book(item.text().split(" - ")[0]))
            menu.addAction(remove_action)

            menu.exec_(self.book_list.viewport().mapToGlobal(pos))

    def open_edit_book_dialog(self, book_name):
        """Open a dialog to edit the selected book."""
        edit_book_dialog = EditBookDialog(self, book_name)  # Pass 'self' as parent and selected book name
        edit_book_dialog.show()  # Show as non-modal

    def remove_book(self, book_name):
        """Remove the selected book."""
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
            self.load_books()  # Refresh the book list in the parent window
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke lagre oppdateringene på serveren: {str(e)}")

        finally:
            sftp.close()
            ssh.close()


# Add Book Dialog Class
class AddBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Legg til Bok (Add Book)")
        self.setMinimumSize(300, 400)  # Set minimum size smaller
        self.setStyleSheet(red_ins_bc_L)  # Light brown background color
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)  # Normal dialog window

        main_layout = QVBoxLayout()

        # Creating input fields for book details
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Boknavn (Book Name)")

        self.author_input = QLineEdit(self)
        self.author_input.setPlaceholderText("Forfatter (Author)")

        self.pages_input = QLineEdit(self)
        self.pages_input.setPlaceholderText("Antall sider (Pages)")

        self.genre_input = QLineEdit(self)
        self.genre_input.setPlaceholderText("Sjanger (Genre)")

        self.summary_input = QLineEdit(self)
        self.summary_input.setPlaceholderText("Sammendrag (Summary)")

        self.price_input = QLineEdit(self)
        self.price_input.setPlaceholderText("Pris (Price)")

        self.stock_input = QLineEdit(self)
        self.stock_input.setPlaceholderText("Antall på lager (Stock)")

        # Adding the input fields to the main layout
        main_layout.addWidget(self.name_input)
        main_layout.addWidget(self.author_input)
        main_layout.addWidget(self.pages_input)
        main_layout.addWidget(self.genre_input)
        main_layout.addWidget(self.summary_input)
        main_layout.addWidget(self.price_input)
        main_layout.addWidget(self.stock_input)

        add_button = QPushButton("Legg til Bok (Add Book)", self)
        add_button.clicked.connect(self.add_book)
        main_layout.addWidget(add_button)

        self.setLayout(main_layout)

    def add_book(self):
        """Add book to the server."""
        book = {
            "name": self.name_input.text(),
            "author": self.author_input.text(),
            "pages": self.pages_input.text(),
            "genre": self.genre_input.text(),
            "summary": self.summary_input.text(),
            "price": self.price_input.text(),
            "stock": self.stock_input.text()
        }

        # Attempt to connect to the server
        try:
            ssh, remote_file_path = self.connect_to_server()
            sftp = ssh.open_sftp()
        except Exception as e:
            QMessageBox.critical(self, "Serverfeil", f"Kunne ikke koble til serveren: {str(e)}")
            return

        # Read the existing books
        try:
            with sftp.open(remote_file_path, 'r') as file:
                books = json.load(file)
        except FileNotFoundError:
            # If file doesn't exist, start with an empty list
            books = []
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Feil", "Kunne ikke lese JSON-filen fra serveren.")
            return

        # Add the new book
        books.append(book)

        # Write the updated list back to the server
        try:
            with sftp.open(remote_file_path, 'w') as file:
                json.dump(books, file, indent=4)
            QMessageBox.information(self, "Suksess", "Boken ble lagt til!")  # Success message
            self.accept()  # Close the dialog on success
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke lagre boken på serveren: {str(e)}")
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


# Edit Book Dialog Class
class EditBookDialog(QDialog):
    def __init__(self, parent, book_name):
        super().__init__(parent)
        self.book_name = book_name
        self.init_ui()
        self.load_book_details()

    def init_ui(self):
        self.setWindowTitle("Rediger Bok (Edit Book)")
        self.setMinimumSize(300, 400)  # Set minimum size smaller
        self.setStyleSheet(red_ins_bc_L)  # Light brown background color
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)  # Normal dialog window

        main_layout = QVBoxLayout()

        # Creating input fields for book details
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Boknavn (Book Name)")

        self.author_input = QLineEdit(self)
        self.author_input.setPlaceholderText("Forfatter (Author)")

        self.pages_input = QLineEdit(self)
        self.pages_input.setPlaceholderText("Antall sider (Pages)")

        self.genre_input = QLineEdit(self)
        self.genre_input.setPlaceholderText("Sjanger (Genre)")

        self.summary_input = QLineEdit(self)
        self.summary_input.setPlaceholderText("Sammendrag (Summary)")

        self.price_input = QLineEdit(self)
        self.price_input.setPlaceholderText("Pris (Price)")

        self.stock_input = QLineEdit(self)
        self.stock_input.setPlaceholderText("Antall på lager (Stock)")

        # Adding the input fields to the main layout
        main_layout.addWidget(self.name_input)
        main_layout.addWidget(self.author_input)
        main_layout.addWidget(self.pages_input)
        main_layout.addWidget(self.genre_input)
        main_layout.addWidget(self.summary_input)
        main_layout.addWidget(self.price_input)
        main_layout.addWidget(self.stock_input)

        save_button = QPushButton("Lagre endringer (Save Changes)", self)
        save_button.clicked.connect(self.save_changes)
        main_layout.addWidget(save_button)

        self.setLayout(main_layout)

    def load_book_details(self):
        """Load the book details into the input fields."""
        try:
            ssh, remote_file_path = self.connect_to_server()
            sftp = ssh.open_sftp()
            with sftp.open(remote_file_path, 'r') as file:
                books = json.load(file)

            # Find the book by name
            for book in books:
                if book['name'] == self.book_name:
                    self.name_input.setText(book['name'])
                    self.author_input.setText(book.get('author', ''))
                    self.pages_input.setText(book.get('pages', ''))
                    self.genre_input.setText(book.get('genre', ''))
                    self.summary_input.setText(book.get('summary', ''))
                    self.price_input.setText(book['price'])
                    self.stock_input.setText(book.get('stock', ''))
                    break
            else:
                QMessageBox.warning(self, "Feil", "Boken ble ikke funnet.")
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke laste boken: {str(e)}")
        finally:
            sftp.close()
            ssh.close()

    def save_changes(self):
        """Save the changes made to the book."""
        updated_book = {
            "name": self.name_input.text(),
            "author": self.author_input.text(),
            "pages": self.pages_input.text(),
            "genre": self.genre_input.text(),
            "summary": self.summary_input.text(),
            "price": self.price_input.text(),
            "stock": self.stock_input.text()
        }

        try:
            ssh, remote_file_path = self.connect_to_server()
            sftp = ssh.open_sftp()
            with sftp.open(remote_file_path, 'r') as file:
                books = json.load(file)

            # Find the book to update
            for i, book in enumerate(books):
                if book['name'] == self.book_name:
                    books[i] = updated_book  # Update book information
                    break
            else:
                QMessageBox.warning(self, "Feil", "Boken ble ikke funnet.")
                return

            # Write the updated list back to the server
            with sftp.open(remote_file_path, 'w') as file:
                json.dump(books, file, indent=4)
            QMessageBox.information(self, "Suksess", "Endringer lagret!")  # Success message
            self.accept()  # Close the dialog on success
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke lagre endringene: {str(e)}")
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
        self.setMinimumSize(300, 200)  # Set minimum size smaller
        self.setStyleSheet(red_ins_bc_L)  # Light brown background color

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Innstillinger vil komme snart."))  # Placeholder text
        self.setLayout(layout)


# Main execution
if __name__ == "__main__":
    red_ins_bc_L = ("background-color: #D2B48C;")
    left_side_bc_L =("background-color: #F0EAD6;")
    app = QApplication(sys.argv)
    window = BookUploader()
    tekst = QTextEdit()
    #tekst_bc_L = tekst.setTextColor(QColor("white"))
    app.setStyleSheet("QLabel, QTextEdit {color: white; }")
    window.show()
    sys.exit(app.exec_())
