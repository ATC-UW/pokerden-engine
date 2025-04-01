from dataclasses import dataclass

@dataclass
class RoundStateClient:
    round_num: int
    round: str
    community_cards: list
    pot: int
    current_player: int
    current_bet: int
    min_raise: int
    max_raise: int
    player_bets: dict[int, int]
    player_actions: dict[int, str]