from enum import Enum

class PokerAction(Enum):
    FOLD = 1
    CHECK = 2
    CALL = 3
    RAISE = 4
    ALL_IN = 5

class PokerRound(Enum):
    PREFLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4
