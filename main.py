import argparse
from server import PokerEngineServer
from config import NUM_ROUNDS, OUTPUT_FILE_SIMULATION, OUTPUT_GAME_RESULT_FILE

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Poker Engine Server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host address')
    parser.add_argument('--port', type=int, default=5000, help='Port number')
    parser.add_argument('--players', type=int, default=2, help='Number of players')
    parser.add_argument('--timeout', type=int, default=30, help='Turn timeout in seconds')
    parser.add_argument('--debug', default=False, action='store_true', help='Enable debug mode')
    parser.add_argument('--sim', default=False, action='store_true', help='Enable simulation mode')
    parser.add_argument('--sim-rounds', type=int, default=NUM_ROUNDS, help='Number of rounds to simulate')
    parser.add_argument('--blind', type=int, default=10, help='Blind amount for the game')
    args = parser.parse_args()

    # simulation mode
    if args.sim:
        try:
            # Write RUNNING when starting simulation
            with open(OUTPUT_FILE_SIMULATION, 'w') as sim_file:
                sim_file.write("RUNNING\n")

            print(f"Starting continuous simulation mode for {args.sim_rounds} games")
            # Create one server that runs multiple games
            server = PokerEngineServer(args.host, args.port, args.players, args.timeout, args.debug, args.sim, args.blind)
            server.simulation_rounds = args.sim_rounds  # Add this attribute to track rounds
            server.start_server()

        except KeyboardInterrupt:
            print("Shutting down simulation...")
            if 'server' in locals():
                server.stop_server()
     
    # normal mode - run 1 game and write to game_result file
    else:
        try:
            # Write RUNNING when starting single game
            with open(OUTPUT_GAME_RESULT_FILE, 'w') as game_file:
                game_file.write("RUNNING\n")

            print("Starting single game mode")
            # Create server that runs 1 game (sim=False to use game_result output)
            server = PokerEngineServer(args.host, args.port, args.players, args.timeout, args.debug, False, args.blind)
            server.simulation_rounds = 1  # Set to run only 1 game
            server.start_server()

        except KeyboardInterrupt:
            print("Shutting down server...")
            if 'server' in locals():
                server.stop_server()
