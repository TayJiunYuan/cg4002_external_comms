import queue
from multiprocessing import Queue

from src.core.game_engine.two_player_game_engine import TwoPlayerGameEngine
from src.models.sensor_packet import IMUPacket, ShootPacket, DisconnectPacket
from src.models.ai_packet import AIPacket
from src.utils.print_color import print_colored, COLORS


def two_player_game_engine_process(
    to_game_engine_queue: Queue,
    to_relay_queue_p1: Queue,
    to_relay_queue_p2: Queue,
    to_ai_queue: Queue,
    from_eval_queue: Queue,
    to_eval_queue: Queue,
    from_visualizer_queue: Queue,
    to_visualizer_queue: Queue,
):
    game_engine = TwoPlayerGameEngine(
        to_relay_queue_p1,
        to_relay_queue_p2,
        to_ai_queue,
        from_eval_queue,
        to_eval_queue,
        from_visualizer_queue,
        to_visualizer_queue,
    )
    while True:
        # Either IMU Packet, Shoot Packet or AI action
        packet: IMUPacket | ShootPacket | AIPacket | DisconnectPacket = (
            to_game_engine_queue.get()
        )

        # Disconnect Packet
        if packet["type"] == "dc":
            game_engine.on_disconnect_packet_received(packet=packet)
            game_engine.send_disconnect_to_relay(packet=packet)

        # IMU Packet
        elif packet["type"] == "imu":
            game_engine.on_imu_packet_received(packet=packet)
            game_engine.send_imu_packet_to_ai(packet=packet)

        # Shoot Packet
        elif packet["type"] == "shoot":
            player_id = game_engine.on_shoot_packet_received(packet=packet)

            # Get old Game State
            old_game_state = game_engine.get_game_state()

            # Check Visibility
            try:
                can_see, snow_bomb_count = game_engine.check_visibility(
                    player_id=player_id
                )
            except queue.Empty:
                print_colored(
                    "GAME ENGINE - Visualizer Timeout, skipping current packet",
                    COLORS["white"],
                )
                continue

            # Calculate Game State prediction
            predicted_game_state = game_engine.calculate_predicted_game_state(
                action="gun",
                player_id=player_id,
                can_see=can_see,
                snow_bomb_count=snow_bomb_count,
            )

            # Verify prediction with Eval Server
            try:
                correct_game_state = game_engine.verify_game_state_with_eval(
                    predicted_game_state=predicted_game_state
                )
            except queue.Empty:
                print_colored(
                    "GAME ENGINE - Eval Server Timeout",
                    COLORS["white"],
                )
                continue

            # Update Game State
            new_game_state = game_engine.update_game_state(
                correct_game_state=correct_game_state
            )

            # Send new game state to visualizer
            game_engine.send_updates_to_visualizer(
                action="gun",
                player_id=player_id,
                can_see=can_see,
                old_game_state=old_game_state,
                new_game_state=new_game_state,
            )

            # Send hp and bullets to relays
            game_engine.send_updates_to_relays(correct_game_state=correct_game_state)

        # AI packet
        else:
            player_id, action = game_engine.on_ai_packet_received(packet=packet)

            # Get old Game State
            old_game_state = game_engine.get_game_state()

            # Check Visibility
            try:
                can_see, snow_bomb_count = game_engine.check_visibility(
                    player_id=player_id
                )
            except queue.Empty:
                print_colored(
                    "GAME ENGINE - Visualizer Timeout, skipping current packet",
                    COLORS["white"],
                )
                continue

            # Calculate Game State prediction
            predicted_game_state = game_engine.calculate_predicted_game_state(
                action=action,
                player_id=player_id,
                can_see=can_see,
                snow_bomb_count=snow_bomb_count,
            )

            # Verify prediction with Eval Server
            try:
                correct_game_state = game_engine.verify_game_state_with_eval(
                    predicted_game_state=predicted_game_state
                )
            except queue.Empty:
                print_colored(
                    "GAME ENGINE - Eval Server Timeout",
                    COLORS["white"],
                )
                continue

            # Update Game State
            new_game_state = game_engine.update_game_state(
                correct_game_state=correct_game_state
            )

            # Send new game state to visualizer
            game_engine.send_updates_to_visualizer(
                action=action,
                player_id=player_id,
                can_see=can_see,
                old_game_state=old_game_state,
                new_game_state=new_game_state,
            )

            # Send hp and bullets to relays
            game_engine.send_updates_to_relays(correct_game_state=correct_game_state)