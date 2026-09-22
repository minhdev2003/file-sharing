import socket
import threading
import os
from pathlib import Path

class FileServer:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        # Create a directory to store files if it doesn't exist
        self.storage_dir = Path("server_files")
        self.storage_dir.mkdir(exist_ok=True)
        
        print(f"Server started on {self.host}:{self.port}")

    def start(self):
        """Start the server and listen for connections"""
        while True:
            client_socket, address = self.server_socket.accept()
            print(f"Connection from {address}")
            client_thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket,)
            )
            client_thread.start()

    def handle_client(self, client_socket):
        """Handle individual client connections"""
        try:
            while True:
                # Receive operation type from client
                operation = client_socket.recv(1024).decode()
                
                if not operation:
                    break
                
                if operation == "UPLOAD":
                    self.handle_upload(client_socket)
                elif operation == "DOWNLOAD":
                    self.handle_download(client_socket)
                elif operation == "LIST":
                    self.handle_list_files(client_socket)
                
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def handle_upload(self, client_socket):
        """Handle file upload from client"""
        try:
            # Receive filename
            filename = client_socket.recv(1024).decode()
            file_path = self.storage_dir / filename
            
            # Receive file size
            file_size = int(client_socket.recv(1024).decode())
            
            # Send acknowledgment
            client_socket.send("READY".encode())
            
            # Receive and write file
            with open(file_path, 'wb') as f:
                bytes_received = 0
                while bytes_received < file_size:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    f.write(data)
                    bytes_received += len(data)
            
            print(f"File {filename} received successfully")
            client_socket.send("SUCCESS".encode())
            
        except Exception as e:
            print(f"Error in upload: {e}")
            client_socket.send("ERROR".encode())

    def handle_download(self, client_socket):
        """Handle file download request from client"""
        try:
            # Receive filename
            filename = client_socket.recv(1024).decode()
            file_path = self.storage_dir / filename
            
            if not file_path.exists():
                client_socket.send("NOT_FOUND".encode())
                return
                
            # Send file size
            file_size = os.path.getsize(file_path)
            client_socket.send(str(file_size).encode())
            
            # Wait for client ready signal
            if client_socket.recv(1024).decode() != "READY":
                return
            
            # Send file
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    client_socket.send(data)
                    
            print(f"File {filename} sent successfully")
            
        except Exception as e:
            print(f"Error in download: {e}")

    def handle_list_files(self, client_socket):
        """Send list of available files to client"""
        try:
            files = [f.name for f in self.storage_dir.iterdir() if f.is_file()]
            file_list = ','.join(files)
            client_socket.send(file_list.encode())
        except Exception as e:
            print(f"Error listing files: {e}")
            client_socket.send("ERROR".encode())

if __name__ == "__main__":
    server = FileServer()
    server.start()

