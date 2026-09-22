import socket
import threading
import os
from pathlib import Path


class FileServer:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        # Create a directory to store files if it doesn't exist
        self.storage_dir = Path("server_files").resolve()
        self.storage_dir.mkdir(exist_ok=True)

        print(f"Server started on {self.host}:{self.port}")

    def _recv_exact(self, client_socket, length):
        """Receive exactly the requested number of bytes."""
        chunks = []
        bytes_received = 0

        while bytes_received < length:
            chunk = client_socket.recv(length - bytes_received)
            if not chunk:
                raise ConnectionError("Connection closed by client")
            chunks.append(chunk)
            bytes_received += len(chunk)

        return b''.join(chunks)

    def _send_message(self, client_socket, message):
        """Send a string message with a 4-byte length prefix."""
        payload = str(message).encode('utf-8')
        header = len(payload).to_bytes(4, byteorder='big', signed=False)
        client_socket.sendall(header + payload)

    def _recv_message(self, client_socket):
        """Receive a length-prefixed string message."""
        header = self._recv_exact(client_socket, 4)
        message_length = int.from_bytes(header, byteorder='big', signed=False)
        if message_length == 0:
            return ""
        return self._recv_exact(client_socket, message_length).decode('utf-8')

    def _is_valid_filename(self, filename):
        """Reject unsafe or invalid filenames."""
        if not filename or filename in {'.', '..'}:
            return False

        if os.path.isabs(filename):
            return False

        if '/' in filename or '\\' in filename:
            return False

        safe_name = Path(filename).name
        return safe_name == filename and safe_name not in {'.', '..'}

    def start(self):
        """Start the server and listen for connections"""
        while True:
            client_socket, address = self.server_socket.accept()
            print(f"Connection from {address}")
            client_thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket,),
            )
            client_thread.daemon = True
            client_thread.start()

    def handle_client(self, client_socket):
        """Handle individual client connections"""
        try:
            while True:
                # Receive operation type from client
                operation = self._recv_message(client_socket)

                if not operation:
                    break

                if operation == "UPLOAD":
                    self.handle_upload(client_socket)
                elif operation == "DOWNLOAD":
                    self.handle_download(client_socket)
                elif operation == "LIST":
                    self.handle_list_files(client_socket)
                else:
                    self._send_message(client_socket, "ERROR")

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def handle_upload(self, client_socket):
        """Handle file upload from client"""
        try:
            filename = self._recv_message(client_socket)
            if not self._is_valid_filename(filename):
                self._send_message(client_socket, "ERROR")
                return

            file_path = self.storage_dir / filename

            file_size_raw = self._recv_message(client_socket)
            if not file_size_raw.isdigit():
                self._send_message(client_socket, "ERROR")
                return

            file_size = int(file_size_raw)

            # Send acknowledgment
            self._send_message(client_socket, "READY")

            # Receive and write file
            with open(file_path, 'wb') as f:
                bytes_received = 0
                while bytes_received < file_size:
                    remaining = file_size - bytes_received
                    chunk_size = min(1024, remaining)
                    data = client_socket.recv(chunk_size)
                    if not data:
                        raise ConnectionError("Client disconnected during upload")
                    f.write(data)
                    bytes_received += len(data)

            print(f"File {filename} received successfully")
            self._send_message(client_socket, "SUCCESS")

        except Exception as e:
            print(f"Error in upload: {e}")
            try:
                self._send_message(client_socket, "ERROR")
            except Exception:
                pass

    def handle_download(self, client_socket):
        """Handle file download request from client"""
        try:
            filename = self._recv_message(client_socket)
            if not self._is_valid_filename(filename):
                self._send_message(client_socket, "NOT_FOUND")
                return

            file_path = self.storage_dir / filename

            if not file_path.exists() or not file_path.is_file():
                self._send_message(client_socket, "NOT_FOUND")
                return

            # Send file size
            file_size = file_path.stat().st_size
            self._send_message(client_socket, str(file_size))

            # Wait for client ready signal
            ready = self._recv_message(client_socket)
            if ready != "READY":
                return

            # Send file
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    client_socket.sendall(data)

            print(f"File {filename} sent successfully")

        except Exception as e:
            print(f"Error in download: {e}")

    def handle_list_files(self, client_socket):
        """Send list of available files to client"""
        try:
            files = [f.name for f in self.storage_dir.iterdir() if f.is_file()]
            file_list = ','.join(files)
            self._send_message(client_socket, file_list)
        except Exception as e:
            print(f"Error listing files: {e}")
            self._send_message(client_socket, "ERROR")


if __name__ == "__main__":
    server = FileServer()
    server.start()
