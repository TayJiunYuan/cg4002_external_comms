"""
Runs the dummy ai service and tests if the buffers are working correctly
Command: 'python3 -m test.ai.test_ai_buffer' from project root.
"""

from src.core.ai_service.dummy_ai_service_process import dummy_ai_service_process

from multiprocessing import Queue, Process


if __name__ == "__main__":

    to_ai_queue = Queue()
    from_ai_queue = Queue()

    ai_service_process = Process(
        target=dummy_ai_service_process,
        args=(to_ai_queue, from_ai_queue),
        daemon=True,
    )
    ai_service_process.start()
    while True:
        print()
        user_input = input("TEST - Enter player_id followed by timestamp and ENTER:\n")
        player_id, timestamp = user_input.split(" ")
        player_id = int(player_id)
        timestamp = int(timestamp)
        to_ai_queue.put(
            {
                "type": "imu",
                "player_id": player_id,
                "data": {
                    "aX_g": 0,
                    "aY_g": 0,
                    "aZ_g": 0,
                    "gX_g": 0,
                    "gY_g": 0,
                    "gZ_g": 0,
                    "aX_v": 0,
                    "aY_v": 0,
                    "aZ_v": 0,
                    "gX_v": 0,
                    "gY_v": 0,
                    "gZ_v": 0,
                    "timestamp": timestamp,
                },
            }
        )
