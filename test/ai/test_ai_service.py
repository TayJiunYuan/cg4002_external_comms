"""
Runs the ai service and fills up buffer to test if it is running correctly with prediction. Run on U96 only.
Command: 'sudo -E python3 -m test.ai.test_ai_service' from project root.
"""

from src.core.ai_service.ai_service_process import ai_service_process

from multiprocessing import Queue, Process


if __name__ == "__main__":

    to_ai_queue = Queue()
    from_ai_queue = Queue()

    ai_process = Process(
        target=ai_service_process,
        args=(to_ai_queue, from_ai_queue),
        daemon=True,
    )
    ai_process.start()
    while True:
        print()
        user_input = input("Press a to send 15 packets:\n")
        if user_input == "a":
            for i in range(0, 15):
                to_ai_queue.put(
                    {
                        "type": "imu",
                        "player_id": 1,
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
                            "timestamp": i,
                        },
                    }
                )
