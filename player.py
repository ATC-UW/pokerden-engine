from abc import ABC, abstractmethod
START_MONEY = 1000

class Player(ABC):
    def __init__(self):
        """ Initializes the player. """
        pass

    @abstractmethod
    def on_start(self):
        """ Called when the game starts. """
        pass

    @abstractmethod
    def on_round_start(self, game_state, round_state):
        """ Called at the start of each round. """
        pass

    @abstractmethod
    def get_action(self, game_state, round_state):
        """ Called when it is the player's turn to act. """
        pass

    @abstractmethod
    def on_end_round(self, game_state, round_state, result):
        """ Called at the end of each round. """
        pass

    @abstractmethod
    def on_end_game(self, game_state, round_state, result):
        """ Called at the end of the game. """
        pass
    


        


    