import os
from config import OUTPUT_DIR_CONTAINER

def main():
    if os.path.exists(OUTPUT_DIR_CONTAINER) and os.path.isfile(OUTPUT_DIR_CONTAINER):
        with open(OUTPUT_DIR_CONTAINER, 'r') as file:
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