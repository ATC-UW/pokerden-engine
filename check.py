import os
import argparse
from config import OUTPUT_GAME_RESULT_FILE, OUTPUT_FILE_SIMULATION

def check_status(filename):
    """Check status of a given file."""
    if os.path.exists(filename) and os.path.isfile(filename):
        with open(filename, 'r') as file:
            content = file.read()

        if not content:
            print("NOT STARTED")
            return

        if "RUNNING" in content:
            print("RUNNING")
        elif "DONE" in content:
            print("DONE")
    else:
        print("NOT STARTED")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Check status of game or simulation.')
    parser.add_argument('--sim', action='store_true', help='Check simulation file instead of game result file')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Choose which file to check based on command line argument
    status_file = OUTPUT_FILE_SIMULATION if args.sim else OUTPUT_GAME_RESULT_FILE
    
    # Check the status of the selected file
    check_status(status_file)

if __name__ == "__main__":
    main()