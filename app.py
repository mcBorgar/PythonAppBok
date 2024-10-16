import paramiko
import json

# Server details
server_ip = '192.168.1.218'
username = 'bok'
password = 'bok'  

# Path to the JSON file on the server
remote_file_path = '/home/bok/books.json'  # Replace with the actual path on your server

# Connect to the server via SSH
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(server_ip, username=username, password=password)

# Open an SFTP session to transfer files
sftp = ssh.open_sftp()

# Read the JSON file from the server
with sftp.open(remote_file_path, 'r') as file:
    books = json.load(file)

# Close the SFTP and SSH connection
sftp.close()
ssh.close()

# Print the books
print("Books:", books)
