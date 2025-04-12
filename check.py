import os
from config import OUTPUT_GAME_RESULT_FILE

def main():
    if os.path.exists(OUTPUT_GAME_RESULT_FILE) and os.path.isfile(OUTPUT_GAME_RESULT_FILE):
        with open(OUTPUT_GAME_RESULT_FILE, 'r') as file:
            content = file.read()

        if not content:
            print("NOT STARTED")

        if "RUNNING" in content:
            print("RUNNING")
        elif "DONE" in content:
            print("DONE")
    else:
        print("NOT STARTED")


if __name__ == "__main__":
    main()