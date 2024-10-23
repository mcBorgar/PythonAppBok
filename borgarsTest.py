import sys
import json
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QMessageBox,
    QDialog,
)

class BookUploader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Book Uploader")
        self.setGeometry(100, 100, 300, 200)
        self.books = []  # List to store books
        self.init_ui()

    def init_ui(self):
        # Create main layout and central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create input fields for book name and price
        self.book_name_input = QLineEdit(self)
        self.book_name_input.setPlaceholderText("Book Name")
        self.book_price_input = QLineEdit(self)
        self.book_price_input.setPlaceholderText("Book Price")

        # Create buttons for uploading, removing, and settings
        upload_button = self.create_button("Upload Book", self.upload_book)
        remove_button = self.create_button("Remove Book", self.remove_book)
        settings_button = self.create_button("Innstillinger", self.open_settings_dialog)

        # Add widgets to layout
        layout.addWidget(self.book_name_input)
        layout.addWidget(self.book_price_input)
        layout.addWidget(upload_button)
        layout.addWidget(remove_button)
        layout.addWidget(settings_button)

        self.show()

    def create_button(self, label, callback):
        """Create a button with the given label and callback function."""
        button = QPushButton(label, self)
        button.clicked.connect(callback)
        return button

    def upload_book(self):
        """Upload book information and save to JSON file."""
        book_name = self.book_name_input.text()
        book_price = self.book_price_input.text()

        if not book_name or not book_price:
            QMessageBox.warning(self, "Input Error", "Please enter both book name and price.")
            return

        try:
            book_price = float(book_price)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Price must be a valid number.")
            return

        self.books.append({"name": book_name, "price": book_price})
        self.save_books_to_file()
        QMessageBox.information(self, "Success", f"Book '{book_name}' uploaded successfully!")

        # Clear input fields
        self.book_name_input.clear()
        self.book_price_input.clear()

    def remove_book(self):
        """Remove a book by name."""
        book_name = self.book_name_input.text()
        if not book_name:
            QMessageBox.warning(self, "Input Error", "Please enter a book name to remove.")
            return

        for book in self.books:
            if book['name'] == book_name:
                self.books.remove(book)
                self.save_books_to_file()
                QMessageBox.information(self, "Success", f"Book '{book_name}' removed successfully!")
                self.book_name_input.clear()
                return

        QMessageBox.warning(self, "Not Found", f"Book '{book_name}' not found.")

    def save_books_to_file(self):
        """Save the list of books to a JSON file."""
        with open("books.json", "w") as file:
            json.dump(self.books, file)

    def open_settings_dialog(self):
        """Open the settings dialog."""
        settings_dialog = QDialog(self)
        settings_dialog.setWindowTitle("Innstillinger")

        # You can add your settings UI elements here.
        layout = QVBoxLayout(settings_dialog)
        label = QLabel("Settings will be here.")
        layout.addWidget(label)

        settings_dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookUploader()
    sys.exit(app.exec_())
