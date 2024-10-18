import paramiko
import json
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt

class BookUploader(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Library App")

        # Layout
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

        # Make the widgets scale with window size
        self.book_name_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.book_price_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.upload_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setLayout(layout)

        # # Apply light brown theme using QSS (Qt Style Sheets)
        # self.setStyleSheet("""
        #     QWidget {
        #         background-color: #D2B48C;  /* Light brown background */
        #         font-family: Arial, sans-serif;
        #     }
        #     QLabel {
        #         color: #4B2E2E;  /* Darker brown text color */
        #         font-size: 16px;
        #     }
        #     QLineEdit {
        #         background-color: #F5DEB3;  /* Wheat color background for input fields */
        #         color: #4B2E2E;
        #         border: 2px solid #8B4513;  /* SaddleBrown border */
        #         border-radius: 5px;
        #         padding: 5px;
        #         font-size: 14px;
        #     }
        #     QPushButton {
        #         background-color: #8B4513;  /* SaddleBrown button */
        #         color: white;
        #         font-size: 16px;
        #         padding: 10px;
        #         border-radius: 10px;
        #     }
        #     QPushButton:hover {
        #         background-color: #A0522D;  /* Slightly lighter brown on hover */
        #     }
        #     QPushButton:pressed {
        #         background-color: #5C4033;  /* Darker brown when pressed */
        #     }
        # """)

    def connect_to_server(self):
        server_ip = '192.168.1.218'
        username = 'bok'
        password = 'bok'
        remote_file_path = '/home/bok/books.json'

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_ip, username=username, password=password)

        return ssh, remote_file_path

    def upload_book(self):
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    uploader = BookUploader()
    uploader.show()
    sys.exit(app.exec_())