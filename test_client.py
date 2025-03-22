import socket
import json
import threading
import time
import sys
from typing import Optional, Dict, List, Any

class PokerGameClient:
    def __init__(self, host: str = 'localhost', port: int = 5000):
        """
        Initialize the poker game client.
        
        Args:
            host: Server host address
            port: Server port
        """
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player_id: Optional[int] = None
        self.game_state: Dict[str, Any] = {}
        self.hand: List[str] = []
        self.is_my_turn = False
        self.running = True
        self.buffer = ""  # Buffer to handle incomplete JSON messages

    def connect(self):
        """Connect to the poker game server."""
        try:
            print(f"Connecting to server at {self.host}:{self.port}...")
            self.client_socket.connect((self.host, self.port))
            
            # Start listening for messages from the server
            threading.Thread(target=self.listen_for_messages).start()
            
            return True
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False

    def listen_for_messages(self):
        """Listen for messages from the server."""
        while self.running:
            try:
                data = self.client_socket.recv(4096)
                print(data)
                if not data:
                    print("Disconnected from server")
                    self.running = False
                    break
                
                # Add received data to buffer
                self.buffer += data.decode('utf-8')
                
                # Process complete JSON objects in the buffer
                self.process_buffer()
                
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.running = False
                break

    def process_buffer(self):
        """Process complete JSON objects from the buffer."""
        while self.buffer:
            try:
                # Try to parse a complete JSON object
                message = json.loads(self.buffer)
                
                # If we got here, we have a complete JSON object
                self.process_message(message)
                
                # Clear the buffer after processing
                self.buffer = ""
                
            except json.JSONDecodeError as e:
                # If we have multiple JSON objects concatenated
                if "Extra data" in str(e):
                    try:
                        # Find position of the first complete JSON
                        valid_json = self.buffer[:e.pos]
                        message = json.loads(valid_json)
                        
                        # Process the complete message
                        self.process_message(message)
                        
                        # Keep the rest for later processing
                        self.buffer = self.buffer[e.pos:]
                    except Exception as inner_e:
                        print(f"Error processing partial JSON: {inner_e}")
                        self.buffer = ""
                else:
                    # We don't have a complete JSON object yet
                    break

    def process_message(self, message: Dict[str, Any]):
        """Process a message received from the server."""
        message_type = message.get('type')
        
        if message_type == 'player_id':
            self.player_id = message['id']
            print(f"You are Player {self.player_id}")
        
        elif message_type == 'player_count':
            print(f"Players connected: {message['count']}/{message['required']}")
        
        elif message_type == 'game_start':
            print(f"Game is starting!")
        
        elif message_type == 'game_state':
            self.game_state = message
            self.hand = message.get('your_hand', [])
            
            # Display game state
            print("\n==== Game State ====")
            print(f"Round: {message['round']}")
            print(f"Active Players: {message['active_players']}")
            print(f"Total Pot: {message['total_pot']}")
            print(f"Board: {message['board']}")
            print(f"Your Hand: {self.hand}")
            print(f"Raise Amount: {message['raise_amount']}")
            print(f"Player Bets: {message['player_bets']}")
            print(f"Waiting for: {message['current_waiting_for']}")
            print("====================\n")
        
        elif message_type == 'your_turn':
            self.is_my_turn = True
            timeout = message['timeout']
            print(f"\n=== YOUR TURN (timeout: {timeout}s) ===")
            
            # Display available actions
            print("Available actions:")
            print("  FOLD - Give up your hand")
            print("  CHECK - Pass the action (if no one has bet)")
            print("  CALL - Match the current bet")
            print("  RAISE <amount> - Increase the bet")
            print("  ALL_IN <amount> - Bet all your chips")
            
            # Start a timer thread to handle timeout
            threading.Thread(target=self.handle_turn_timeout, args=(timeout,)).start()
        
        elif message_type == 'player_action':
            print(f"Player {message['player']} {message['action']} {message.get('amount', '')}")
            if 'error' in message:
                print(f"Error: {message['error']}")
        
        elif message_type == 'timeout':
            print(f"Player {message['player']} timed out and defaulted to {message['default_action']}")
        
        elif message_type == 'round_complete':
            print(f"\nRound {message['round']} complete")
            print(f"Pot: {message['pot']}")
        
        elif message_type == 'game_end':
            print("\n==== GAME OVER ====")
            print(f"Winner: Player {message['winner']}")
            print(f"Final Board: {message['board']}")
            print("Player Hands:")
            for player, hand in message['hands'].items():
                print(f"  Player {player}: {hand}")
            print("Final Scores:")
            for player, score in message['scores'].items():
                print(f"  Player {player}: {score}")
            print("==================\n")
        
        elif message_type == 'player_disconnected':
            print(f"Player {message['player']} disconnected and {message['action']}")
        
        elif message_type == 'waiting_for_players':
            print("Waiting for players to join...")
            
        elif message_type == 'server_shutdown':
            print(f"Server message: {message.get('message', 'Server is shutting down')}")
            self.running = False
            print("Disconnecting due to server shutdown...")

    def handle_turn_timeout(self, timeout: int):
        """Handle the turn timeout."""
        start_time = time.time()
        
        while self.is_my_turn and time.time() - start_time < timeout:
            time.sleep(0.1)
        
        if self.is_my_turn:
            print("\nTimeout! Defaulting to FOLD")
            self.send_action('FOLD', 0)
            self.is_my_turn = False

    def send_action(self, action: str, amount: int = 0):
        """Send an action to the server."""
        try:
            message = {
                'action': action,
                'amount': amount
            }
            self.client_socket.send(json.dumps(message).encode('utf-8'))
            self.is_my_turn = False
        except Exception as e:
            print(f"Error sending action: {e}")

    def handle_user_input(self):
        """Handle user input for actions."""
        while self.running:
            if self.is_my_turn:
                try:
                    user_input = input("Enter your action: ").strip().upper()
                    
                    if user_input == 'FOLD':
                        self.send_action('FOLD')
                    elif user_input == 'CHECK':
                        self.send_action('CHECK')
                    elif user_input == 'CALL':
                        self.send_action('CALL')
                    elif user_input.startswith('RAISE '):
                        amount = int(user_input.split(' ')[1])
                        self.send_action('RAISE', amount)
                    elif user_input.startswith('ALL_IN '):
                        amount = int(user_input.split(' ')[1])
                        self.send_action('ALL_IN', amount)
                    else:
                        print("Invalid action. Try again.")
                except ValueError:
                    print("Invalid amount. Please enter a number.")
                except Exception as e:
                    print(f"Error processing input: {e}")
            else:
                # Not our turn, wait a bit before checking again
                time.sleep(0.5)

    def disconnect(self):
        """Disconnect from the server."""
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        print("Disconnected from server")

# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Poker Game Client')
    parser.add_argument('--host', type=str, default='localhost', help='Server host address')
    parser.add_argument('--port', type=int, default=5000, help='Server port number')
    
    args = parser.parse_args()
    
    client = PokerGameClient(host=args.host, port=args.port)
    
    if client.connect():
        # Start handling user input in a separate thread
        input_thread = threading.Thread(target=client.handle_user_input)
        input_thread.daemon = True
        input_thread.start()
        
        try:
            # Keep the main thread alive
            while client.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            client.disconnect()