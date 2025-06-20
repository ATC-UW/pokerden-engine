import unittest
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game import Game
from poker_type.game import PokerAction
import eval7


class TestSidePots(unittest.TestCase):
    
    def test_simple_side_pot_scenario_with_scoring(self):
        """Test a simple side pot scenario with one all-in player and score calculation"""
        game = Game(debug=True)
        
        # Add three players
        game.add_player(1)
        game.add_player(2) 
        game.add_player(3)
        
        game.start_game()
        
        # Set specific hands for predictable results
        # Player 1 gets pair of Aces (strong hand)
        # Player 2 gets pair of Kings  
        # Player 3 gets high card
        game.hands[1] = [eval7.Card("As"), eval7.Card("Ad")]
        game.hands[2] = [eval7.Card("Ks"), eval7.Card("Kd")]
        game.hands[3] = [eval7.Card("Qh"), eval7.Card("Jc")]
        
        # Set a board
        game.board = [eval7.Card("2h"), eval7.Card("3s"), eval7.Card("4d"), eval7.Card("7c"), eval7.Card("9h")]
        
        # Player 1 goes all-in for 50
        game.update_game(1, (PokerAction.ALL_IN, 50))
        
        # Player 2 raises to 100  
        game.update_game(2, (PokerAction.RAISE, 100))
        
        # Player 3 calls 100
        game.update_game(3, (PokerAction.CALL, 100))
        
        # Check that side pots are created correctly
        self.assertEqual(len(game.current_round.pots), 2)
        
        # Main pot should be 150 (50 from each player)
        main_pot = game.current_round.pots[0]
        self.assertEqual(main_pot.amount, 150)
        self.assertEqual(main_pot.eligible_players, {1, 2, 3})
        
        # Side pot should be 100 (50 each from players 2 and 3)  
        side_pot = game.current_round.pots[1]
        self.assertEqual(side_pot.amount, 100)
        self.assertEqual(side_pot.eligible_players, {2, 3})
        
        print(f"Main pot: {main_pot.amount} chips, eligible: {main_pot.eligible_players}")
        print(f"Side pot: {side_pot.amount} chips, eligible: {side_pot.eligible_players}")
        
        # End the round and game to calculate scores
        game.end_round()
        game.end_game()
        
        # Player 1 should win main pot (150) with pair of Aces
        # Player 2 should win side pot (100) with pair of Kings vs Player 3's high card
        # Verify final scores: Player 1: 150-50=100, Player 2: 100-100=0, Player 3: 0-100=-100
        
        print(f"Final scores: {game.score}")
        self.assertEqual(game.score[1], 100)  # Won main pot, paid 50
        self.assertEqual(game.score[2], 0)    # Won side pot, paid 100  
        self.assertEqual(game.score[3], -100) # Won nothing, paid 100
        
        # Verify zero-sum
        self.assertEqual(sum(game.score.values()), 0)
    
    def test_multiple_side_pots_with_scoring(self):
        """Test scenario with multiple all-in players creating multiple side pots with score calculation"""
        game = Game(debug=True)
        
        # Add four players
        game.add_player(1)
        game.add_player(2)
        game.add_player(3)
        game.add_player(4)
        
        game.start_game()
        
        # Set specific hands for predictable results
        # Player 1: Pair of Aces (strongest)
        # Player 2: Pair of Kings 
        # Player 3: Pair of Queens
        # Player 4: High card Jack (weakest)
        game.hands[1] = [eval7.Card("As"), eval7.Card("Ad")]
        game.hands[2] = [eval7.Card("Ks"), eval7.Card("Kd")]
        game.hands[3] = [eval7.Card("Qs"), eval7.Card("Qd")]
        game.hands[4] = [eval7.Card("Jh"), eval7.Card("Tc")]
        
        # Set a board with no pairs/straights/flushes to keep hands predictable
        game.board = [eval7.Card("2h"), eval7.Card("3s"), eval7.Card("4d"), eval7.Card("7c"), eval7.Card("9h")]
        
        # Player 1 goes all-in for 30
        game.update_game(1, (PokerAction.ALL_IN, 30))
        
        # Player 2 goes all-in for 60 
        game.update_game(2, (PokerAction.ALL_IN, 60))
        
        # Player 3 goes all-in for 90
        game.update_game(3, (PokerAction.ALL_IN, 90))
        
        # Player 4 calls 90
        game.update_game(4, (PokerAction.CALL, 90))
        
        # Should create 3 pots
        self.assertEqual(len(game.current_round.pots), 3)
        
        # First pot: 30 * 4 = 120, all players eligible
        pot1 = game.current_round.pots[0]
        self.assertEqual(pot1.amount, 120)
        self.assertEqual(pot1.eligible_players, {1, 2, 3, 4})
        
        # Second pot: 30 * 3 = 90, players 2,3,4 eligible
        pot2 = game.current_round.pots[1]
        self.assertEqual(pot2.amount, 90)
        self.assertEqual(pot2.eligible_players, {2, 3, 4})
        
        # Third pot: 30 * 2 = 60, players 3,4 eligible  
        pot3 = game.current_round.pots[2]
        self.assertEqual(pot3.amount, 60)
        self.assertEqual(pot3.eligible_players, {3, 4})
        
        print(f"Pot 1: {pot1.amount} chips, eligible: {pot1.eligible_players}")
        print(f"Pot 2: {pot2.amount} chips, eligible: {pot2.eligible_players}")
        print(f"Pot 3: {pot3.amount} chips, eligible: {pot3.eligible_players}")
        
        # End the round and game to calculate scores
        game.end_round()
        game.end_game()
        
        # Expected winners:
        # Pot 1 (120): Player 1 wins with Aces
        # Pot 2 (90): Player 2 wins with Kings (among players 2,3,4)
        # Pot 3 (60): Player 3 wins with Queens (among players 3,4)
        
        print(f"Final scores: {game.score}")
        
        # Player 1: wins 120, paid 30 = +90
        # Player 2: wins 90, paid 60 = +30
        # Player 3: wins 60, paid 90 = -30
        # Player 4: wins 0, paid 90 = -90
        
        self.assertEqual(game.score[1], 90)   # Won pot 1
        self.assertEqual(game.score[2], 30)   # Won pot 2
        self.assertEqual(game.score[3], -30)  # Won pot 3
        self.assertEqual(game.score[4], -90)  # Won nothing
        
        # Verify zero-sum
        self.assertEqual(sum(game.score.values()), 0)
    
    def test_no_side_pots_equal_bets_with_scoring(self):
        """Test that no side pots are created when all players bet equally, with score calculation"""
        game = Game(debug=True)
        
        game.add_player(1)
        game.add_player(2)
        game.add_player(3)
        
        game.start_game()
        
        # Set hands - Player 2 has the best hand
        game.hands[1] = [eval7.Card("7s"), eval7.Card("3d")]  # Weak hand
        game.hands[2] = [eval7.Card("As"), eval7.Card("Ad")]  # Pair of Aces (best hand)
        game.hands[3] = [eval7.Card("9h"), eval7.Card("8c")]  # High card
        
        # Set a board that doesn't help anyone make straights/flushes
        game.board = [eval7.Card("2h"), eval7.Card("4s"), eval7.Card("6d"), eval7.Card("Jc"), eval7.Card("Kh")]
        
        # All players bet the same amount
        game.update_game(1, (PokerAction.RAISE, 50))
        game.update_game(2, (PokerAction.CALL, 50))
        game.update_game(3, (PokerAction.CALL, 50))
        
        # Should only have one pot
        self.assertEqual(len(game.current_round.pots), 1)
        self.assertEqual(game.current_round.pots[0].amount, 150)
        self.assertEqual(game.current_round.pots[0].eligible_players, {1, 2, 3})
        
        # End the round and game to calculate scores
        game.end_round()
        game.end_game()
        
        # Player 2 should win the entire pot with pair of Aces
        print(f"Final scores: {game.score}")
        self.assertEqual(game.score[1], -50)  # Lost bet
        self.assertEqual(game.score[2], 100)  # Won pot minus bet: 150-50=100
        self.assertEqual(game.score[3], -50)  # Lost bet
        
        # Verify zero-sum
        self.assertEqual(sum(game.score.values()), 0)


if __name__ == '__main__':
    unittest.main() 