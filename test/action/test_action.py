"""
Test each possible action (including AI action) through relay_client
Command: 'python3 -m test.action.test_action'.
Run after starting 1 player game 
"""

from src.core.relay_client_sender.relay_client_sender_process import (
    relay_client_sender_process,
)
from src.core.relay_client_receiver.relay_client_receiver_process import (
    relay_client_receiver_process,
)
from multiprocessing import Queue, Process
from datetime import datetime

dummy_imu_packet = {
    "type": "imu",
    "player_id": 1,
    "data": {
        "position": "glove",
        "accelerometer": {"x": 10, "y": 10, "z": 10},
        "gyroscope": {"yaw": 10, "pitch": 10, "roll": 10},
    },
    "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.")
    + f"{datetime.utcnow().microsecond:06d}"
    + "Z",
}

dummy_shoot_packet = {
    "type": "shoot",
    "player_id": 1,
    "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.")
    + f"{datetime.utcnow().microsecond:06d}"
    + "Z",
}

dummy_shield_packet = {"type": "ai", "player_id": 1, "action": "shield"}

dummy_bomb_packet = {"type": "ai", "player_id": 1, "action": "bomb"}

dummy_reload_packet = {"type": "ai", "player_id": 1, "action": "reload"}

dummy_badminton_packet = {"type": "ai", "player_id": 1, "action": "badminton"}

dummy_golf_packet = {"type": "ai", "player_id": 1, "action": "golf"}

dummy_fencing_packet = {"type": "ai", "player_id": 1, "action": "fencing"}

dummy_boxing_packet = {"type": "ai", "player_id": 1, "action": "boxing"}

dummy_logout_packet = {"type": "ai", "player_id": 1, "action": "logout"}


if __name__ == "__main__":
    relay_server_receiver_host_p1 = str(
        input("TEST - IP Address for Server Receiver: ")
    )
    relay_server_receiver_port_p1 = int(input("TEST - Port for Server Receiver: "))

    relay_server_sender_host_p1 = str(input("TEST - IP Address for Server Receiver: "))
    relay_server_sender_port_p1 = int(input("TEST - Port for Server Receiver: "))

    from_u96_queue = Queue()
    to_u96_queue = Queue()

    relay_client_sender_process_p1 = Process(
        target=relay_client_sender_process,
        args=(
            relay_server_receiver_host_p1,
            relay_server_receiver_port_p1,
            1,
            to_u96_queue,
        ),
        daemon=True,
    )

    relay_client_receiver_process_p1 = Process(
        target=relay_client_receiver_process,
        args=(
            relay_server_sender_host_p1,
            relay_server_sender_port_p1,
            1,
            from_u96_queue,
        ),
        daemon=True,
    )

    relay_client_sender_process_p1.start()
    relay_client_receiver_process_p1.start()

    while True:
        print()
        user_input = input(
            'TEST - Enter i - IMU, s - shoot, sh - shield, bo - bomb, re - reload, ba - badminton, go - golf, fe - fencing, box - boxing, lo - logout: \n'
        )
        if user_input == "i":
            to_u96_queue.put(dummy_imu_packet)
        if user_input == "s":
            to_u96_queue.put(dummy_shoot_packet)
        if user_input == "sh":
            to_u96_queue.put(dummy_shield_packet)
        if user_input == "bo":
            to_u96_queue.put(dummy_bomb_packet)
        if user_input == "re":
            to_u96_queue.put(dummy_reload_packet)
        if user_input == "ba":
            to_u96_queue.put(dummy_badminton_packet)
        if user_input == "go":
            to_u96_queue.put(dummy_golf_packet)
        if user_input == "fe":
            to_u96_queue.put(dummy_fencing_packet)
        if user_input == "box":
            to_u96_queue.put(dummy_boxing_packet)
        if user_input == "lo":
            to_u96_queue.put(dummy_logout_packet)
