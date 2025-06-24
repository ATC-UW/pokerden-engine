import unittest

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.game import Game
from poker_type.game import PokerAction, PokerRound

class TestTerminateGameEarly(unittest.TestCase):
    def test_early_game_end_all_fold(self):
        game = Game(debug=True)
        game.add_player(1)
        game.add_player(2)
        game.start_game()
        game.update_game(1, (PokerAction.CHECK, 0))
        game.update_game(2, (PokerAction.CHECK, 0))
        game.end_round()
        game.start_round()
        game.update_game(1, (PokerAction.FOLD, 0))
        game.update_game(2, (PokerAction.FOLD, 0))
        game.end_round()
        self.assertEqual(True, game.is_game_over())

    def test_early_game_end_preflop_fold(self):
        game = Game(debug=True)
        game.add_player(1)
        game.add_player(2)
        game.start_game()
        game.update_game(1, (PokerAction.FOLD, 0))
        game.update_game(2, (PokerAction.FOLD, 0))
        game.end_round()
        self.assertEqual(True, game.is_game_over())

    def test_early_game_end_river_fold(self):
        game = Game(debug=True)
        game.add_player(1)
        game.add_player(2)
        game.start_game()
        game.update_game(1, (PokerAction.CHECK, 0))
        game.update_game(2, (PokerAction.CHECK, 0))
        game.end_round()
        game.start_game()
        game.update_game(1, (PokerAction.CHECK, 0))
        game.update_game(2, (PokerAction.CHECK, 0))
        game.end_round()
        game.start_game()
        game.update_game(1, (PokerAction.CHECK, 0))
        game.update_game(2, (PokerAction.CHECK, 0))
        game.end_round()
        game.start_game()
        game.update_game(1, (PokerAction.FOLD, 0))
        game.update_game(2, (PokerAction.FOLD, 0))
        game.end_round()
        self.assertEqual(True, game.is_game_over())

    """
    Below are the tests that were used for checking the terminate game when 1 player is left functionality
    """

    # def test_early_game_end_one_left(self):
    #     game = Game(debug=True)
    #     game.add_player(1)
    #     game.add_player(2)
    #     game.add_player(3)
    #     game.start_game()
    #     game.update_game(1, (PokerAction.CHECK, 0))
    #     game.update_game(2, (PokerAction.CHECK, 0))
    #     game.update_game(3, (PokerAction.CHECK, 0))
    #     game.end_round()
    #     game.start_round()
    #     game.update_game(1, (PokerAction.FOLD, 0))
    #     game.update_game(2, (PokerAction.FOLD, 0))
    #     game.update_game(3, (PokerAction.CHECK, 0))
    #     game.end_round()
    #     self.assertEqual(True, game.is_game_over())
    #     expected_scores = {1: 0, 2: 0, 3: 0}
    #     actual_scores = game.score
    #     self.assertEqual(expected_scores, actual_scores)

    # def test_early_game_end_preflop_fold(self):
    #     game = Game(debug=True)
    #     game.add_player(1)
    #     game.add_player(2)
    #     game.add_player(3)
    #     game.start_game()
    #     game.update_game(1, (PokerAction.FOLD, 0))
    #     game.update_game(2, (PokerAction.FOLD, 0))
    #     game.update_game(3, (PokerAction.CHECK, 0))
    #     game.end_round()
    #     self.assertEqual(True, game.is_game_over())
    #     expected_scores = {1: 0, 2: 0, 3: 0}
    #     actual_scores = game.score
    #     self.assertEqual(expected_scores, actual_scores)

    # def test_early_game_end_flop_bet_payout(self):
    #     game = Game(debug=True)
    #     game.add_player(1)
    #     game.add_player(2)
    #     game.add_player(3)
    #     game.start_game()
    #     game.update_game(1, (PokerAction.RAISE, 100))
    #     game.update_game(2, (PokerAction.CALL, 100))
    #     game.update_game(3, (PokerAction.CALL, 100))
    #     game.end_round()
    #     game.start_round()
    #     game.update_game(1, (PokerAction.FOLD, 0))
    #     game.update_game(2, (PokerAction.FOLD, 0))
    #     game.update_game(3, (PokerAction.CHECK, 0))
    #     game.end_round()
    #     self.assertEqual(True, game.is_game_over())
    #     expected_scores = {1: -100, 2: -100, 3: 200}
    #     actual_scores = game.score
    #     self.assertEqual(expected_scores, actual_scores)

    # def test_early_game_end_turn_bet_payout(self):
    #     game = Game(debug=True)
    #     game.add_player(1)
    #     game.add_player(2)
    #     game.add_player(3)
    #     game.start_game()
    #     game.update_game(1, (PokerAction.RAISE, 100))
    #     game.update_game(2, (PokerAction.CALL, 100))
    #     game.update_game(3, (PokerAction.CALL, 100))
    #     game.end_round()
    #     game.start_game()
    #     game.update_game(1, (PokerAction.CHECK, 0))
    #     game.update_game(2, (PokerAction.RAISE, 150))
    #     game.update_game(3, (PokerAction.CALL, 150))
    #     game.update_game(1, (PokerAction.FOLD, 0))
    #     game.end_round()
    #     game.start_round()
    #     game.update_game(2, (PokerAction.RAISE, 300))
    #     game.update_game(3, (PokerAction.FOLD, 0))
    #     game.end_round()
    #     self.assertEqual(True, game.is_game_over())
        
    #     # Check scores
    #     expected_scores = {1: -100, 2: 350, 3: -250}
    #     actual_scores = game.score
    #     self.assertEqual(expected_scores, actual_scores)



if __name__ == '__main__':
    unittest.main()
