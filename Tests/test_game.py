import unittest
from xml.dom import InvalidStateErr

from game.game import Game
from poker_type.game import PokerAction, PokerRound


class TestAddPlayer(unittest.TestCase):
    def test_add_no_player(self):
        game = Game(debug=True)
        self.assertEqual(game.players, [])
        self.assertEqual(game.active_players, [])

    def test_add_one_player(self):
        game = Game(debug=True)
        game.add_player(99)
        self.assertEqual(game.players, [99])
        self.assertEqual(game.active_players, [99])

    def test_add_mult_players(self):
        game = Game(debug=True)
        game.add_player(99)
        game.add_player(11)
        game.add_player(22)
        self.assertEqual(game.players, [99, 11, 22])
        self.assertEqual(game.active_players, [99, 11, 22])

class TestIsNextRound(unittest.TestCase):
    def test_player_still_playing_non_river(self):
        game = Game(debug=True)
        game.add_player(1)
        game.add_player(2)
        game.add_player(3)
        game.start_game()
        game.update_game(1, (PokerAction.FOLD, 0))
        game.update_game(2, (PokerAction.FOLD, 0))
        self.assertEqual(False, game.is_next_round())

    def test_all_acts_non_river_round_not_end(self):
        game = Game(debug=True)
        game.add_player(1)
        game.add_player(2)
        game.add_player(3)
        game.start_game()
        game.update_game(1, (PokerAction.FOLD, 0))
        game.update_game(2, (PokerAction.FOLD, 0))
        game.update_game(3, (PokerAction.FOLD, 0))
        self.assertEqual(False, game.is_next_round())

    def test_all_acts_non_river_round_end(self):
        game = Game(debug=True)
        game.add_player(1)
        game.add_player(2)
        game.add_player(3)
        game.start_game()
        game.update_game(1, (PokerAction.CHECK, 0))
        game.update_game(2, (PokerAction.CHECK, 0))
        game.update_game(3, (PokerAction.CHECK, 0))
        game.end_round()
        self.assertEqual(True, game.is_next_round())

    def test_river(self):
        game = Game(debug=True)
        game.add_player(1)
        game.start_game()
        game.update_game(1, (PokerAction.CHECK, 0))
        game.end_round()
        game.start_round()
        game.update_game(1, (PokerAction.CHECK, 0))
        game.end_round()
        game.start_round()
        game.update_game(1, (PokerAction.CHECK, 0))
        game.end_round()
        game.start_round()
        game.update_game(1, (PokerAction.CHECK, 0))
        self.assertEqual(False, game.is_next_round())

class TestIsGameOver(unittest.TestCase):
    def test_unstarted(self):
        game = Game(debug=True)
        game.start_game()
        self.assertEqual(False, game.is_game_over())

    def test_pre_flop(self):
        game = Game(debug=True)
        game.start_game()
        game.start_round()
        self.assertEqual(False, game.is_game_over())

    def test_flop(self):
        game = Game(debug=True)
        game.start_game()
        game.start_round()
        game.end_round()
        game.start_round()
        self.assertEqual(False, game.is_game_over())

    def test_turn(self):
        game = Game(debug=True)
        game.start_game()
        game.start_round()
        game.end_round()
        game.start_round()
        game.end_round()
        game.start_round()
        self.assertEqual(False, game.is_game_over())

    def test_river(self):
        game = Game(debug=True)
        game.start_game()
        game.start_round()
        game.end_round()
        game.start_round()
        game.end_round()
        game.start_round()
        game.end_round()
        game.start_round()
        self.assertEqual(False, game.is_game_over())

    def test_river_end_but_not_end_game(self):
        game = Game(debug=True)
        game.start_game()
        game.start_round()
        game.end_round()
        game.start_round()
        game.end_round()
        game.start_round()
        game.end_round()
        game.start_round()
        game.end_round()
        self.assertEqual(False, game.is_game_over())

    def test_end_game(self):
        game = Game(debug=True)
        game.start_game()
        game.start_round()
        game.end_round()
        game.start_round()
        game.end_round()
        game.start_round()
        game.end_round()
        game.start_round()
        game.end_round()
        game.end_game()
        self.assertEqual(True, game.is_game_over())

