import uuid
from multiprocessing import Queue
from src.core.game_engine.game_state_engine import GameStateEngine
from src.models.game_state import GameState, GameStatePrediction, HPAndBulletsState
from src.models.visualizer_packet import (
    VisibilityRequestPacket,
    VisibilityResponsePacket,
    VisualizerActionPacket,
)
from src.utils.print_color import print_colored, COLORS


class OnePlayerGameEngine:
    def __init__(
        self,
        to_relay_queue_p1: Queue,
        to_relay_queue_p2: Queue,
        to_ai_queue: Queue,
        from_eval_queue: Queue,
        to_eval_queue: Queue,
        from_visualizer_queue: Queue,
        to_visualizer_queue: Queue,
    ):
        self.to_relay_queue_p1 = to_relay_queue_p1
        self.to_relay_queue_p2 = to_relay_queue_p2
        self.to_ai_queue = to_ai_queue
        self.from_eval_queue = from_eval_queue
        self.to_eval_queue = to_eval_queue
        self.from_visualizer_queue = from_visualizer_queue
        self.to_visualizer_queue = to_visualizer_queue
        self.game_state_engine = GameStateEngine()

    def check_visibility(self, player_id: int) -> bool:
        visibility_request: VisibilityRequestPacket = {
            "request_id": str(uuid.uuid4()),
            "player_id": player_id,
        }
        self.to_visualizer_queue.put(visibility_request)
        print_colored(
            f"GAME ENGINE - Sent Visibility Request: {visibility_request}",
            COLORS["white"],
        )

        visibility_response: VisibilityResponsePacket = (
            self.from_visualizer_queue.get()
        )  # TODO: this is blocking, find alternative
        print_colored(
            f"GAME ENGINE - Received Visibility Request{visibility_response}",
            COLORS["white"],
        )
        return visibility_response["is_opponent_visible"]

    def calculate_predicted_game_state(
        self, action: str, player_id: int, can_see: bool
    ) -> GameStatePrediction:
        self.game_state_engine.perform_action(
            action=action, player_id=player_id, can_see=can_see
        )
        predicted_game_state: GameStatePrediction = {
            "player_id": player_id,
            "action": action,
            "game_state": self.game_state_engine.get_dict(),
        }
        return predicted_game_state

    def verify_game_state_with_eval(
        self, predicted_game_state: GameStatePrediction
    ) -> GameState:
        self.to_eval_queue.put(predicted_game_state)
        print_colored(
            f"GAME ENGINE - Send prediction to evaluation server: {predicted_game_state['game_state']}",
            COLORS["white"],
        )
        correct_game_state: GameState = (
            self.from_eval_queue.get()
        )  # TODO: this is blocking, find alternative
        print(
            f"GAME ENGINE - Received correct game state from evaluation server: {correct_game_state}"
        )
        return correct_game_state

    def get_game_state(self) -> GameState:
        game_state = self.game_state_engine.get_dict()
        return game_state

    def update_game_state(self, correct_game_state: GameState) -> GameState:
        self.game_state_engine.player_1.set_state(
            hp=correct_game_state["p1"]["hp"],
            bullets_remaining=correct_game_state["p1"]["bullets"],
            bombs_remaining=correct_game_state["p1"]["bombs"],
            shield_health=correct_game_state["p1"]["shield_hp"],
            num_deaths=correct_game_state["p1"]["deaths"],
            num_unused_shield=correct_game_state["p1"]["shields"],
        )

        self.game_state_engine.player_2.set_state(
            hp=correct_game_state["p2"]["hp"],
            bullets_remaining=correct_game_state["p2"]["bullets"],
            bombs_remaining=correct_game_state["p2"]["bombs"],
            shield_health=correct_game_state["p2"]["shield_hp"],
            num_deaths=correct_game_state["p2"]["deaths"],
            num_unused_shield=correct_game_state["p2"]["shields"],
        )
        game_state = self.get_game_state()
        return game_state

    def send_updates_to_visualizer(
        self, action, player_id, can_see, old_game_state, new_game_state
    ) -> None:
        action_successful = False
        opponent_hp_hit = 0
        if action in ["shield, reload, logout"]:  # non-damaging action
            action_successful = True
            opponent_hp_hit = 0
        else:  # damaging action (gun, bomb, badminton, golf, fencing, boxing)
            action_successful = can_see
            opponent_id = 2 if player_id == 1 else 1
            opponent_hp_hit = (
                old_game_state[f"p{opponent_id}"]["hp"]
                - new_game_state[f"p{opponent_id}"]["hp"]
            )
        visualizer_action_packet: VisualizerActionPacket = {
            "action": action,
            "action_successful": action_successful,
            "player_id": player_id,
            "opponent_hp_hit": opponent_hp_hit,
        }
        self.to_visualizer_queue.put(visualizer_action_packet)
        print_colored(
            f"GAME ENGINE - Sent correct game state to Visualizer: {visualizer_action_packet}",
            COLORS["white"],
        )

    def send_updates_to_relays(self, correct_game_state: GameState) -> None:
        hp_and_bullets_p1: HPAndBulletsState = {
            "player_id": 1,
            "hp": correct_game_state["p1"]["hp"],
            "bullets": correct_game_state["p1"]["bullets"],
        }
        self.to_relay_queue_p1.put(hp_and_bullets_p1)
        print_colored(
            f"GAME ENGINE - Sent HP and Bullets to relay P1: {hp_and_bullets_p1}",
            COLORS["white"],
        )

        hp_and_bullets_p2: HPAndBulletsState = {
            "player_id": 2,
            "hp": correct_game_state["p2"]["hp"],
            "bullets": correct_game_state["p2"]["bullets"],
        }
        self.to_relay_queue_p2.put(hp_and_bullets_p2)
        print_colored(
            f"GAME ENGINE - Sent HP and Bullets to relay P2 {hp_and_bullets_p2}",
            COLORS["white"],
        )
