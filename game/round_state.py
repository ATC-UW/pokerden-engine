
from poker_type.game import PokerAction
from typing import List, Dict, Set


class RoundState:
    def __init__(self, active_players: List[int]):
        self.pot = 0
        self.raise_amount = 0
        self.bettor = None
        self.waiting_for: Set[int] = set(active_players)
        self.player_bets: Dict[int, int] = {player: 0 for player in active_players}
        self.player_actions: Dict[int, PokerAction] = {}
    
    def __str__(self):
        return f"\tPot: {self.pot} \n\t Raise Amount: {self.raise_amount} \n\t Bettor: {self.bettor} \n\t Waiting For: {self.waiting_for} \n\t Player Bets: {self.player_bets} \n\t Player Actions: {self.player_actions}"

    def print_debug(self):
        s = f"Pot: {self.pot} \n Raise Amount: {self.raise_amount} \n Bettor: {self.bettor} \n Waiting For: {self.waiting_for} \n Player Bets: {self.player_bets} \n Player Actions: {self.player_actions}"
        print(s)


    def _update_waiting_for_after_raise(self, player_id: int) -> None:
        self.waiting_for = set(p for p in self.player_bets.keys() if p != player_id)
        for player in self.waiting_for.copy():
            if player in self.player_actions and self.player_actions[player] in [PokerAction.FOLD, PokerAction.ALL_IN]:
                self.waiting_for.discard(player)
            else:
                self.player_actions[player] = None

    def update_player_action(self, player_id: int, action: PokerAction, amount: int = 0) -> None:
        """Update the round state based on a player's action"""

        if amount < 0:
            raise ValueError("Amount cannot be negative")

        self.player_actions[player_id] = action

        if player_id not in self.waiting_for:
            raise ValueError("Player is not waiting for their turn")

        if action == PokerAction.FOLD:
            self.waiting_for.discard(player_id)
            self.player_actions[player_id] = PokerAction.FOLD
        elif action == PokerAction.CHECK:
            if self.bettor is not None:
                raise ValueError("Cannot check when there has been a raise")
            self.waiting_for.discard(player_id)
            self.player_actions[player_id] = PokerAction.CHECK
        elif action == PokerAction.CALL:
            """
            Call the current raise amount, the amount is the difference between the
            current raise amount and the player's current bet. 
            input amount doesn't matter
            """
            call_amount = self.raise_amount - self.player_bets[player_id]
            if call_amount <= 0:
                raise ValueError("Cannot call with less than the raise amount")
            self.player_bets[player_id] += call_amount
            self.pot += call_amount
            self.waiting_for.discard(player_id)
            self.player_actions[player_id] = PokerAction.CALL
        elif action == PokerAction.ALL_IN:
            self.player_bets[player_id] += amount
            self.pot += amount
            self.waiting_for.discard(player_id)
            self.player_actions[player_id] = PokerAction.ALL_IN
            if(amount > self.raise_amount):
                self.raise_amount = amount
                self.bettor = player_id
                self._update_waiting_for_after_raise(player_id)

        elif action == PokerAction.RAISE:
            if amount + self.player_bets[player_id] <= self.raise_amount:
                raise ValueError("Raise amount + current bet must be higher than the current raise")
            self.raise_amount = self.player_bets[player_id] + amount
            self.bettor = player_id
            self.pot += self.raise_amount
            self.player_bets[player_id] += amount
            self.waiting_for = set(p for p in self.player_bets.keys() if p != player_id)
            self._update_waiting_for_after_raise(player_id)

    def is_round_complete(self) -> bool:
        """Check if the current round is complete"""
        return len(self.waiting_for) == 0

    def reset_for_next_round(self, active_players: List[int]) -> None:
        """Reset the round state for a new round"""
        self.pot = 0
        self.raise_amount = 0
        self.bettor = None
        self.waiting_for = set(active_players)
        self.player_bets = {player: 0 for player in active_players}
        self.player_actions = {}

    def get_current_player(self) -> Set[int]:
        """Get the current player in the round"""
        if len(self.waiting_for) == 0:
            return set()
        return self.waiting_for