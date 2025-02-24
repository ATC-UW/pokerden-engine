import json
from poker_types import MessageType


class Message:
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message
    
class START(Message):
    def __init__(self, message):
        self.message = message
        self.type = MessageType.GAME_START

    def __str__(self, message):
        return json.dumps({"type": self.type, "message": self.message})
    
    @staticmethod
    def parse(message_str):
        data = json.loads(message_str)
        if data["type"] == MessageType.GAME_START:
            return START(data["message"])
        return Message(data["message"])
    
class GAME_STATE(Message):
    def __init__(self, round_num, community_cards, players, pot, current_player, current_bet, min_raise, max_raise):
        self.message = {
            "round_num": round_num,
            "community_cards": community_cards,
            "players": players,
            "pot": pot,
            "current_player": current_player,
            "current_bet": current_bet,
            "min_raise": min_raise,
            "max_raise": max_raise
        }
        self.type = MessageType.GAME_STATE

    def __str__(self):
        return json.dumps({"type": self.type, "message": self.message})
    
    @staticmethod
    def parse(message_str):
        data = json.loads(message_str)
        if data["type"] == MessageType.GAME_STATE:
            return GAME_STATE(data["round_num"], data["community_cards"], data["players"], data["pot"], data["current_player"], data["current_bet"], data["min_raise"], data["max_raise"])
        raise ValueError("Invalid message type")
    
class REQUEST_PLAYER_MESSAGE(Message):
    def __init__(self, player_id, time_left):
        self.message = {
            "player_id": player_id,
            "time_left": time_left
        }
        self.type = MessageType.REQUEST_PLAYER_ACTION

    def __str__(self):
        return json.dumps({"type": self.type, "message": self.message})
    
    @staticmethod
    def parse(message_str):
        data = json.loads(message_str)
        if data["type"] == MessageType.REQUEST_PLAYER_ACTION:
            return REQUEST_PLAYER_MESSAGE(data["player_id"], data["time_left"])
        raise ValueError("Invalid message type")