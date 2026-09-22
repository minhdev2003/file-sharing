# Secure File Transfer Demo

A Python client/server application that demonstrates file upload, download, and listing over a local TCP connection. Built as a clean, portfolio-friendly networking project to showcase socket programming, multithreaded server handling, and practical file transfer workflows.

## Project Overview

This project implements a lightweight file-sharing system with a server that stores uploaded files locally and a client that interacts with it over a network socket. It is designed to be easy to run, easy to understand, and a strong example of core Python networking concepts.

## Why This Project

This project is useful for demonstrating:

- Python socket programming
- Client/server architecture
- Multithreaded request handling
- File I/O and data transfer over TCP
- Secure-by-default validation patterns for file names and paths

## Features

- Upload files from a client to a central server
- Download files from the server to a local machine
- List all currently available files on the server
- Local file storage in a dedicated `server_files` directory
- Basic validation for invalid or unsafe file names
- Threaded request handling so multiple clients can be processed concurrently

## Architecture

The project follows a simple layered design:

- `server.py` contains the TCP server and handles incoming requests
- `client.py` contains the client logic and interactive command-line menu
- `server_files/` is where uploaded files are stored locally

## How It Works

1. The server starts listening on a configured host and port.
2. The client connects to the server using a socket.
3. The client sends an operation type: `UPLOAD`, `DOWNLOAD`, or `LIST`.
4. The server processes the request and returns the appropriate response.
5. Files are transferred in chunks to avoid loading everything into memory at once.

## Tech Stack

- Python 3
- `socket` module for networking
- `threading` for multithreaded server requests
- `pathlib` for local file path management

## Getting Started

### Prerequisites

- Python 3.8+
- Local machine or same-network environment for testing client/server communication

### Run the server

```bash
python server.py
```

### Run the client

```bash
python client.py
```

## Example Workflow

1. Start the server.
2. Start the client.
3. Choose option `1` to upload a file.
4. Choose option `2` to download a file.
5. Choose option `3` to list the available files.


## License

This project is intended for educational and portfolio use.
