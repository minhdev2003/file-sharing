import socket
import os
from pathlib import Path

class FileClient:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.client_socket = None

    def connect(self):
        """Connect to the server"""
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

    def disconnect(self):
        """Disconnect from the server"""
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None

    def upload_file(self, filepath):
        """Upload a file to the server"""
        try:
            if not os.path.exists(filepath):
                print("File does not exist")
                return False

            # Send operation type
            self.client_socket.send("UPLOAD".encode())
            
            # Send filename
            filename = os.path.basename(filepath)
            self.client_socket.send(filename.encode())
            
            # Send file size
            file_size = os.path.getsize(filepath)
            self.client_socket.send(str(file_size).encode())
            
            # Wait for server ready signal
            if self.client_socket.recv(1024).decode() != "READY":
                return False
            
            # Send file
            with open(filepath, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    self.client_socket.send(data)
            
            # Wait for upload confirmation
            response = self.client_socket.recv(1024).decode()
            return response == "SUCCESS"
            
        except Exception as e:
            print(f"Error in upload: {e}")
            return False

    def download_file(self, filename, save_path):
        """Download a file from the server"""
        try:
            # Send operation type
            self.client_socket.send("DOWNLOAD".encode())
            
            # Send filename
            self.client_socket.send(filename.encode())
            
            # Receive file size or error
            response = self.client_socket.recv(1024).decode()
            if response == "NOT_FOUND":
                print("File not found on server")
                return False
                
            file_size = int(response)
            
            # Send ready signal
            self.client_socket.send("READY".encode())
            
            # Receive and write file
            with open(save_path, 'wb') as f:
                bytes_received = 0
                while bytes_received < file_size:
                    data = self.client_socket.recv(1024)
                    if not data:
                        break
                    f.write(data)
                    bytes_received += len(data)
            
            return True
            
        except Exception as e:
            print(f"Error in download: {e}")
            return False

    def list_files(self):
        """Get list of available files from server"""
        try:
            self.client_socket.send("LIST".encode())
            response = self.client_socket.recv(1024).decode()
            if response == "ERROR":
                return []
            return response.split(',') if response else []
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

def main():
    client = FileClient()
    client.connect()

    while True:
        print("\nFile Sharing Client")
        print("1. Upload file")
        print("2. Download file")
        print("3. List available files")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == "1":
            filepath = input("Enter the path of the file to upload: ")
            if client.upload_file(filepath):
                print("File uploaded successfully")
            else:
                print("Failed to upload file")
                
        elif choice == "2":
            filename = input("Enter the filename to download: ")
            save_path = input("Enter where to save the file: ")
            if client.download_file(filename, save_path):
                print("File downloaded successfully")
            else:
                print("Failed to download file")
                
        elif choice == "3":
            files = client.list_files()
            if files:
                print("\nAvailable files:")
                for file in files:
                    print(f"- {file}")
            else:
                print("No files available or error occurred")
                
        elif choice == "4":
            client.disconnect()
            break
            
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()