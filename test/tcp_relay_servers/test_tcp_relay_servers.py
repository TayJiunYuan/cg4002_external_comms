"""
Run TCP Servers (Receiver and Sender) for testing on Ultra 96.
Command: 'python3 -m test.tcp_relay_servers.test_tcp_relay_servers' from project root.
"""

import multiprocessing
from src.core.tcp_server_sender.tcp_server_sender_process import (
    tcp_server_sender_process,
)
from src.core.tcp_server_receiver.tcp_server_receiver_process import (
    tcp_server_receiver_process,
)


if __name__ == "__main__":
    from_beetle_queue = multiprocessing.Queue()
    to_beetle_queue = multiprocessing.Queue()

    tcp_server_sender_process = multiprocessing.Process(
        target=tcp_server_sender_process,
        args=(
            "127.0.0.1",
            8000,
            to_beetle_queue,
        ),
        daemon=True,
    )

    tcp_server_receiver_process = multiprocessing.Process(
        target=tcp_server_receiver_process,
        args=(
            "127.0.0.1",
            8001,
            from_beetle_queue,
        ),
        daemon=True,
    )

    tcp_server_sender_process.start()
    tcp_server_receiver_process.start()
    
    while True:
        user_input = input('Enter "a" to send dummy hp and bullets packet: ')

        if user_input == "a":
            dummy_data = {"player_id": 1, "hp": 100, "bullets": 6}
            to_beetle_queue.put(dummy_data)
