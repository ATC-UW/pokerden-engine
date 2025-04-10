import os
from config import OUTPUT_DIR_CONTAINER

def main():
    if os.path.exists(OUTPUT_DIR_CONTAINER) and os.path.isfile(OUTPUT_DIR_CONTAINER):
        with open(OUTPUT_DIR_CONTAINER, 'w') as file:
            file.truncate(0)

if __name__ == "__main__":
    main()
