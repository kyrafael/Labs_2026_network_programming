import socket

HOST = "127.0.0.1"
PORT = 50007

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server listening on {HOST}:{PORT}")

    while True:  # Wait for the next client
        connection, address = server.accept()
        print(f"Client connected: {address}")

        with connection:
            while True:  # Read data from the current client
                data = connection.recv(1024)
                if not data:
                    break
                connection.sendall(data)

        print("Client disconnected. Waiting for the next client.")