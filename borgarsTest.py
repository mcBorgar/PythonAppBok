import paramiko
import json
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton

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

        self.setLayout(layout)

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
