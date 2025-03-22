import socket
import threading

def receive_messages(client_socket):
    """ Continuously receive messages from the server. """
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Server: {message}")
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def main():
    host = 'localhost'  # Change if needed
    port = 5000  # Change if needed
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        print(f"Connected to server at {host}:{port}")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # Start a thread to listen for messages from the server
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()
    
    try:
        while True:
            message = input("Enter message: ")
            if message.lower() == 'exit':
                break
            client_socket.send(message.encode('utf-8'))
    except KeyboardInterrupt:
        print("Disconnecting...")
    finally:
        client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()
