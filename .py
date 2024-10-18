import paramiko
import json
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap
from PIL import Image
import os

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

        # Image Upload Button
        self.upload_image_button = QPushButton("Upload Image")
        self.upload_image_button.clicked.connect(self.upload_image)
        layout.addWidget(self.upload_image_button)

        # Image Label
        self.image_label = QLabel("No image uploaded")
        layout.addWidget(self.image_label)

        # Upload Button
        self.upload_button = QPushButton("OK")
        self.upload_button.clicked.connect(self.upload_book)
        layout.addWidget(self.upload_button)

        self.setLayout(layout)

        self.image_path = None  # To store the path of the uploaded image

    def connect_to_server(self):
        server_ip = '192.168.1.218'
        username = 'bok'
        password = 'bok'  
        remote_file_path = '/home/bok/books.json'

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_ip, username=username, password=password)

        return ssh, remote_file_path

    def upload_image(self):
        # Open a file dialog to select an image
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)", options=options)

        if file_path:
            self.image_path = file_path
            self.display_image(file_path)

    def display_image(self, file_path):
        pixmap = QPixmap(file_path)
        self.image_label.setPixmap(pixmap.scaled(200, 200, aspectRatioMode=True))  # Resize the image to fit in the label
        self.image_label.setText("")  # Clear the text label

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
            "price": book_price,
            "image": os.path.basename(self.image_path) if self.image_path else None  # Store image filename
        }
        books.append(new_book)

        # Write the updated list back to the server
        with sftp.open(remote_file_path, 'w') as file:
            json.dump(books, file, indent=4)

        # Upload the image to the server if an image was selected
        if self.image_path:
            image_remote_path = f'/home/bok/{os.path.basename(self.image_path)}'
            sftp.put(self.image_path, image_remote_path)  # Upload the image

        sftp.close()
        ssh.close()

        print("Updated books:", books)
        self.book_name_input.clear()
        self.book_price_input.clear()
        self.image_label.setText("No image uploaded")
        self.image_path = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    uploader = BookUploader()
    uploader.show()
    sys.exit(app.exec_())
