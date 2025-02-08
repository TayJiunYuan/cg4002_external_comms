"""
Run Relay Server (Sending) and Relay Server (Receiving) for testing on Ultra 96.
Command: 'python3 -m test.relay_servers.test_relay_servers' from project root.
"""

from multiprocessing import Queue, Process
from src.core.relay_server_receiver.relay_server_receiver_process import (
    relay_server_receiver_process,
)
from src.core.relay_server_sender.relay_server_sender_process import (
    relay_server_sender_process,
)


if __name__ == "__main__":

    relay_server_receiver_host_p1 = str(input("TEST - Host for Server Receiver: "))
    relay_server_receiver_port_p1 = int(input("TEST - Port for Server Receiver: "))

    relay_server_sender_host_p1 = str(input("TEST - Host for Server Receiver: "))
    relay_server_sender_port_p1 = int(input("TEST - Port for Server Receiver: "))

    from_relay_queue = Queue()
    to_relay_queue = Queue()

    relay_server_receiver_process_p1 = Process(
        target=relay_server_receiver_process,
        args=(
            relay_server_receiver_host_p1,
            relay_server_receiver_port_p1,
            1,
            from_relay_queue,
        ),
        daemon=True,
    )

    relay_server_sender_process_p1 = Process(
        target=relay_server_sender_process,
        args=(
            relay_server_sender_host_p1,
            relay_server_sender_port_p1,
            1,
            to_relay_queue,
        ),
        daemon=True,
    )

    relay_server_receiver_process_p1.start()
    relay_server_sender_process_p1.start()

    while True:
        print()
        user_input = input('TEST - Enter "a" to send dummy hp and bullets packet:\n')

        if user_input == "a":
            dummy_data = {"player_id": 1, "hp": 100, "bullets": 6}
            to_relay_queue.put(dummy_data)
