import paramiko
import json
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QDialog, QHBoxLayout, QFrame, QSplitter, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMovie

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
        left_container.setStyleSheet("background-color: #73A96F; padding: 20px;")  # Light brown background

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
        self.setFixedSize(400, 300)  # Adjust size to make it more usable
        self.setStyleSheet("background-color: #D2B48C;")  # Light brown background color
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)  # Normal dialog window

        main_layout = QVBoxLayout()

        # Loading spinner
        self.loading_label = QLabel(self)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_movie = QMovie("path_to_your_spinner.gif")  # Set the path to your loading GIF
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.setVisible(False)  # Initially hide it
        main_layout.addWidget(self.loading_label)

        self.book_name_label = QLabel("Book Name:")
        self.book_name_input = QLineEdit()
        main_layout.addWidget(self.book_name_label)
        main_layout.addWidget(self.book_name_input)

        self.book_name_label = QLabel("Genre:")
        self.book_name_input = QLineEdit()
        main_layout.addWidget(self.book_name_label)
        main_layout.addWidget(self.book_name_input)

        self.book_name_label = QLabel("Author:")
        self.book_name_input = QLineEdit()
        main_layout.addWidget(self.book_name_label)
        main_layout.addWidget(self.book_name_input)

        self.book_price_label = QLabel("Summary:")
        self.book_price_input = QLineEdit()
        main_layout.addWidget(self.book_price_label)
        main_layout.addWidget(self.book_price_input)

        self.book_price_label = QLabel("Pages:")
        self.book_price_input = QLineEdit()
        main_layout.addWidget(self.book_price_label)
        main_layout.addWidget(self.book_price_input)

        self.book_name_label = QLabel("Stock:")
        self.book_name_input = QLineEdit()
        main_layout.addWidget(self.book_name_label)
        main_layout.addWidget(self.book_name_input)

        self.book_price_label = QLabel("Price:")
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

        # Show loading spinner
        self.loading_label.setVisible(True)
        self.loading_movie.start()  # Start the loading animation

        # Attempt to connect to the server
        try:
            ssh, remote_file_path = self.connect_to_server()
            sftp = ssh.open_sftp()
        except Exception as e:
            QMessageBox.critical(self, "Serverfeil", f"Kunne ikke koble til serveren: {str(e)}")
            self.loading_label.setVisible(False)  # Hide loading spinner after handling error
            self.loading_movie.stop()  # Stop the loading animation
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
            # Check if books is a dictionary
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
            except Exception as e:
                QMessageBox.critical(self, "Feil", f"Kunne ikke skrive til JSON-filen: {str(e)}")
                sftp.close()
                ssh.close()
                self.loading_label.setVisible(False)  # Hide loading spinner
                self.loading_movie.stop()  # Stop the loading animation
                return

            print("Oppdaterte bøker:", books)
            self.book_name_input.clear()
            self.book_price_input.clear()

        finally:
            sftp.close()
            ssh.close()

        self.loading_label.setVisible(False)  # Hide loading spinner
        self.loading_movie.stop()  # Stop the loading animation

        # Show success message
        success_message = QMessageBox(self)
        success_message.setWindowTitle("Suksess")
        success_message.setText("Boken har blitt lagt til.")
        success_message.setIcon(QMessageBox.Information)

        # Move the success message to the side and make it stay for 2 seconds
        success_message.setGeometry(self.x() + 50, self.y() + 50, 300, 100)  # Position the message box slightly to the side

        success_message.show()
        QTimer.singleShot(2000, success_message.close)  # Close after 2 seconds


# Remove Book Dialog Class
class RemoveBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Fjern Bok (Remove Book)")
        self.setFixedSize(400, 300)  # Adjust size for usability
        self.setStyleSheet("background-color: #D2B48C;")  # Light brown background color

        main_layout = QVBoxLayout()

        self.book_name_label = QLabel("Book Name to Remove:")
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
        """Remove a book from the server."""
        book_name_to_remove = self.book_name_input.text()

        if not book_name_to_remove:
            QMessageBox.warning(self, "Feil", "Vennligst skriv inn navnet på boken som skal fjernes.")
            return

        try:
            ssh, remote_file_path = self.connect_to_server()
            sftp = ssh.open_sftp()
            with sftp.open(remote_file_path, 'r') as file:
                books = json.load(file)

            # Check if books is a dictionary
            if isinstance(books, dict):
                books = []  # Initialize books as an empty list if it's a dict

            # Filter out the book to be removed
            updated_books = [book for book in books if book['name'] != book_name_to_remove]

            if len(updated_books) == len(books):
                QMessageBox.warning(self, "Feil", "Boken ble ikke funnet.")
                return

            # Write the updated list back to the server
            with sftp.open(remote_file_path, 'w') as file:
                json.dump(updated_books, file, indent=4)

            QMessageBox.information(self, "Suksess", "Boken har blitt fjernet.")
            self.book_name_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke håndtere forespørselen: {str(e)}")
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
        self.setFixedSize(400, 300)  # Adjust size for usability
        self.setStyleSheet("background-color: #D2B48C;")  # Light brown background color

        main_layout = QVBoxLayout()

        # Add some setting options
        setting_label = QLabel("Innstillinger kommer snart...")
        main_layout.addWidget(setting_label)

        self.setLayout(main_layout)


# Main application loop
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = BookUploader()
    main_window.show()
    sys.exit(app.exec_())
