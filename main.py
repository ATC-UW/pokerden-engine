
import argparse
from server import PokerEngineServer

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Poker Engine Server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host address')
    parser.add_argument('--port', type=int, default=5000, help='Port number')
    parser.add_argument('--players', type=int, default=2, help='Number of players')
    parser.add_argument('--timeout', type=int, default=30, help='Turn timeout in seconds')
    parser.add_argument('--debug', default=False, action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    server = PokerEngineServer(args.host, args.port, args.players, args.timeout, args.debug)
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.stop_server()
