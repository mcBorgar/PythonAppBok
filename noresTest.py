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
from PyQt5.QtCore import Qt, QTimer, pyqtSlot 
from PyQt5.QtGui import QColor

#Background color var:


light = None


button_text = ("color: #2F4F4F;")
button_bc =("background-color: #D8CFC4;")
red_ins_bc_L = ("background-color: #D2B48C;")
left_side_bc_L =("background-color: #F0EAD6;")


    #@pyqtSlot

#####



# Main Window Class (Home Page)
class BookUploader(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.timer = QTimer(self)  # Create a QTimer instance
        self.timer.timeout.connect(self.load_books)  # Connect to the load_books method
        self.timer.start(5000)  # Check for updates every 5 seconds
        

    def init_ui(self, execute = False):
        con = True
        left_container = QFrame()
        if execute == False:
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
            left_container.setLayout(button_container)
            button_container.addWidget(add_button)
            button_container.addWidget(settings_button)

            # Left container frame for alignment and styling
            

            # left_layout.addWidget(left_container)
            
       
       
        
        if execute == False:
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
        #Switch dark light
        if execute == True or con == True:
            #left_container = QFrame()
            #left_container.setLayout(button_container)
            left_layout.addWidget(left_container)
            print("kode kjører2323")
            left_container.setStyleSheet(f"{left_side_bc_L} padding: 20px;")  # Light brown background
            execute = False
            print("kode kjører")

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
        self.load_book_details()

    def init_ui(self):
        self.setWindowTitle("Rediger Bok (Edit Book)")
        self.setMinimumSize(300, 400)  # Set minimum size smaller
        self.setStyleSheet("background-color: #D2B48C;")  # Light brown background color
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
        self.setStyleSheet("background-color: #D2B48C;")  # Light brown background color

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Innstillinger vil komme snart."))  # Placeholder text
        self.setLayout(layout)


if __name__ == "__main__":
    light = True
    button_text = ("color: #2F4F4F;")
    button_bc =("background-color: #D8CFC4;")
    red_ins_bc_L = ("background-color: #D2B48C;")
    left_side_bc_L =("background-color: #F0EAD6;")
    app = QApplication(sys.argv)
    text = app.setStyleSheet("QLabel, QTextEdit {color: black; }")
    
    window = BookUploader()
    tekst = QTextEdit()
    #tekst_bc_L = tekst.setTextColor(QColor("white"))
    
    
    window.show()
    sys.exit(app.exec_())





