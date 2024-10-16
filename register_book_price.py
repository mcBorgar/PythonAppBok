import paramiko
import json

server_ip = '192.168.1.218'
username = 'bok'
password = 'bok'
remote_file_path = '/home/bok/books.json'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(server_ip, username=username, password=password)

sftp = ssh.open_sftp()

with sftp.open(remote_file_path, 'r') as file:
    books = json.load(file)

print("Books:", books)

def register_price(books):
    book_title = input("Enter the title of the book: ")
    for book in books:
        if book['title'] == book_title:
            print("Error: Book already exists!")
            return
    new_book = {'title': book_title, 'author': input("Enter the author of the book: ")}
    price = float(input("Enter the price of the book: "))
    new_book['price'] = price
    books.append(new_book)
    print(f"Price registered for {book_title}: {price}")
    return

register_price(books)

with sftp.open(remote_file_path, 'w') as file:
    json.dump(books, file, indent=4)

sftp.close()
ssh.close()