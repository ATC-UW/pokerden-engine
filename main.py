import socket
import threading
from typing import Dict, Tuple
import uuid
from game import Game
import argparse

from message import GAME_STATE

class PokerEngineServer:
    def __init__(self, host='localhost', port=5000, num_players=2, turn_timeout=30, debug=False):
        self.host = host
        self.port = port
        self.required_players = num_players
        self.turn_timeout = turn_timeout
        self.debug = debug
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.game = Game()
        self.player_connections: Dict[int, socket.socket] = {}
        self.player_addresses: Dict[int, Tuple[str, int]] = {}
        self.game_in_progress = False
        self.server_lock = threading.Lock()
        self.game_lock = threading.Lock()
        self.running = True

    def start_server(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.required_players)
            print(f"Server started on {self.host}:{self.port}")
            print(f"Waiting for {self.required_players} players to join...")
            self.accept_connections()
        except Exception as e:
            print(f"Error starting server: {e}")
            self.stop_server()

    def stop_server(self):
        self.running = False
        self.server_socket.close()
        for conn in self.player_connections.values():
            conn.close()
        print("Server stopped.")

    def accept_connections(self):
        while self.running and len(self.player_connections) < self.required_players:
            try:
                client_socket, address = self.server_socket.accept()
                player_id = self.generate_player_id()
                self.player_connections[player_id] = client_socket
                self.player_addresses[player_id] = address
                print(f"Player {player_id} connected from {address}")

                with self.game_lock:
                    self.game.add_player(player_id)
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
                break

        if len(self.player_connections) == self.required_players:
            self.run_game()

    def run_game(self):
        with self.game_lock:
            self.game_in_progress = True
        
        self.broadcast("Game starting!")

        self.broadcast("Game state!" + GAME_STATE(self.game.round_num, self.game.community_cards, self.game.players, self.game.pot, self.game.current_player, self.game.current_bet, self.game.min_raise, self.game.max_raise))

        for(player_id, conn) in self.player_connections.items():
            conn.sendall(f"Welcome, Player {player_id}!".encode('utf-8'))

        try:
            while self.running and self.game_in_progress:
                for player_id, conn in list(self.player_connections.items()):
                    conn.sendall(b"Your turn. Enter action: ")
                    action = conn.recv(1024).decode('utf-8')
                    if not action:
                        self.remove_player(player_id)
                    else:
                        self.process_action(player_id, action)
        except Exception as e:
            print(f"Error running game: {e}")
        finally:
            self.game_in_progress = False
            self.stop_server()

    def broadcast(self, message):
        for player_id, conn in self.player_connections.items():
            try:
                conn.sendall(message.encode('utf-8'))
            except:
                self.remove_player(player_id)

    def process_action(self, player_id, action):
        print(f"Player {player_id} action: {action}")
        self.broadcast(f"Player {player_id} did: {action}")

    def remove_player(self, player_id):
        if player_id in self.player_connections:
            self.player_connections[player_id].close()
            del self.player_connections[player_id]
            del self.player_addresses[player_id]
            print(f"Player {player_id} disconnected.")

    def generate_player_id(self):
        return uuid.uuid4().int & (1<<32)-1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Poker Engine Server')
    parser.add_argument('--host', type=str, default='localhost', help='Host address')
    parser.add_argument('--port', type=int, default=5000, help='Port number')
    parser.add_argument('--players', type=int, default=2, help='Number of players')
    parser.add_argument('--timeout', type=int, default=30, help='Turn timeout in seconds')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    server = PokerEngineServer(args.host, args.port, args.players, args.timeout, args.debug)
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.stop_server()
