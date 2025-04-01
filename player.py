from abc import ABC, abstractmethod

from poker_type.client import RoundStateClient
from poker_type.game import PokerAction

class Player(ABC):
    def __init__(self):
        """ Initializes the player. """
        pass

    @abstractmethod
    def on_start(self):
        """ Called when the game starts. """
        pass

    @abstractmethod
    def on_round_start(self, game_state, round_state: RoundStateClient):
        """ Called at the start of each round. """
        pass

    @abstractmethod
    def get_action(self, game_state, round_state: RoundStateClient):
        """ Called when it is the player's turn to act. """
        pass

    @abstractmethod
    def on_end_round(self, game_state, round_state: RoundStateClient):
        """ Called at the end of each round. """
        pass

    @abstractmethod
    def on_end_game(self, game_state, round_state: RoundStateClient, result):
        """ Called at the end of the game. """
        pass

class SimplePlayer(Player):
    def __init__(self):
        super().__init__()

    def on_start(self):
        print("Player called on game start")

    def on_round_start(self, game_state, round_state: RoundStateClient):
        print("Player called on round start")

    def get_action(self, game_state, round_state: RoundStateClient):
        print("Player called get action")

        if round_state.current_bet == 0:
            return PokerAction.CHECK, 0

        return PokerAction.CALL, 0

    def on_end_round(self, game_state, round_state: RoundStateClient):
        print("Player called on end round")

    def on_end_game(self, game_state, round_state: RoundStateClient, result):
        print("Player called on end game")