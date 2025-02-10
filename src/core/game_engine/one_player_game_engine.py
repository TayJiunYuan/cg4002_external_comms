import queue
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


def one_player_game_engine_process(
    from_relay_queue_p1: Queue,
    to_relay_queue_p1: Queue,
    from_relay_queue_p2: Queue,
    to_relay_queue_p2: Queue,
    from_ai_queue: Queue,
    to_ai_queue: Queue,
    from_eval_queue: Queue,
    to_eval_queue: Queue,
    from_visualizer_queue: Queue,
    to_visualizer_queue: Queue,
):
    game_state_engine = GameStateEngine()
    while True:
        try:
            packet: IMUPacket | ShootPacket = from_relay_queue_p1.get_nowait()

            # Case 1: IMU Packet from P1
            if packet["type"] == "imu":
                print_colored(
                    f"GAME ENGINE - Received IMU packet from P1: {packet}",
                    COLORS["white"],
                )
                to_ai_queue.put(packet)
                print_colored(
                    f"GAME ENGINE - Sent IMU packet to AI: {packet}", COLORS["white"]
                )

            # Case 2: Shoot Packet from P1
            elif packet["type"] == "shoot":
                print_colored(
                    f"GAME ENGINE - Received shoot packet from P1: {packet}",
                    COLORS["white"],
                )
                player_id = packet["player_id"]

                # Check Visibility
                visibility_request: VisibilityRequestPacket = {
                    "request_id": str(uuid.uuid4()),
                    "player_id": player_id,
                }
                to_visualizer_queue.put(visibility_request)
                print_colored(
                    f"GAME ENGINE - Sent Visibility Request: {visibility_request}",
                    COLORS["white"],
                )
                visibility_response: VisibilityResponsePacket = (
                    from_visualizer_queue.get()  # TODO: this is blocking, find alternative
                )
                print_colored(
                    f"GAME ENGINE - Received Visibility Request{visibility_response}",
                    COLORS["white"],
                )
                can_see = visibility_response["is_opponent_visible"]

                # Calculate Game State prediction
                game_state_engine.perform_action(
                    action="gun", player_id=player_id, can_see=can_see
                )
                predicted_game_state: GameStatePrediction = {
                    "player_id": player_id,
                    "action": "gun",
                    "game_state": game_state_engine.get_dict(),
                }

                # Verify prediction with Eval Server
                to_eval_queue.put(predicted_game_state)
                print_colored(
                    f"GAME ENGINE - Send prediction to evaluation server: {predicted_game_state['game_state']}",
                    COLORS["white"],
                )
                correct_game_state: GameState = (
                    from_eval_queue.get()
                )  # TODO: this is blocking, find alternative
                print(
                    f"GAME ENGINE - Received correct game state from evaluation server: {correct_game_state}"
                )

                game_state_engine.player_1.set_state(
                    hp=correct_game_state["p1"]["hp"],
                    bullets_remaining=correct_game_state["p1"]["bullets"],
                    bombs_remaining=correct_game_state["p1"]["bombs"],
                    shield_health=correct_game_state["p1"]["shield_hp"],
                    num_deaths=correct_game_state["p1"]["deaths"],
                    num_unused_shield=correct_game_state["p1"]["shields"],
                )

                game_state_engine.player_2.set_state(
                    hp=correct_game_state["p2"]["hp"],
                    bullets_remaining=correct_game_state["p2"]["bullets"],
                    bombs_remaining=correct_game_state["p2"]["bombs"],
                    shield_health=correct_game_state["p2"]["shield_hp"],
                    num_deaths=correct_game_state["p2"]["deaths"],
                    num_unused_shield=correct_game_state["p2"]["shields"],
                )

                # Send new game state to visualizer
                visualizer_action_packet = {
                    "action": "gun",
                    "player_id": player_id,
                    "game_state": correct_game_state,
                }  # TODO: Implement hp calculation to Send ActionPacket class instead (cfm action packet with Visualizer)
                to_visualizer_queue.put(visualizer_action_packet)
                print_colored(
                    f"GAME ENGINE - Sent correct game state to Visualizer: {visualizer_action_packet}",
                    COLORS["white"],
                )

                # Send hp and bullets to relays
                hp_and_bullets_p1: HPAndBulletsState = {
                    "player_id": 1,
                    "hp": correct_game_state["p1"]["hp"],
                    "bullets": correct_game_state["p1"]["bullets"],
                }
                to_relay_queue_p1.put(hp_and_bullets_p1)
                print_colored(
                    f"GAME ENGINE - Sent HP and Bullets to relay P1: {hp_and_bullets_p1}",
                    COLORS["white"],
                )

                hp_and_bullets_p2: HPAndBulletsState = {
                    "player_id": 2,
                    "hp": correct_game_state["p2"]["hp"],
                    "bullets": correct_game_state["p2"]["bullets"],
                }
                to_relay_queue_p2.put(hp_and_bullets_p2)
                print_colored(
                    f"GAME ENGINE - Sent HP and Bullets to relay P2 {hp_and_bullets_p2}",
                    COLORS["white"],
                )

        except (
            queue.Empty
        ):  # no packet in from relay queue, check from_ai_queue for ai action
            # Case 3: Receive AI Action
            try:
                action_packet = from_ai_queue.get_nowait()
                print_colored(
                    f"GAME ENGINE - Received AI action: {action_packet}",
                    COLORS["white"],
                )
                action = action_packet["action"]
                player_id = action_packet["player_id"]
                # Check Visibility
                visibility_request: VisibilityRequestPacket = {
                    "request_id": str(uuid.uuid4()),
                    "player_id": player_id,
                }
                to_visualizer_queue.put(visibility_request)
                print_colored(
                    f"GAME ENGINE - Sent Visibility Request: {visibility_request}",
                    COLORS["white"],
                )
                visibility_response: VisibilityResponsePacket = (
                    from_visualizer_queue.get()  # TODO: this is blocking, find alternative
                )
                print_colored(
                    f"GAME ENGINE - Received Visibility Request{visibility_response}",
                    COLORS["white"],
                )
                can_see = visibility_response["is_opponent_visible"]

                # Calculate Game State prediction
                game_state_engine.perform_action(
                    action=action, player_id=player_id, can_see=can_see
                )
                predicted_game_state: GameStatePrediction = {
                    "player_id": player_id,
                    "action": action,
                    "game_state": game_state_engine.get_dict(),
                }

                # Verify prediction with Eval Server
                to_eval_queue.put(predicted_game_state)
                print_colored(
                    f"GAME ENGINE - Send prediction to evaluation server: {predicted_game_state['game_state']}",
                    COLORS["white"],
                )
                correct_game_state: GameState = (
                    from_eval_queue.get()
                )  # TODO: this is blocking, find alternative
                print(
                    f"GAME ENGINE - Received correct game state from evaluation server: {correct_game_state}"
                )

                game_state_engine.player_1.set_state(
                    hp=correct_game_state["p1"]["hp"],
                    bullets_remaining=correct_game_state["p1"]["bullets"],
                    bombs_remaining=correct_game_state["p1"]["bombs"],
                    shield_health=correct_game_state["p1"]["shield_hp"],
                    num_deaths=correct_game_state["p1"]["deaths"],
                    num_unused_shield=correct_game_state["p1"]["shields"],
                )

                game_state_engine.player_2.set_state(
                    hp=correct_game_state["p2"]["hp"],
                    bullets_remaining=correct_game_state["p2"]["bullets"],
                    bombs_remaining=correct_game_state["p2"]["bombs"],
                    shield_health=correct_game_state["p2"]["shield_hp"],
                    num_deaths=correct_game_state["p2"]["deaths"],
                    num_unused_shield=correct_game_state["p2"]["shields"],
                )

                # Send new game state to visualizer
                visualizer_action_packet = {
                    "action": action,
                    "player_id": player_id,
                    "game_state": correct_game_state,
                }  # TODO: Implement hp calculation to Send ActionPacket class instead (cfm action packet with Visualizer)
                to_visualizer_queue.put(visualizer_action_packet)
                print_colored(
                    f"GAME ENGINE - Sent correct game state to Visualizer: {visualizer_action_packet}",
                    COLORS["white"],
                )

                # Send hp and bullets to relays
                hp_and_bullets_p1: HPAndBulletsState = {
                    "player_id": 1,
                    "hp": correct_game_state["p1"]["hp"],
                    "bullets": correct_game_state["p1"]["bullets"],
                }
                to_relay_queue_p1.put(hp_and_bullets_p1)
                print_colored(
                    f"GAME ENGINE - Sent HP and Bullets to relay P1: {hp_and_bullets_p1}",
                    COLORS["white"],
                )

                hp_and_bullets_p2: HPAndBulletsState = {
                    "player_id": 2,
                    "hp": correct_game_state["p2"]["hp"],
                    "bullets": correct_game_state["p2"]["bullets"],
                }
                to_relay_queue_p2.put(hp_and_bullets_p2)
                print_colored(
                    f"GAME ENGINE - Sent HP and Bullets to relay P2 {hp_and_bullets_p2}",
                    COLORS["white"],
                )
            except queue.Empty:
                pass
