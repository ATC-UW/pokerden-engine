import socket
import threading
import time
from typing import Dict, Tuple
import uuid
import logging
from config import OUTPUT_GAME_RESULT_FILE, OUTPUT_FILE_SIMULATION, SERVER_SIM_WAIT_BETWEEN_GAMES
from game.game import Game
import os

from message import (
    CONNECT,
    END, 
    GAME_STATE,
    PLAYER_ACTION, 
    REQUEST_PLAYER_MESSAGE, 
    ROUND_END, 
    ROUND_START, 
    START, TEXT, 
    Message
)

from poker_type.game import PokerAction
from poker_type.utils import (
    get_poker_action_enum_from_index, 
    get_round_name, 
    get_round_name_from_enum
)

logger = logging.getLogger(__name__)

class PokerEngineServer:
    def __init__(self, host='localhost', port=5000, num_players=2, turn_timeout=30, debug=False, sim=False, blind_amount=10):
        self.host = host
        self.port = port
        self.required_players = num_players
        self.turn_timeout = turn_timeout
        self.debug = debug
        self.sim = sim
        self.blind_amount = blind_amount
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.game = Game(self.debug, self.blind_amount)
        self.player_connections: Dict[int, socket.socket] = {}
        self.player_addresses: Dict[int, Tuple[str, int]] = {}
        self.game_in_progress = False
        self.server_lock = threading.Lock()
        self.game_lock = threading.Lock()
        self.running = True
        self.current_player_idx = 0
        self.game_count = 0
        
        # Dealer button management for continuous games
        self.dealer_button_position = 0

    def start_server(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.required_players)
            print(f"Server started on {self.host}:{self.port}")
            print(f"Waiting for {self.required_players} players to join...")
            if not self.sim:
                self.remove_file_content(OUTPUT_GAME_RESULT_FILE)
                self.append_to_file(OUTPUT_GAME_RESULT_FILE, "RUNNING")
            self.accept_connections()
        except Exception as e:
            print(f"Error starting server: {e}")
            self.stop_server()

    def stop_server(self):
        self.running = False
        self.server_socket.close()
        for conn in self.player_connections.values():
            conn.close()
        
        # If this was a simulation, replace RUNNING with DONE
        if self.sim:
            self.replace_running_with_done()
        
        print("Server stopped.")

    def replace_running_with_done(self):
        """Replace RUNNING with DONE in the simulation output file"""
        try:
            if os.path.exists(OUTPUT_FILE_SIMULATION):
                with open(OUTPUT_FILE_SIMULATION, 'r') as file:
                    content = file.read()
                
                # Replace RUNNING with DONE
                content = content.replace("RUNNING", "DONE")
                
                with open(OUTPUT_FILE_SIMULATION, 'w') as file:
                    file.write(content)
                
                print("Simulation status updated to DONE")
        except Exception as e:
            print(f"Error updating simulation status: {e}")

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
            self.run_continuous_games()

    def reset_game_state(self):
        """Reset the game state for a new game while keeping the same players"""
        with self.game_lock:
            # Create a new game instance
            self.game = Game(self.debug, self.blind_amount)
            
            # Set the current dealer button position
            self.game.set_dealer_button_position(self.dealer_button_position)
            
            # Add all existing players to the new game
            for player_id in self.player_connections.keys():
                self.game.add_player(player_id)
            
            self.game_in_progress = False
            self.current_player_idx = 0

    def run_continuous_games(self):
        """Run multiple games with the same connections"""
        while self.running and len(self.player_connections) >= self.required_players:
            self.game_count += 1
            print(f"\n=== Starting Game #{self.game_count} ===")
            print(f"Dealer button position: {self.dealer_button_position}")
            
            # Check if we've reached the simulation rounds limit
            if hasattr(self, 'simulation_rounds') and self.game_count > self.simulation_rounds:
                print(f"Reached simulation limit of {self.simulation_rounds} games. Stopping.")
                break
            
            # Reset game state for new game
            self.reset_game_state()
            
            # Run a single game
            self.run_single_game()
            
            # Rotate dealer button after each game for continuous mode
            self.rotate_dealer_button()
            
            # Check if we should continue
            if len(self.player_connections) < self.required_players:
                print("Not enough players remaining, stopping server.")
                break
            
            # Wait a bit before starting the next game
            print(f"Waiting {SERVER_SIM_WAIT_BETWEEN_GAMES} seconds before starting next game...")
            time.sleep(SERVER_SIM_WAIT_BETWEEN_GAMES)
        
        print("Game session ended.")
        self.stop_server()

    def run_single_game(self):
        """Run a single game"""
        with self.game_lock:
            self.game_in_progress = True
        
        self.broadcast_text(f"Game #{self.game_count} starting!")

        self.game.start_game()
        # broadcast message with hands to each player
        for (player_id, conn) in self.player_connections.items():
            logger.debug(f"Player {player_id} hands: {self.game.get_player_hands(player_id)}")
            
            # Determine if this player is small blind or big blind
            is_small_blind = player_id == self.game.get_small_blind_player()
            is_big_blind = player_id == self.game.get_big_blind_player()
            
            start_message = START(
                "Game initiated!", 
                self.game.get_player_hands(player_id),
                self.blind_amount,
                is_small_blind,
                is_big_blind
            )
            logger.debug(f"Sending start message to player {player_id}: {str(start_message)}")  
            self.send_message(player_id, str(start_message))
        
        self.broadcast_game_state()

        round_start_message = ROUND_START(get_round_name_from_enum(self.game.get_current_round()))
        self.current_player_idx = 0
        self.broadcast_message(round_start_message)

        waiting_for = self.game.get_current_waiting_for()

        for(player_id, conn) in self.player_connections.items():
            connect_message = CONNECT(player_id)
            self.send_message(player_id, str(connect_message))
            self.send_text_message(player_id, f"Welcome to Game #{self.game_count}! Your ID is {player_id}")

        try:
            while self.running and self.game_in_progress:
                if self.game.is_current_round_complete() and self.game.is_game_over():
                    self.broadcast_text(f"Game #{self.game_count} over!")
                    score = self.game.get_final_score()
                    for player_id in score.keys():
                        end_message = END(score[player_id])
                        self.send_message(player_id, str(end_message))
                    # TODO: Add a reveal cards message
                    self.game_in_progress = False

                    if not self.sim:
                        self.append_to_file(OUTPUT_GAME_RESULT_FILE, f"GAME_{self.game_count} " + str(score))
                    else:
                        pass
                    break

                self.broadcast_text("New round starting!")
                self.broadcast_game_state()
                
                # round logic
                while not self.game.is_current_round_complete():
                    waiting_for = self.game.get_current_waiting_for()
                    length = len(waiting_for)
                    queue = list(waiting_for)
                    if length == 0:
                        break

                    print("Current player in game: ", waiting_for)
                    
                    # For the first round, prioritize blind players
                    if self.game.round_index == 0:
                        # Sort queue to have small blind first, then big blind
                        small_blind = self.game.get_small_blind_player()
                        big_blind = self.game.get_big_blind_player()
                        
                        if small_blind in waiting_for and big_blind in waiting_for:
                            # Arrange so small blind goes first, then big blind
                            queue = []
                            if small_blind in waiting_for:
                                queue.append(small_blind)
                            if big_blind in waiting_for:
                                queue.append(big_blind)
                            # Add other players
                            for player in waiting_for:
                                if player not in [small_blind, big_blind]:
                                    queue.append(player)
                    
                    start_player_idx = 0
                    length = len(queue)

                    idx = start_player_idx
                    while idx < start_player_idx + length:
                        print(f"Current player index: {idx}, Player ID: {queue[idx % length]}")
                        player_id = queue[idx % length]
                        
                        if player_id not in self.player_connections:
                            idx += 1
                            continue  # Skip removed players
                            
                        conn = self.player_connections[player_id]

                        request_action_message = REQUEST_PLAYER_MESSAGE(player_id, 0)
                        self.send_message(player_id, str(request_action_message))

                        try:
                            conn.settimeout(1)
                            action = conn.recv(4096).decode('utf-8')
                            if not action:
                                self.remove_player(player_id)
                                break

                            else:
                                action = action.strip()
                                if action == "":
                                    self.send_text_message(player_id, "Invalid action. Try again.")
                                    continue
                                
                                print(f"Player {player_id} action: {action}")
                                ok = self.process_action(player_id, action)
                                if not ok:
                                    self.send_text_message(player_id, "Invalid action. Try again.")
                                    continue
                        except socket.timeout:
                            self.send_text_message(player_id, "Timeout!")
                            action = PLAYER_ACTION(player_id, PokerAction.FOLD.value, 0)

                            ok = self.process_action(player_id, str(action))
                            if not ok:
                                self.send_text_message(player_id, "Invalid action. Try again.")
                                continue
                        except Exception as e:
                            print(f"Error receiving action from player {player_id}: {e}")
                            self.remove_player(player_id)
                            break

                        idx += 1

                # round end
                end_round = ROUND_END(get_round_name_from_enum(self.game.get_current_round()))
                self.game.end_round()
                self.broadcast_game_state()

                self.broadcast_message(end_round)

                # next round
                self.broadcast_game_state()
                self.broadcast_message(round_start_message)
                self.game.start_round()

        except Exception as e:
            print(f"Error running game: {e}")
        finally:
            self.game_in_progress = False

    def send_message(self, player_id, message):
        """
        Send a message to a player in raw text.
        """
        message = message + "\n"
        if player_id in self.player_connections:
            self.player_connections[player_id].sendall(message.encode('utf-8'))

    def send_text_message(self, player_id, message):
        mes = TEXT(message)
        self.send_message(player_id, mes.serialize())
        print(f"Sent message to player {player_id}: {message}")

    def broadcast(self, message):
        message = message + "\n"
        for player_id, conn in self.player_connections.items():
            try:
                conn.sendall(message.encode('utf-8'))
            except:
                self.remove_player(player_id)

    def broadcast_text(self, message):
        mes = TEXT(message)
        self.broadcast(str(mes))

    def broadcast_message(self, message: Message):
        self.broadcast(message.serialize())

    def broadcast_game_state(self):
        round_name = get_round_name(self.game.round_index)
        print(f"Broadcasting game state for round {round_name}")

        game_state = self.game.get_game_state()
        message = GAME_STATE(game_state)
        
        self.broadcast(str(message))

    def process_action(self, player_id, action):
        # Process the action received from the player, broadcast the game state if successful
        action = action.strip()
        action_message = PLAYER_ACTION.parse(action)
        action_type = action_message.message["action"]

        action_tuple = (get_poker_action_enum_from_index(action_type), action_message.message["amount"])
        print(f"Processing action from player {player_id}: {action_tuple}")
        try:
            self.game.update_game(player_id, action_tuple)
        except Exception as e:
            self.send_text_message(player_id, f"Invalid action: {e}")
            print(f"Error processing action from player {player_id}: {e}")
            return False

        self.broadcast_game_state()
        return True

    def remove_player(self, player_id):
        if player_id in self.player_connections:
            self.player_connections[player_id].close()
            del self.player_connections[player_id]
            del self.player_addresses[player_id]
            print(f"Player {player_id} disconnected.")

    def generate_player_id(self):
        return uuid.uuid4().int & (1<<32)-1
    
    def append_to_file(self, path, score):
        with open(path, "a") as file:
            file.write(f"{score}\n")
        
        file.close()

    def remove_file_content(self, path):
        with open(path, "w") as file:
            file.write("")
        
        file.close()

    def rotate_dealer_button(self):
        """Rotate the dealer button to the next player"""
        if len(self.player_connections) > 1:
            self.dealer_button_position = (self.dealer_button_position + 1) % len(self.player_connections)
            print(f"Dealer button rotated to position {self.dealer_button_position}")