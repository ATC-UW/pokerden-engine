from poker_type.game import PokerAction
from typing import List, Dict, Set
from dataclasses import dataclass

@dataclass
class Pot:
    """Represents a single pot (main pot or side pot)"""
    amount: int
    eligible_players: Set[int]  # Players who can win this pot
    
    def __init__(self, amount: int = 0, eligible_players: Set[int] = None):
        self.amount = amount
        self.eligible_players = eligible_players if eligible_players else set()

class RoundState:
    def __init__(self, active_players: List[int]):
        self.pots: List[Pot] = [Pot(0, set(active_players))]  # Start with main pot
        self.raise_amount = 0
        self.bettor = None
        self.waiting_for: Set[int] = set(active_players)
        self.player_bets: Dict[int, int] = {player: 0 for player in active_players}
        self.player_actions: Dict[int, PokerAction] = {}
        self.all_in_players: Set[int] = set()  # Track all-in players
    
    @property
    def pot(self) -> int:
        """Total pot amount across all pots (for backward compatibility)"""
        return sum(pot.amount for pot in self.pots)
    
    def __str__(self):
        pots_str = ", ".join([f"Pot {i}: {pot.amount} (players: {pot.eligible_players})" for i, pot in enumerate(self.pots)])
        return f"\tPots: [{pots_str}] \n\t Raise Amount: {self.raise_amount} \n\t Bettor: {self.bettor} \n\t Waiting For: {self.waiting_for} \n\t Player Bets: {self.player_bets} \n\t Player Actions: {self.player_actions} \n\t All-in Players: {self.all_in_players}"

    def print_debug(self):
        pots_str = ", ".join([f"Pot {i}: {pot.amount} (players: {pot.eligible_players})" for i, pot in enumerate(self.pots)])
        s = f"Pots: [{pots_str}] \n Raise Amount: {self.raise_amount} \n Bettor: {self.bettor} \n Waiting For: {self.waiting_for} \n Player Bets: {self.player_bets} \n Player Actions: {self.player_actions} \n All-in Players: {self.all_in_players}"
        print(s)

    def _create_side_pots(self):
        """Create side pots when players have unequal investments"""
        # Get all active players (not folded)
        active_players = set()
        for player_id, action in self.player_actions.items():
            if action != PokerAction.FOLD:
                active_players.add(player_id)
        
        if len(active_players) <= 1:
            return  # Not enough players for side pots
        
        # Get unique bet levels in ascending order
        bet_levels = sorted(set(bet for bet in self.player_bets.values() if bet > 0))
        
        if len(bet_levels) <= 1:
            # All players bet the same amount
            total_pot = sum(self.player_bets.values())
            self.pots = [Pot(total_pot, active_players)]
            return
        
        # Clear existing pots and recreate them
        self.pots = []
        
        # Create pots for each betting level
        for i, current_level in enumerate(bet_levels):
            prev_level = bet_levels[i-1] if i > 0 else 0
            level_contribution = current_level - prev_level
            
            # Find players who contributed to this level (bet >= current_level)
            eligible_players = set()
            contributing_count = 0
            for player_id, bet_amount in self.player_bets.items():
                if player_id in active_players and bet_amount >= current_level:
                    eligible_players.add(player_id)
                    contributing_count += 1
            
            if contributing_count > 0 and level_contribution > 0:
                pot_amount = level_contribution * contributing_count
                self.pots.append(Pot(pot_amount, eligible_players))
        
        # If no pots were created, create a single main pot
        if len(self.pots) == 0:
            total_pot = sum(self.player_bets.values())
            self.pots = [Pot(total_pot, active_players)]

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
            self.waiting_for.discard(player_id)
            self.player_actions[player_id] = PokerAction.CALL
        elif action == PokerAction.ALL_IN:
            self.player_bets[player_id] += amount
            self.all_in_players.add(player_id)
            self.waiting_for.discard(player_id)
            self.player_actions[player_id] = PokerAction.ALL_IN
            if self.player_bets[player_id] > self.raise_amount:
                self.raise_amount = self.player_bets[player_id]
                self.bettor = player_id
                self._update_waiting_for_after_raise(player_id)
        elif action == PokerAction.RAISE:
            if amount + self.player_bets[player_id] <= self.raise_amount:
                raise ValueError("Raise amount + current bet must be higher than the current raise")
            self.raise_amount = self.player_bets[player_id] + amount
            self.bettor = player_id
            self.player_bets[player_id] += amount
            self.waiting_for = set(p for p in self.player_bets.keys() if p != player_id)
            self._update_waiting_for_after_raise(player_id)
        
        # Update pots after any action that changes bet amounts
        self._update_pots()

    def _update_pots(self):
        """Update pot amounts based on current player bets"""
        # Always try to create side pots when there are unequal bet amounts
        bet_amounts = [amount for amount in self.player_bets.values() if amount > 0]
        if len(set(bet_amounts)) > 1:
            # Unequal bet amounts - create side pots
            self._create_side_pots()
        else:
            # Equal bet amounts - use simple pot calculation
            total_contributed = sum(self.player_bets.values())
            if len(self.pots) == 1:
                self.pots[0].amount = total_contributed
            else:
                # Reset to single pot
                active_players = set()
                for player_id, action in self.player_actions.items():
                    if action != PokerAction.FOLD:
                        active_players.add(player_id)
                self.pots = [Pot(total_contributed, active_players)]

    def is_round_complete(self) -> bool:
        """Check if the current round is complete"""
        if len(self.waiting_for) == 0:
            # Create final side pots when round is complete
            self._create_side_pots()
            return True
        return False

    def reset_for_next_round(self, active_players: List[int]) -> None:
        """Reset the round state for a new round"""
        # Keep track of players who are still all-in from previous rounds
        still_all_in = self.all_in_players.intersection(set(active_players))
        
        self.pots = [Pot(0, set(active_players))]
        self.raise_amount = 0
        self.bettor = None
        self.waiting_for = set(active_players) - still_all_in  # All-in players don't act
        self.player_bets = {player: 0 for player in active_players}
        self.player_actions = {}
        self.all_in_players = still_all_in

    def get_current_player(self) -> Set[int]:
        """Get the current player in the round"""
        if len(self.waiting_for) == 0:
            return set()
        return self.waiting_for

    def get_side_pots_info(self) -> List[Dict]:
        """Get information about all pots for display purposes"""
        return [
            {
                "amount": pot.amount,
                "eligible_players": list(pot.eligible_players)
            }
            for pot in self.pots
        ]