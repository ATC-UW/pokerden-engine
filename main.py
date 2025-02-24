from config import NUM_ROUNDS, HOST, PORT
import socket


print(f"NUM_ROUNDS: {NUM_ROUNDS}")
print(f"HOST: {HOST}")
print(f"PORT: {PORT}")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server started at {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        client_socket.sendall(b"Welcome to the PokerDen server!")
        client_socket.close()

if __name__ == "__main__":
    start_server()