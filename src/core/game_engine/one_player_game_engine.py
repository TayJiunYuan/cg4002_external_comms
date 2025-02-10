import uuid
from multiprocessing import Queue
from src.core.game_engine.game_state_engine import GameStateEngine
from src.models.game_state import GameState, GameStatePrediction, HPAndBulletsState
from src.models.sensor_packet import IMUPacket, ShootPacket
from src.models.visualizer_packet import (
    VisibilityRequestPacket,
    VisibilityResponsePacket,
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

    def update_game_state(self, correct_game_state: GameState) -> None:
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

    def send_updates_to_visualizer(
        self, action: str, player_id: int, correct_game_state: GameState
    ) -> None:
        visualizer_action_packet = {
            "action": action,
            "player_id": player_id,
            "game_state": correct_game_state,
        }  # TODO: Implement hp calculation to Send ActionPacket class instead (cfm action packet with Visualizer)
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
