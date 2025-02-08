class ActionPacket:
    action: str
    player_id: int
    opponent_hp_hit: int
    opponent_died: bool


class VisibilityRequestPacket:
    request_id: str
    player_id: int


class VisibilityResponsePacket:
    request_id: str
    player_id: int
    is_opponent_visible: bool
