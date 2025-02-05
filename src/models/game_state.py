class Player:
    hp: int
    bullets: int
    bombs: int
    shield_hp: int
    deaths: int
    shields: int


class GameState:
    """Game State class for data received from evaluation server."""

    p1: Player
    p2: Player


class GameStatePrediction:
    """Game State Prediction class for data sent to evaluation server."""

    player_id: int
    action: str
    game_state: GameState


class HPAndBulletsState:
    """State class to send to beetle to keep hp and bullets state."""

    player_id: int
    hp: int
    bullets: int
