#!/usr/bin/env python3

import unittest
import json
import tempfile
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from game.game import Game

class TestPlayerMoneyLogging(unittest.TestCase):
    """Test cases for player money logging in game JSON"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.game = Game(debug=False)
        self.players = [1001, 1002, 1003]
        self.initial_money = 10000
        self.player_starting_money = {1001: 10000, 1002: 9500, 1003: 10500}
        self.player_delta = {1001: 0, 1002: -500, 1003: 500}
        
        # Add players to game
        for player_id in self.players:
            self.game.add_player(player_id)
    
    def test_player_money_info_logging(self):
        """Test that player money information is correctly logged"""
        # Set player money information
        self.game.set_player_money_info(
            self.player_starting_money,
            self.player_delta,
            self.initial_money
        )
        
        # Start game (this creates the JSON log structure)
        self.game.start_game()
        
        # Check that player money information is in the JSON log
        self.assertIn('playerMoney', self.game.json_game_log)
        player_money_section = self.game.json_game_log['playerMoney']
        
        # Check initial amount
        self.assertEqual(player_money_section['initialAmount'], self.initial_money)
        
        # Check starting money
        self.assertIn('startingMoney', player_money_section)
        for player_id, money in self.player_starting_money.items():
            self.assertEqual(int(player_money_section['startingMoney'][str(player_id)]), money)
        
        # Check starting delta
        self.assertIn('startingDelta', player_money_section)
        for player_id, delta in self.player_delta.items():
            self.assertEqual(int(player_money_section['startingDelta'][str(player_id)]), delta)
    
    def test_final_money_info_logging(self):
        """Test that final money information is correctly logged after game ends"""
        # Set initial money information
        self.game.set_player_money_info(
            self.player_starting_money,
            self.player_delta,
            self.initial_money
        )
        
        # Start game
        self.game.start_game()
        
        # Simulate game scores
        game_scores = {1001: 100, 1002: -200, 1003: 100}
        
        # Simulate final money after game
        final_money = {1001: 10100, 1002: 9300, 1003: 10600}
        final_delta = {1001: 100, 1002: -700, 1003: 600}
        
        # Update final money information
        self.game.update_final_money_after_game(game_scores, final_money, final_delta)
        
        # Manually set scores (normally done by game logic)
        self.game.score = game_scores
        
        # End game (this should add final money information)
        self.game.end_game()
        
        # Check final money information
        player_money_section = self.game.json_game_log['playerMoney']
        
        # Check final money
        self.assertIn('finalMoney', player_money_section)
        for player_id, money in final_money.items():
            self.assertEqual(int(player_money_section['finalMoney'][str(player_id)]), money)
        
        # Check final delta
        self.assertIn('finalDelta', player_money_section)
        for player_id, delta in final_delta.items():
            self.assertEqual(int(player_money_section['finalDelta'][str(player_id)]), delta)
        
        # Check game scores
        self.assertIn('gameScores', player_money_section)
        for player_id, score in game_scores.items():
            self.assertEqual(int(player_money_section['gameScores'][str(player_id)]), score)
        
        # Check this game delta
        self.assertIn('thisGameDelta', player_money_section)
        for player_id, score in game_scores.items():
            self.assertEqual(int(player_money_section['thisGameDelta'][str(player_id)]), score)
    
    def test_no_player_money_info(self):
        """Test that game still works without player money information"""
        # Start game without setting player money info
        self.game.start_game()
        
        # Should not have playerMoney section
        self.assertNotIn('playerMoney', self.game.json_game_log)
        
        # End game should still work
        self.game.score = {1001: 0, 1002: 0, 1003: 0}
        self.game.end_game()
        
        # Should have created playerMoney section with minimal info
        self.assertIn('playerMoney', self.game.json_game_log)
    
    def test_json_structure_completeness(self):
        """Test that the complete JSON structure is correct"""
        # Set player money information
        self.game.set_player_money_info(
            self.player_starting_money,
            self.player_delta,
            self.initial_money
        )
        
        # Start and end game with some scores
        self.game.start_game()
        game_scores = {1001: 50, 1002: -100, 1003: 50}
        final_money = {1001: 10050, 1002: 9400, 1003: 10550}
        final_delta = {1001: 50, 1002: -600, 1003: 550}
        
        self.game.update_final_money_after_game(game_scores, final_money, final_delta)
        self.game.score = game_scores
        self.game.end_game()
        
        # Check complete structure
        expected_keys = ['initialAmount', 'startingMoney', 'startingDelta', 'finalMoney', 'finalDelta', 'gameScores', 'thisGameDelta']
        player_money_section = self.game.json_game_log['playerMoney']
        
        for key in expected_keys:
            self.assertIn(key, player_money_section, f"Missing key: {key}")
        
        # Verify JSON is serializable
        json_str = json.dumps(self.game.json_game_log, indent=2)
        self.assertIsInstance(json_str, str)
        
        # Verify JSON can be parsed back
        parsed_json = json.loads(json_str)
        self.assertEqual(parsed_json['playerMoney']['initialAmount'], self.initial_money)

if __name__ == '__main__':
    unittest.main(verbosity=2) 