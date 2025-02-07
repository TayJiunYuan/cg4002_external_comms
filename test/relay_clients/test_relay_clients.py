""" 
Run Relay Client (Sending) and Relay Client (Receiving) on Laptop with dummy data for testing.
Command: 'python3 -m test.relay_clients.test_relay_clients' from project root.
Run after starting Relay Servers on Ultra96.
"""

import sys
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
            'Enter "i" to send dummy IMU data or "s" to send dummy shoot data: \n'
        )
        if user_input == "i":
            to_u96_queue.put(dummy_imu_packet)
        if user_input == "s":
            to_u96_queue.put(dummy_shoot_packet)
