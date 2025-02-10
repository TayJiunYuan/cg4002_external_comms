import queue
from multiprocessing import Queue

from src.core.game_engine.one_player_game_engine import OnePlayerGameEngine
from src.models.sensor_packet import IMUPacket, ShootPacket
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
    game_engine = OnePlayerGameEngine(
        to_relay_queue_p1,
        to_relay_queue_p2,
        to_ai_queue,
        from_eval_queue,
        to_eval_queue,
        from_visualizer_queue,
        to_visualizer_queue,
    )
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
                can_see = game_engine.check_visibility(player_id=player_id)

                # Calculate Game State prediction
                predicted_game_state = game_engine.calculate_predicted_game_state(
                    action="gun", player_id=player_id, can_see=can_see
                )

                # Verify prediction with Eval Server
                correct_game_state = game_engine.verify_game_state_with_eval(
                    predicted_game_state=predicted_game_state
                )

                # Update Game State
                game_engine.update_game_state(correct_game_state=correct_game_state)

                # Send new game state to visualizer
                game_engine.send_updates_to_visualizer(
                    action="gun",
                    player_id=player_id,
                    correct_game_state=correct_game_state,
                )

                # Send hp and bullets to relays
                game_engine.send_updates_to_relays(
                    correct_game_state=correct_game_state
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
                can_see = game_engine.check_visibility(player_id=player_id)

                # Calculate Game State prediction
                predicted_game_state = game_engine.calculate_predicted_game_state(
                    action=action, player_id=player_id, can_see=can_see
                )

                # Verify prediction with Eval Server
                correct_game_state = game_engine.verify_game_state_with_eval(
                    predicted_game_state=predicted_game_state
                )

                # Update Game State
                game_engine.update_game_state(correct_game_state=correct_game_state)

                # Send new game state to visualizer
                game_engine.send_updates_to_visualizer(
                    action=action,
                    player_id=player_id,
                    correct_game_state=correct_game_state,
                )

                # Send hp and bullets to relays
                game_engine.send_updates_to_relays(
                    correct_game_state=correct_game_state
                )
            except queue.Empty:
                pass
