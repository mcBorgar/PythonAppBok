import paramiko
import json

# Server details
server_ip = '192.168.1.218'
username = 'bok'
password = 'bok'  

# Path to the JSON file on the server
remote_file_path = '/home/bok/books.json'  # Make sure this path is correct

# Connect to the server via SSH
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(server_ip, username=username, password=password)

# Open an SFTP session to transfer files
sftp = ssh.open_sftp()

# Read the JSON file from the server
with sftp.open(remote_file_path, 'r') as file:
    books = json.load(file)

# Example: Add a new book
new_book = {
    "title": "New Book Title",
    "author": "New Author",
    "isbn": "1122334455"
}

# Add the new book to the existing list
books.append(new_book)

# Write the updated list back to the server
with sftp.open(remote_file_path, 'w') as file:
    json.dump(books, file, indent=4)

# Close the SFTP and SSH connection
sftp.close()
ssh.close()

# Print the updated list of books
print("Updated books:", books)