class TestGetCurrentRound(unittest.TestCase):
    def test_preflop(self):
        game = Game(debug=True)
        game.start_game()
        self.assertEqual(PokerRound.PREFLOP, game.get_current_round())

    def test_flop(self):
        game = Game(debug=True)
        game.start_game()
        game.end_round()
        game.start_round()
        self.assertEqual(PokerRound.FLOP, game.get_current_round())

    def test_turn(self):
        game = Game(debug=True)
        game.start_game()
        game.end_round()
        game.start_round()
        game.end_round()
        game.start_round()
        self.assertEqual(PokerRound.TURN, game.get_current_round())

    def test_river(self):
        game = Game(debug=True)
        game.start_game()
        game.end_round()
        game.start_round()
        game.end_round()
        game.start_round()
        game.end_round()
        game.start_round()
        self.assertEqual(PokerRound.RIVER, game.get_current_round())

class TestStartGame(unittest.TestCase):
    def test_not_started(self):
        game = Game(debug=True)
        game.add_player(1)
        self.assertEqual(-1, game.round_index)
        self.assertEqual(None, game.current_round)

    def test_start_no_player(self):
        # Not sure if we could start game without player (assume that we can)
        game = Game(debug=True)
        game.start_game()
        self.assertEqual(0, game.round_index)
        self.assertEqual(PokerRound.PREFLOP, game.current_round)

    def test_start_with_one_player(self):
        game = Game(debug=True)
        game.add_player(1)
        game.start_game()
        self.assertEqual(0, game.round_index)
        self.assertEqual(PokerRound.PREFLOP, game.current_round)
        self.assertEqual(2, len(game.hands[1]))
        self.assertEqual(0, game.total_pot)
        self.assertEqual([], game.historical_pots)
        self.assertEqual({1: 0}, game.score)
        self.assertEqual({}, game.player_history)

    def test_start_with_mult_players(self):
        game = Game(debug=True)
        game.add_player(1)
        game.add_player(2)
        game.start_game()
        self.assertEqual(0, game.round_index)
        self.assertEqual(PokerRound.PREFLOP, game.current_round)
        self.assertEqual(2, len(game.hands[1]))
        self.assertEqual(2, len(game.hands[2]))
        self.assertEqual(0, game.total_pot)
        self.assertEqual([], game.historical_pots)
        self.assertEqual({1: 0, 2: 0}, game.score)
        self.assertEqual({}, game.player_history)

class TestUpdateGame(unittest.TestCase):
    def test_player_not_in_the_game(self):
        game = Game(debug=True)
        game.start_game()
        self.assertRaises(ValueError, game.update_game, 1, (PokerAction.CHECK, 0))

    def test_player_fold(self):
        game = Game(debug=True)
        game.add_player(1)
        game.add_player(2)
        game.start_game()
        game.update_game(1, (PokerAction.FOLD, 0))
        self.assertTrue(1 not in game.active_players)

    # def test_player_allin_twice(self):
    #     game = Game(debug=True)
    #     game.add_player(1)
    #     game.start_game()
    #     game.update_game(1, (PokerAction.ALL_IN, 100))
    #     game.end_round()
    #     game.start_round(1, (PokerAction))

class TestStartRound(unittest.TestCase):
    def test_invalid_start(self):
        game = Game(debug=True)
        game.add_player(1)
        game.start_game()
        self.assertRaises(InvalidStateErr, game.start_round())

    def test_start_flop(self):
        game = Game(debug=True)
        game.start_game()
        game.end_round()
        game.start_round()
        self.assertEqual(3, len(game.board))
        self.assertEqual(1, game.round_index)

    def test_start_turn(self):
        game = Game(debug=True)
        game.start_game()
        game.end_round()
        game.start_round()
        game.end_round()
        game.start_round()
        self.assertEqual(4, len(game.board))
        self.assertEqual(2, game.round_index)

    def test_start_river(self):
        game = Game(debug=True)
        game.start_game()
        game.end_round()
        game.start_round()
        game.end_round()
        game.start_round()
        game.end_round()
        game.start_round()
        self.assertEqual(5, len(game.board))
        self.assertEqual(3, game.round_index)

# class TestEndRound(unittest.TestCase):

# class TestEndGame(unittest.TestCase):
    # def


if __name__ == '__main__':
    unittest.main()
