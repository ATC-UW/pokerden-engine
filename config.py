import os

# Environment detection
IS_DOCKER = os.path.exists('/.dockerenv')

# Base paths for different environments
DOCKER_BASE_PATH = "/app/output"
LOCAL_BASE_PATH = "output"

# Use appropriate base path based on environment
BASE_PATH = DOCKER_BASE_PATH if IS_DOCKER else LOCAL_BASE_PATH

# Ensure local output directory exists
if not IS_DOCKER:
    os.makedirs(BASE_PATH, exist_ok=True)

NUM_ROUNDS = 6
SERVER_SIM_WAIT_BETWEEN_GAMES = 0.5 # seconds, time to wait between games in simulation mode
OUTPUT_GAME_RESULT_FILE = os.path.join(BASE_PATH, "game_result.log")
OUTPUT_FILE_SIMULATION = os.path.join(BASE_PATH, "sim_result.log")