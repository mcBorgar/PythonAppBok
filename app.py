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
    QAction
)
from PyQt5.QtCore import Qt, QTimer


# Main Window Class (Home Page)
class BookUploader(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.timer = QTimer(self)  # Create a QTimer instance
        self.timer.timeout.connect(self.load_books)  # Connect to the load_books method
        self.timer.start(5000)  # Check for updates every 5 seconds

    def init_ui(self):
        self.setWindowTitle("Library App")
        self.setGeometry(100, 100, 1200, 800)  # Increased main window size

        # Create main horizontal layout
        main_layout = QHBoxLayout()

        # Left side layout for buttons and headline
        left_layout = QVBoxLayout()
        headline = QLabel("GUDENES \n  BIBLIOTEK")
        headline.setStyleSheet("font-size: 40px; font-weight: bold; margin-bottom: 0px; padding: 0px;")

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
        left_container.setStyleSheet("background-color: #F0EAD6; padding: 20px;")  # Light brown background

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
        
        # Ask the user if they want to edit or delete the book
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Choose Action")
        msg_box.setText(f"Do you want to edit or delete '{book_name}'?")
        edit_button = msg_box.addButton("Edit", QMessageBox.AcceptRole)
        delete_button = msg_box.addButton("Delete", QMessageBox.RejectRole)
        cancel_button = msg_box.addButton("Cancel", QMessageBox.DestructiveRole)
        
        msg_box.exec_()
        
        # Perform actions based on user selection
        if msg_box.clickedButton() == edit_button:
            self.open_edit_book_dialog(book_name)  # Open edit dialog
        elif msg_box.clickedButton() == delete_button:
            self.remove_book(book_name)  # Remove the book

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


# Opprette og 
class AddBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Legg til Bok (Add Book)")
        self.setMinimumSize(300, 400)  # Set minimum size smaller
        self.setStyleSheet("background-color: #E8EAF6;")

        layout = QVBoxLayout()

        name_label = QLabel("Navn på Bok (Book Name):")
        self.name_input = QLineEdit()
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)

        price_label = QLabel("Pris (Price):")
        self.price_input = QLineEdit()
        layout.addWidget(price_label)
        layout.addWidget(self.price_input)

        add_button = QPushButton("Legg til Bok")
        add_button.clicked.connect(self.add_book)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def add_book(self):
        book_name = self.name_input.text()
        book_price = self.price_input.text()

        if not book_name or not book_price:
            QMessageBox.warning(self, "Feil", "Begge feltene må fylles ut.")
            return

        try:
            ssh, remote_file_path = self.parent().connect_to_server()
            sftp = ssh.open_sftp()

            try:
                with sftp.open(remote_file_path, 'r') as file:
                    books = json.load(file)
            except FileNotFoundError:
                books = []
            except json.JSONDecodeError:
                QMessageBox.critical(self, "Feil", "Kunne ikke lese JSON-filen fra serveren.")
                return

            books.append({"name": book_name, "price": book_price})

            with sftp.open(remote_file_path, 'w') as file:
                json.dump(books, file, indent=4)

            QMessageBox.information(self, "Suksess", "Bok lagt til!")

            self.parent().load_books()  # Refresh the book list in the parent window

        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke koble til serveren: {str(e)}")

        finally:
            sftp.close()
            ssh.close()

        self.close()


# Edit Book Dialog Class
class EditBookDialog(QDialog):
    def __init__(self, parent=None, book_name=None):
        super().__init__(parent)
        self.book_name = book_name
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Rediger Bok - {self.book_name}")
        self.setMinimumSize(300, 400)
        self.setStyleSheet("background-color: #FFF3E0;")

        layout = QVBoxLayout()

        name_label = QLabel("Nytt Navn på Bok (New Book Name):")
        self.name_input = QLineEdit(self.book_name)  # Prefill with current name
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)

        price_label = QLabel("Ny Pris (New Price):")
        self.price_input = QLineEdit()
        layout.addWidget(price_label)
        layout.addWidget(self.price_input)

        save_button = QPushButton("Lagre Endringer (Save Changes)")
        save_button.clicked.connect(self.save_changes)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_changes(self):
        new_book_name = self.name_input.text()
        new_book_price = self.price_input.text()

        if not new_book_name or not new_book_price:
            QMessageBox.warning(self, "Feil", "Begge feltene må fylles ut.")
            return

        try:
            ssh, remote_file_path = self.parent().connect_to_server()
            sftp = ssh.open_sftp()

            try:
                with sftp.open(remote_file_path, 'r') as file:
                    books = json.load(file)
            except FileNotFoundError:
                QMessageBox.critical(self, "Feil", "JSON-filen finnes ikke på serveren.")
                return
            except json.JSONDecodeError:
                QMessageBox.critical(self, "Feil", "Kunne ikke lese JSON-filen fra serveren.")
                return

            for book in books:
                if book['name'] == self.book_name:
                    book['name'] = new_book_name
                    book['price'] = new_book_price
                    break
            else:
                QMessageBox.warning(self, "Feil", "Bok ikke funnet.")
                return

            with sftp.open(remote_file_path, 'w') as file:
                json.dump(books, file, indent=4)

            QMessageBox.information(self, "Suksess", "Endringene ble lagret!")
            self.parent().load_books()  # Refresh the book list in the parent window

        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke koble til serveren: {str(e)}")

        finally:
            sftp.close()
            ssh.close()

        self.close()


# Settings Dialog Class
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Innstillinger (Settings)")
        self.setMinimumSize(300, 400)
        self.setStyleSheet("background-color: #E0F7FA;")

        layout = QVBoxLayout()

        info_label = QLabel("Ingen innstillinger tilgjengelig for øyeblikket.")
        layout.addWidget(info_label)

        close_button = QPushButton("Lukk (Close)")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookUploader()
    window.show()
    sys.exit(app.exec_())
