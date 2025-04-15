"""
Run Relay Client (Sending) and Relay Client (Receiving) on Laptop with dummy data for testing.
Command: 'python3 -m test.relay_clients.test_relay_clients' from project root.
Run after starting Relay Servers on Ultra96.
"""

from src.core.relay_client_sender.relay_client_sender_thread import (
    relay_client_sender_thread,
)
from src.core.relay_client_receiver.relay_client_receiver_thread import (
    relay_client_receiver_thread,
)
from queue import Queue
import threading

stop_event = threading.Event()

if __name__ == "__main__":
    player_id = int(input("TEST - Player ID: ") or 1)

    relay_server_receiver_host = str(
        input("TEST - IP Address for Server Receiver: ") or "127.0.0.1"
    )
    relay_server_receiver_port = int(input("TEST - Port for Server Receiver: ") or 8002)

    relay_server_sender_host = str(
        input("TEST - IP Address for Server Receiver: ") or "127.0.0.1"
    )
    relay_server_sender_port = int(input("TEST - Port for Server Receiver: ") or 8003)

    from_u96_queue = Queue()
    to_u96_queue = Queue()

    relay_client_sender_thread = threading.Thread(
        target=relay_client_sender_thread,
        args=(
            relay_server_receiver_host,
            relay_server_receiver_port,
            player_id,
            to_u96_queue,
            stop_event,
        ),
    )

    relay_client_receiver_thread = threading.Thread(
        target=relay_client_receiver_thread,
        args=(
            relay_server_sender_host,
            relay_server_sender_port,
            player_id,
            from_u96_queue,
            stop_event,
        ),
    )

    relay_client_sender_thread.start()
    relay_client_receiver_thread.start()

    try:
        while True:
            print()
            user_input = input(
                'TEST - Enter "i" to send 15 dummy IMU packets or "s" to send dummy shoot data: \n'
            )
            # snowball
            if user_input[0] == "i":
                to_u96_queue.put(
                    {
                        "type": "imu",
                        "player_id": player_id,
                        "data": {
                            "gX_g": -4135,
                            "gY_g": -3544,
                            "gZ_g": -3544,
                            "aX_g": 247,
                            "aY_g": 115,
                            "aZ_g": 787,
                            "timestamp": 1,
                        },
                    }
                )
                to_u96_queue.put(
                    {
                        "type": "imu",
                        "player_id": player_id,
                        "data": {
                            "gX_g": -3235,
                            "gY_g": -17952,
                            "gZ_g": -2476,
                            "aX_g": 1826,
                            "aY_g": 195,
                            "aZ_g": 2293,
                            "timestamp": 2,
                        },
                    }
                )

                to_u96_queue.put(
                    {
                        "type": "imu",
                        "player_id": player_id,
                        "data": {
                            "gX_g": 1413,
                            "gY_g": -12000,
                            "gZ_g": -7073,
                            "aX_g": 4263,
                            "aY_g": 1505,
                            "aZ_g": 2945,
                            "timestamp": 3,
                        },
                    }
                )

                to_u96_queue.put(
                    {
                        "type": "imu",
                        "player_id": player_id,
                        "data": {
                            "gX_g": 1303,
                            "gY_g": -11713,
                            "gZ_g": -8543,
                            "aX_g": 4459,
                            "aY_g": 1820,
                            "aZ_g": 2497,
                            "timestamp": 4,
                        },
                    }
                )

                to_u96_queue.put(
                    {
                        "type": "imu",
                        "player_id": player_id,
                        "data": {
                            "gX_g": 1222,
                            "gY_g": -5895,
                            "gZ_g": -8318,
                            "aX_g": 3081,
                            "aY_g": 1861,
                            "aZ_g": 1484,
                            "timestamp": 5,
                        },
                    }
                )

                to_u96_queue.put(
                    {
                        "type": "imu",
                        "player_id": player_id,
                        "data": {
                            "gX_g": -731,
                            "gY_g": -9845,
                            "gZ_g": -7547,
                            "aX_g": 2224,
                            "aY_g": 3586,
                            "aZ_g": -1919,
                            "timestamp": 6,
                        },
                    }
                )

                to_u96_queue.put(
                    {
                        "type": "imu",
                        "player_id": player_id,
                        "data": {
                            "gX_g": -2167,
                            "gY_g": -15505,
                            "gZ_g": -8007,
                            "aX_g": 3266,
                            "aY_g": 5357,
                            "aZ_g": -1935,
                            "timestamp": 7,
                        },
                    }
                )

                to_u96_queue.put(
                    {
                        "type": "imu",
                        "player_id": player_id,
                        "data": {
                            "gX_g": -7564,
                            "gY_g": -10262,
                            "gZ_g": -6657,
                            "aX_g": 3315,
                            "aY_g": 3792,
                            "aZ_g": 3144,
                            "timestamp": 8,
                        },
                    }
                )

                to_u96_queue.put(
                    {
                        "type": "imu",
                        "player_id": player_id,
                        "data": {
                            "gX_g": -10542,
                            "gY_g": -8509,
                            "gZ_g": -5493,
                            "aX_g": 2547,
                            "aY_g": 3031,
                            "aZ_g": 3888,
                            "timestamp": 9,
                        },
                    }
                )

                to_u96_queue.put(
                    {
                        "type": "imu",
                        "player_id": player_id,
                        "data": {
                            "gX_g": -12984,
                            "gY_g": -7925,
                            "gZ_g": -5311,
                            "aX_g": 2187,
                            "aY_g": 2048,
                            "aZ_g": 4478,
                            "timestamp": 10,
                        },
                    }
                )

                to_u96_queue.put(
                    {
                        "type": "imu",
                        "player_id": player_id,
                        "data": {
                            "gX_g": -12855,
                            "gY_g": -7676,
                            "gZ_g": -12709,
                            "aX_g": -1785,
                            "aY_g": 5662,
                            "aZ_g": 1639,
                            "timestamp": 11,
                        },
                    }
                )

                to_u96_queue.put(
                    {
                        "type": "imu",
                        "player_id": player_id,
                        "data": {
                            "gX_g": -10106,
                            "gY_g": -9558,
                            "gZ_g": -11086,
                            "aX_g": -2625,
                            "aY_g": 5616,
                            "aZ_g": 292,
                            "timestamp": 12,
                        },
                    }
                )

                to_u96_queue.put(
                    {
                        "type": "imu",
                        "player_id": player_id,
                        "data": {
                            "gX_g": -7209,
                            "gY_g": -10377,
                            "gZ_g": -9070,
                            "aX_g": -3052,
                            "aY_g": 4961,
                            "aZ_g": -1129,
                            "timestamp": 13,
                        },
                    }
                )

                to_u96_queue.put(
                    {
                        "type": "imu",
                        "player_id": player_id,
                        "data": {
                            "gX_g": -6113,
                            "gY_g": -17588,
                            "gZ_g": -5282,
                            "aX_g": -5660,
                            "aY_g": 3792,
                            "aZ_g": -3378,
                            "timestamp": 14,
                        },
                    }
                )

                to_u96_queue.put(
                    {
                        "type": "imu",
                        "player_id": player_id,
                        "data": {
                            "gX_g": -1262,
                            "gY_g": 29651,
                            "gZ_g": -11134,
                            "aX_g": -8796,
                            "aY_g": -3501,
                            "aZ_g": -3905,
                            "timestamp": 15,
                        },
                    }
                )

            if user_input == "s":
                to_u96_queue.put({"type": "shoot", "player_id": player_id})
    except KeyboardInterrupt:
        stop_event.set()
        relay_client_sender_thread.join()
        relay_client_receiver_thread.join()
        print("TEST - Threads ended gracefully")
