from typing import Tuple, Set, Dict, List

import eval7
from config import NUM_ROUNDS
from deck import PokerDeck
from game.round_state import RoundState
from poker_type.game import PokerRound, PokerAction
from poker_type.messsage import GameStateMessage
from poker_type.utils import get_poker_action_name_from_enum, get_round_name

GAME_ROUNDS = [PokerRound.UNSTARTED, PokerRound.PREFLOP, PokerRound.FLOP, PokerRound.TURN, PokerRound.RIVER]

class Game:
    def __init__(self, debug: bool = False):
        self.debug = debug
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
        self.score = {}

    def add_player(self, player_id: int):
        self.players.append(player_id)
        self.active_players.append(player_id)

    def print_debug(self):
        if self.debug:
            s = f"Players: {self.players} \n Active Players: {self.active_players} \n Hands: {self.hands} \n Board: {self.board} \n Round Index: {self.round_index} \n Total Pot: {self.total_pot} \n Historical Pots: {self.historical_pots} \n Player History: {self.player_history} \n \t Current Round: \n {self.current_round}"
            print(s)

    def is_next_round(self):
        can_continue = self.round_index < len(GAME_ROUNDS) - 1
        return can_continue and self.current_round.is_round_complete()
    
    def is_game_over(self):
        return self.round_index >= len(GAME_ROUNDS) - 1
    
    def get_current_round(self):
        return GAME_ROUNDS[self.round_index]
    
    def get_current_waiting_for(self):
        return self.current_round.get_current_player()
    
    def is_current_round_complete(self):
        return self.current_round.is_round_complete()

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
        self.score = {
            player: 0 for player in self.active_players
        }
        
        # Initialize the first round
        self.current_round = RoundState(self.active_players)

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
        final = {}
        for player in self.active_players:
            final[player] = 0

        for player in self.active_players:
            players_hand = self.hands[player].copy()
            players_hand.extend(self.board)
            final[player] = eval7.evaluate(players_hand)

        winner = max(final, key=final.get)
        # check if winner all in last round
        if self.player_history[PokerRound.RIVER.value]["player_actions"][winner] == PokerAction.ALL_IN:
            # TODO: split pot
            win_amount = 0
            for r in range(1, 5):
                win_amount += self.player_history[r]["player_bets"][winner]

            if(win_amount * 2 > self.total_pot):
                self.score[winner] = self.total_pot
            else:
                remain = self.total_pot - win_amount * 2
                for player in self.active_players:
                    self.score[player] += remain / (len(self.active_players))
                self.score[winner] += win_amount * 2
            if self.debug:
                print(f"Player {winner} wins with hand {self.hands[winner]} and all in")
        else:
            self.score[winner] = self.total_pot
            if self.debug:
                print(f"Player {winner} wins with hand {self.hands[winner]}")

        for player in self.players:
            for r in range(1, 5):
                if player in self.player_history[r]["player_bets"]:
                    self.score[player] -= self.player_history[r]["player_bets"][player]

        if self.debug:
            print(f"Scores: {self.score}")

    def get_final_score(self):
        return self.score
    
    def get_game_state(self) -> GameStateMessage:
        round_name = get_round_name(self.round_index)
        actions_text = {}
        for player in self.current_round.player_actions:
            if self.current_round.player_actions[player] == None:
                continue
            actions_text[player] = get_poker_action_name_from_enum(self.current_round.player_actions[player])

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
        )