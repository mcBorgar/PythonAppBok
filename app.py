import paramiko
import json

# Server details
server_ip = 'server_ip'
username = 'your_username'
password = 'your_password'  # It's better to use SSH keys for security

# Connect to the server
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(server_ip, username=username, password=password)

# Read the JSON file
sftp = ssh.open_sftp()
remote_file_path = '/path/to/books.json'
with sftp.open(remote_file_path, 'r') as file:
    books = json.load(file)

# Close connections
sftp.close()
ssh.close()

# Display the books
print("Books:", books)
