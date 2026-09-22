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
        self.client_socket.settimeout(10)
        self.client_socket.connect((self.host, self.port))

    def disconnect(self):
        """Disconnect from the server"""
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None

    def _send_message(self, message):
        payload = str(message).encode('utf-8')
        length = len(payload).to_bytes(4, byteorder='big', signed=False)
        self.client_socket.sendall(length + payload)

    def _recv_message(self):
        header = self.client_socket.recv(4)
        if len(header) < 4:
            raise ConnectionError('Connection closed by server')

        msg_length = int.from_bytes(header, byteorder='big', signed=False)
        chunks = []
        remaining = msg_length
        while remaining > 0:
            chunk = self.client_socket.recv(remaining)
            if not chunk:
                raise ConnectionError('Server disconnected before message was fully received')
            chunks.append(chunk)
            remaining -= len(chunk)
        return b''.join(chunks).decode('utf-8')

    def upload_file(self, filepath):
        """Upload a file to the server"""
        try:
            if not os.path.exists(filepath):
                print("File does not exist")
                return False

            filename = os.path.basename(filepath)
            if not filename or filename in {'.', '..'}:
                print("Invalid filename")
                return False

            self._send_message("UPLOAD")
            self._send_message(filename)
            self._send_message(str(os.path.getsize(filepath)))

            if self._recv_message() != "READY":
                return False

            with open(filepath, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    self.client_socket.sendall(data)

            response = self._recv_message()
            return response == "SUCCESS"

        except Exception as e:
            print(f"Error in upload: {e}")
            return False

    def download_file(self, filename, save_path):
        """Download a file from the server"""
        try:
            self._send_message("DOWNLOAD")
            self._send_message(filename)

            response = self._recv_message()
            if response == "NOT_FOUND":
                print("File not found on server")
                return False

            file_size = int(response)
            self._send_message("READY")

            save_dir = os.path.dirname(save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)

            with open(save_path, 'wb') as f:
                bytes_received = 0
                while bytes_received < file_size:
                    data = self.client_socket.recv(min(1024, file_size - bytes_received))
                    if not data:
                        break
                    f.write(data)
                    bytes_received += len(data)

            return bytes_received == file_size

        except Exception as e:
            print(f"Error in download: {e}")
            return False

    def list_files(self):
        """Get list of available files from server"""
        try:
            self._send_message("LIST")
            response = self._recv_message()
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
