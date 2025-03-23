from poker_type.game import PokerRound

ROUND_NAMES_MAPPING_FROM_INDEX = {
    0: "Unstarted",
    1: "Preflop",
    2: "Flop",
    3: "Turn",
    4: "River"
}

ROUND_NAMES_MAPING = {
    PokerRound.UNSTARTED: "Unstarted",
    PokerRound.PREFLOP: "Preflop",
    PokerRound.FLOP: "Flop",
    PokerRound.TURN: "Turn",
    PokerRound.RIVER: "River"
}

def get_round_name(round_index: int) -> str:

    if round_index not in ROUND_NAMES_MAPPING_FROM_INDEX:
        raise ValueError(f"Invalid round index: {round_index}")

    return ROUND_NAMES_MAPPING_FROM_INDEX[round_index]

def get_round_name_from_enum(round: PokerRound) -> str:
    if round not in ROUND_NAMES_MAPING:
        raise ValueError(f"Invalid round enum: {round}")
    return ROUND_NAMES_MAPING[round]