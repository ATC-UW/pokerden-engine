import json
import socket
import threading
from player import SimplePlayer
from poker_type.utils import get_message_type_name

def prompt_for_input():
    """ Prompt the user for input. """
    return input("Enter message: ")

class Runner:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bot = None  # Placeholder for bot instance


    def set_bot(self, bot):
        """ Set the bot instance. """
        self.bot = bot


    def handle_messages(self, message):
        """ Handle messages from the server. """
        lines = message.split('\n')
        for line in lines:
            if line == '':  # Skip empty lines
                continue
            try:
                json_message = json.loads(line)
            except json.JSONDecodeError:
                print(f"Error decoding message: {line}")
                continue
            message_type = json_message.get('type')
            message = json_message.get('message')
            if message_type is None:
                print("Invalid message type")
            
            message_type_name = get_message_type_name(message_type)
            print(f"Message type: {message_type_name}")
            if message_type == 9: 
                # GameStateMessage
                self.bot.on_start()
            print(f"Server: {message}")

    def receive_messages(self):
        """ Continuously receive messages from the server. """
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                self.handle_messages(message)


            except Exception as e:
                print(f"Error receiving message: {e}")
                break


    def run(self):
        self.client_socket.connect((self.host, self.port))
        print(f"Connected to server at {self.host}:{self.port}")
        threading.Thread(target=self.receive_messages, daemon=True).start()

        try:
            while True:
                message = prompt_for_input()
                if message.lower() == 'exit':
                    break
                self.client_socket.send(message.encode('utf-8'))
        except KeyboardInterrupt:
            print("Disconnecting...")
        finally:
            self.client_socket.close()
            print("Connection closed.")


def main():
    host = 'localhost'  # Change if needed
    port = 5000  # Change if needed
    
    runner = Runner(host, port)
    simple_bot = SimplePlayer()
    runner.set_bot(simple_bot)
    runner.run()



if __name__ == "__main__":
    main()
