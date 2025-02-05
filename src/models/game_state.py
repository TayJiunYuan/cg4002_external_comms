class Player:
    hp: int
    bullets: int
    bombs: int
    shield_hp: int
    deaths: int
    shields: int


class GameState:
    p1: Player
    p2: Player


class GameStatePrediction:
    player_id: int
    action: str
    game_state: GameState
