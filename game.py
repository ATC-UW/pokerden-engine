from typing import Tuple, Set, Dict, List

import eval7
from config import NUM_ROUNDS
from deck import PokerDeck
from poker_types import PokerAction, PokerRound

GAME_ROUNDS = [PokerRound.UNSTARTED, PokerRound.PREFLOP, PokerRound.FLOP, PokerRound.TURN, PokerRound.RIVER]

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


    def update_player_action(self, player_id: int, action: PokerAction, amount: int = 0) -> None:
        """Update the round state based on a player's action"""

        if amount < 0:
            raise ValueError("Amount cannot be negative")

        self.player_actions[player_id] = action

        if action == PokerAction.FOLD:
            self.waiting_for.discard(player_id)
            self.player_actions[player_id] = PokerAction.FOLD
        elif action == PokerAction.CHECK:
            if self.bettor is not None:
                raise ValueError("Cannot check when there has been a raise")
            self.waiting_for.discard(player_id)
            self.player_actions[player_id] = PokerAction.CHECK
        elif action == PokerAction.CALL:
            call_amount = self.raise_amount - self.player_bets[player_id]
            if call_amount <= 0:
                raise ValueError("Cannot call with less than the raise amount")
            self.player_bets[player_id] += call_amount
            self.pot += call_amount
            self.waiting_for.discard(player_id)
            self.player_actions[player_id] = PokerAction.CALL
        elif action == PokerAction.RAISE:
            if amount <= self.raise_amount:
                raise ValueError("Raise amount must be higher than the current raise")
            self.raise_amount = self.player_bets[player_id] + amount
            self.bettor = player_id
            self.pot += self.raise_amount
            self.player_bets[player_id] += amount
            self.waiting_for = set(p for p in self.player_bets.keys() if p != player_id)
            for player in self.waiting_for.copy():
                if player in self.player_actions and self.player_actions[player] == PokerAction.FOLD:
                    self.waiting_for.discard(player)
                else:
                    self.player_actions[player] = None

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

class Game:
    def __init__(self):
        self.nums_round = NUM_ROUNDS
        self.players: List[int] = []
        self.active_players: List[int] = []
        self.deck = PokerDeck()
        self.hands: Dict[int, List[str]] = {}
        self.board: List[str] = []
        self.round_index = 0
        self.total_pot = 0
        self.historical_pots: List[int] = []
        self.player_history: Dict = {}
        self.current_round: RoundState = None

    def add_player(self, player_id: int):
        self.players.append(player_id)
        self.active_players.append(player_id)

    def print_debug(self):
        s = f"Players: {self.players} \n Active Players: {self.active_players} \n Hands: {self.hands} \n Board: {self.board} \n Round Index: {self.round_index} \n Total Pot: {self.total_pot} \n Historical Pots: {self.historical_pots} \n Player History: {self.player_history} \n \t Current Round: \n {self.current_round}"
        print(s)

    def start_game(self):
        self.deck = PokerDeck()
        self.deck.shuffle()
        self.round_index = 0

        # Deal two cards to each player
        for player in self.active_players:
            self.hands[player] = self.deck.deal(2)

        
        self.total_pot = 0
        self.historical_pots = []
        self.player_history = {}
        
        # Initialize the first round
        self.current_round = RoundState(self.active_players)

    def update_game(self, player_id: int, action: Tuple[PokerAction, int]):
        if player_id not in self.active_players:
            raise ValueError("Player is not active in the game")

        action_type, amount = action
        
        # Update round state
        self.current_round.update_player_action(player_id, action_type, amount)
        
        # Remove player from active players if they folded
        if action_type == PokerAction.FOLD:
            self.active_players.remove(player_id)

    def start_round(self):
        if self.round_index >= len(GAME_ROUNDS) - 1:
            self.end_game()
            return

        self.round_index += 1
        # Create new round state
        self.current_round = RoundState(self.active_players)

        if(GAME_ROUNDS[self.round_index] == PokerRound.PREFLOP):
            pass
        elif(GAME_ROUNDS[self.round_index] == PokerRound.FLOP):
            # Burn one card
            self.deck.deal(1)
            # Deal the flop
            self.board = self.deck.deal(3)
        else:
            self.deck.deal(1)  # Burn a card
            new_card = self.deck.deal(1)[0]  # Deal one new board card
            self.board.append(new_card)
        

    def end_round(self):
        if not self.current_round.is_round_complete():
            raise ValueError("Round cannot end while players are still waiting to act")
        
        self.historical_pots.append(self.current_round.pot)
        self.total_pot += self.current_round.pot
        self.player_history[self.round_index] =  {
            "pot": self.current_round.pot,
            "player_bets": self.current_round.player_bets,
            "player_actions": self.current_round.player_actions
        }

    def end_game(self):
        score = {}
        for player in self.active_players:
            score[player] = 0

        for player in self.active_players:
            players_hand = self.hands[player].copy()
            players_hand.extend(self.board)
            score[player] = eval7.evaluate(players_hand)

        winner = max(score, key=score.get)
        print(f"Player {winner} wins with hand {self.hands[winner]}")