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
    def on_round_start(self, round_state: RoundStateClient):
        """ Called at the start of each round. """
        pass

    @abstractmethod
    def get_action(self, round_state: RoundStateClient):
        """ Called when it is the player's turn to act. """
        pass

    @abstractmethod
    def on_end_round(self, round_state: RoundStateClient):
        """ Called at the end of each round. """
        pass

    @abstractmethod
    def on_end_game(self, round_state: RoundStateClient, score: float):
        """ Called at the end of the game. """
        pass

class SimplePlayer(Player):
    def __init__(self):
        super().__init__()

    def on_start(self):
        print("Player called on game start")

    def on_round_start(self, round_state: RoundStateClient):
        print("Player called on round start")

    def get_action(self, round_state: RoundStateClient):
        print("Player called get action")

        raised = False
        for player_action in round_state.player_actions.values():
            if player_action == "Raise":
                raised = True
                break

        if not raised and round_state.round_num == 1:
            return PokerAction.RAISE, 100
        
        if round_state.current_bet == 0:
            return PokerAction.CHECK, 0
        

        return PokerAction.CALL, 0

    def on_end_round(self, round_state: RoundStateClient):
        print("Player called on end round")

    def on_end_game(self, round_state: RoundStateClient, score: float):
        print("Player called on end game, with score: ", score)