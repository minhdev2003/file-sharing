# Secure File Transfer Demo

A Python client/server application that demonstrates file upload, download, and listing over a local TCP connection. This project showcases core networking concepts, file handling, and multithreaded server design in a simple, practical implementation.

## Overview

This project implements a lightweight file-sharing system where a server stores uploaded files locally and a client interacts with it through a socket connection. It is designed to be easy to run, easy to understand, and useful as a portfolio example for Python networking and backend application development.

## Features

- Upload files from a client to a server
- Download files from the server to a client
- List files currently available on the server
- Store uploaded files in a dedicated local folder
- Basic validation for invalid or unsafe filenames
- Threaded request handling for concurrent client connections

## Tech Stack

- Python 3
- Socket programming
- Threading
- File I/O
- Path validation

## Project Structure

- `server.py` — starts the TCP server and handles client requests
- `client.py` — connects to the server and provides a command-line interface
- `server_files/` — directory used to store uploaded files

## How It Works

1. The server starts listening on a host and port.
2. The client connects to the server.
3. The client sends one of these commands:
   - `UPLOAD`
   - `DOWNLOAD`
   - `LIST`
4. The server processes the request and responds with the appropriate output.
5. Files are transferred in chunks to avoid loading entire files into memory.

## Getting Started

### Prerequisites

- Python 3.8+
- A local environment to run both the server and client

### Run the server

```bash
python server.py
