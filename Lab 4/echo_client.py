import socket

HOST = "127.0.0.1"
PORT = 50007

message = input("Enter a message: ")

with socket.create_connection((HOST, PORT)) as client:
    client.sendall(message.encode("utf-8"))
    client.shutdown(socket.SHUT_WR)  # Stop sending, but keep receiving

    response = bytearray()
    while True:
        data = client.recv(1024)
        if not data:
            break
        response.extend(data)

print("Server response:", response.decode("utf-8"))