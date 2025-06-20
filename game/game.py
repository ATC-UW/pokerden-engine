from typing import Tuple, Set, Dict, List

import eval7
from config import NUM_ROUNDS
from deck import PokerDeck
from game.round_state import RoundState
from poker_type.game import PokerRound, PokerAction
from poker_type.messsage import GameStateMessage
from poker_type.utils import get_poker_action_name_from_enum, get_round_name

GAME_ROUNDS = [PokerRound.PREFLOP, PokerRound.FLOP, PokerRound.TURN, PokerRound.RIVER]

class Game:
    def __init__(self, debug: bool = False, blind_amount: int = 10):
        self.debug = debug
        self.nums_round = NUM_ROUNDS
        self.players: List[int] = []
        self.active_players: List[int] = []
        self.deck = PokerDeck()
        self.hands: Dict[int, List[eval7.Card]] = {}
        self.board: List[str] = []
        self.round_index = -1
        self.total_pot = 0
        self.historical_pots: List[int] = []
        self.player_history: Dict = {}
        self.current_round: RoundState = None
        self.score = {}
        self.is_running = False
        
        # Blind functionality
        self.blind_amount = blind_amount
        self.small_blind_player = None
        self.big_blind_player = None
        self.dealer_button_position = 0  # This will be set by the server

    def set_blind_amount(self, amount: int):
        """Set the blind amount for the game"""
        self.blind_amount = amount

    def get_blind_amount(self):
        """Get the current blind amount"""
        return self.blind_amount

    def get_small_blind_player(self):
        """Get the current small blind player"""
        return self.small_blind_player

    def get_big_blind_player(self):
        """Get the current big blind player"""
        return self.big_blind_player

    def set_dealer_button_position(self, position: int):
        """Set the dealer button position (called by server)"""
        self.dealer_button_position = position

    def assign_blinds(self):
        """Assign small and big blind players based on dealer button position"""
        if len(self.active_players) < 2:
            return
        
        if len(self.active_players) == 2:
            # In heads-up, dealer is small blind
            self.small_blind_player = self.active_players[self.dealer_button_position % len(self.active_players)]
            self.big_blind_player = self.active_players[(self.dealer_button_position + 1) % len(self.active_players)]
        else:
            # In multi-player, small blind is to the left of dealer, big blind is to the left of small blind
            self.small_blind_player = self.active_players[(self.dealer_button_position + 1) % len(self.active_players)]
            self.big_blind_player = self.active_players[(self.dealer_button_position + 2) % len(self.active_players)]

    def post_blinds(self):
        """Automatically post the blinds for small and big blind players"""
        if self.small_blind_player and self.big_blind_player:
            # Post small blind
            self.current_round.update_player_action(
                self.small_blind_player, 
                PokerAction.RAISE, 
                self.blind_amount // 2
            )
            
            # Post big blind
            self.current_round.update_player_action(
                self.big_blind_player, 
                PokerAction.RAISE, 
                self.blind_amount
            )

    def assign_player_ids_hand(self, player_id: int, hand: List[str]):
        """
        Assign a hand to a player. This is only used for testing purposes.
        In a real game, the hands are dealt by the deck.
        """
        if not self.debug:
            return

        if player_id not in self.players:
            raise ValueError("Player ID not found in the game")
        self.hands[player_id] = hand

    def assign_board(self, board: List[str]):
        """
        Assign a board to the game. This is only used for testing purposes.
        In a real game, the board is dealt by the deck.
        """
        if not self.debug:
            return

        self.board = board

    def add_player(self, player_id: int):
        self.players.append(player_id)
        self.active_players.append(player_id)

    def get_active_players(self):
        return self.active_players
    
    def get_player_hands(self, player_id: int):
        return self.hands[player_id]

    def print_debug(self):
        if self.debug:
            s = f"Players: {self.players} \n Active Players: {self.active_players} \n Hands: {self.hands} \n Board: {self.board} \n Round Index: {self.round_index} \n Total Pot: {self.total_pot} \n Historical Pots: {self.historical_pots} \n Player History: {self.player_history} \n \t Current Round: \n {self.current_round}"
            print(s)

    def is_next_round(self):
        if self.active_players == []:
            print("No active players")
            return False
        can_continue = self.round_index < len(GAME_ROUNDS) - 1
        return can_continue and self.current_round.is_round_complete()
    
    def is_game_over(self):
        if self.active_players == [] and self.players != []:
            if self.is_running:
                self.is_running = False
            return not self.is_running

        if self.round_index >= len(GAME_ROUNDS):
            print("This can't happen")
            return False

        return not self.is_running
    
    def get_current_round(self):
        return GAME_ROUNDS[self.round_index]
    
    def get_current_waiting_for(self):
        return self.current_round.get_current_player()
    
    def get_player_hands(self, player_id: int) -> List[str]:
        return [str(card) for card in self.hands[player_id]]

    def is_current_round_complete(self):
        return self.current_round.is_round_complete()

    def start_game(self):
        self.deck = PokerDeck()
        self.deck.shuffle()
        self.round_index = 0
        self.is_running = True

        # Deal two cards to each player
        for player in self.active_players:
            self.hands[player] = self.deck.deal(2)

        
        self.total_pot = 0
        self.historical_pots = []
        self.player_history = {}
        self.score = {
            player: 0 for player in self.active_players
        }
        
        # Assign blinds for this game
        self.assign_blinds()
        
        # Initialize the first round
        self.current_round = RoundState(self.active_players)
        
        # Don't post blinds automatically - let clients handle it when they receive action requests

    def update_game(self, player_id: int, action: Tuple[PokerAction, int]):
        if player_id not in self.active_players:
            raise ValueError("Player is not active in the game")
        
        action_type, amount = action
        # All in propagation
        if self.round_index > 1:
            if self.player_history[self.round_index - 1]["player_actions"][player_id] == PokerAction.ALL_IN:
                if self.debug:
                    print(f"Player {player_id} is all in from previous round")
                action_type, amount = PokerAction.ALL_IN, 0

        # Update round state
        self.current_round.update_player_action(player_id, action_type, amount)
        
        # Remove player from active players if they folded
        if action_type == PokerAction.FOLD:
            self.active_players.remove(player_id)

    def start_round(self):
        if not self.is_next_round():
            self.end_game()
            return

        self.round_index += 1
        # Create new round state
        self.current_round = RoundState(self.active_players)

        if(GAME_ROUNDS[self.round_index] == PokerRound.FLOP):
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
        # Ensure current round bets are included in player history if not already
        if self.current_round and self.round_index not in self.player_history:
            self.player_history[self.round_index] = {
                "pot": self.current_round.pot,
                "player_bets": self.current_round.player_bets,
                "player_actions": self.current_round.player_actions
            }
        
        # Calculate total pot from all rounds - this is the most reliable approach
        total_pot_amount = 0
        for round_index in self.player_history:
            round_bets = self.player_history[round_index]["player_bets"]
            total_pot_amount += sum(round_bets.values())
        
        if self.debug:
            print(f"Total pot amount calculated from all rounds: {total_pot_amount}")
        
        # Use side pots from current round if they exist, but update their amounts to reflect the total
        if (self.current_round and hasattr(self.current_round, 'pots') and 
            self.current_round.pots and len(self.current_round.pots) > 1):
            # Multiple pots exist (side pot scenario) - preserve the structure but fix amounts
            if self.debug:
                print(f"Using side pot structure with {len(self.current_round.pots)} pots")
            
            # Force recalculation to ensure correct amounts
            # Temporarily restore current round bets to calculate side pots correctly
            total_current_bets = sum(self.current_round.player_bets.values())
            if total_current_bets == 0:
                # Current round has no bets, use the last round that had bets
                for round_idx in reversed(list(self.player_history.keys())):
                    if sum(self.player_history[round_idx]["player_bets"].values()) > 0:
                        self.current_round.player_bets = self.player_history[round_idx]["player_bets"]
                        break
            
            self.current_round._create_side_pots()
            final_pots = self.current_round.pots
        else:
            # Single pot scenario
            if self.debug:
                print("Using single pot for all players")
            final_pots = [type('Pot', (), {'amount': total_pot_amount, 'eligible_players': set(self.active_players)})()]
        
        # Evaluate hands for all active players
        hand_values = {}
        for player in self.active_players:
            players_hand = self.hands[player].copy()
            players_hand.extend(self.board)
            hand_values[player] = eval7.evaluate(players_hand)
        
        # Initialize all player scores to 0
        for player in self.players:
            self.score[player] = 0
        
        if self.debug:
            print(f"Hand values: {hand_values}")
            print(f"Distributing {len(final_pots)} pot(s)")
        
        # Award each pot to the best hand among eligible players
        for i, pot in enumerate(final_pots):
            print(f"Pot {i}: {pot.amount} chips, eligible players: {pot.eligible_players}")
            print(f"Active players: {self.active_players}")
            print(f"Player history: {self.player_history}")
            if pot.amount == 0:
                continue
                
            # Find eligible players who are still active
            eligible_active_players = pot.eligible_players.intersection(set(self.active_players))
            
            if len(eligible_active_players) == 0:
                if self.debug:
                    print(f"Pot {i}: No eligible active players, pot amount {pot.amount} is lost")
                continue
            
            # Find the best hand among eligible players
            eligible_hand_values = {player: hand_values[player] for player in eligible_active_players}
            pot_winners = [player for player, value in eligible_hand_values.items() 
                          if value == max(eligible_hand_values.values())]
            
            # Split pot among tied winners
            pot_share = pot.amount // len(pot_winners)
            remainder = pot.amount % len(pot_winners)
            
            if self.debug:
                print(f"Pot {i}: {pot.amount} chips, eligible players: {eligible_active_players}")
                print(f"Winners: {pot_winners}, each gets {pot_share} chips")
                if remainder > 0:
                    print(f"Remainder of {remainder} chips goes to player {pot_winners[0]}")
            
            for j, winner in enumerate(pot_winners):
                self.score[winner] += pot_share
                # Give remainder to first winner (arbitrary but fair)
                if j == 0:
                    self.score[winner] += remainder

        if self.debug:
            print(f"Player hands:")
            for player in self.active_players:
                print(f"  Player {player}: {self.hands[player]}")
            print(f"Total pot distributed: {sum(pot.amount for pot in final_pots)}")

        # Subtract each player's total bets from their score
        for player in self.players:
            total_bets = 0
            for round_index in self.player_history:
                if player in self.player_history[round_index]["player_bets"]:
                    total_bets += self.player_history[round_index]["player_bets"][player]
            self.score[player] -= total_bets
            
            if self.debug:
                print(f"Player {player}: total bets = {total_bets}, final score = {self.score[player]}")

        if True:
            print(f"Final Scores: {self.score}")
            # Verify zero-sum
            total_score = sum(self.score.values())
            print(f"Total score (should be 0): {total_score}")

        self.is_running = False
        # Blind rotation is now handled by the server

    def get_final_score(self):
        return self.score
    
    def get_game_state(self) -> GameStateMessage:
        round_name = get_round_name(self.round_index)
        actions_text = {}
        for player in self.current_round.player_actions:
            if self.current_round.player_actions[player] == None:
                continue
            actions_text[player] = get_poker_action_name_from_enum(self.current_round.player_actions[player])

        # Get side pot information
        side_pots_info = self.current_round.get_side_pots_info() if hasattr(self.current_round, 'get_side_pots_info') else []

        return GameStateMessage(
            round_num=self.round_index,
            round=round_name,
            community_cards=self.board,
            pot=self.current_round.pot,
            current_player=self.current_round.get_current_player(),
            current_bet=self.current_round.raise_amount,
            player_bets=self.current_round.player_bets,
            player_actions=actions_text,
            min_raise=self.current_round.raise_amount,
            max_raise=self.current_round.raise_amount * 2,
            side_pots=side_pots_info
        )