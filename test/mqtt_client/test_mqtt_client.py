"""
Run MQTT Client on Ultra 96 for testing.
Command: 'python3 -m test.mqtt_client.test_mqtt_client' from project root.
Run after starting MQTT Broker and Visualizer MQTT Client. 
"""

from multiprocessing import Queue, Process
from src.core.mqtt_client.mqtt_client_process import mqtt_client_process


if __name__ == "__main__":

    dummy_action_packet = {
        "action": "gun",
        "player_id": 1,
        "opponent_hit_hp": 5,
        "opponent_died": False,
    }

    dummy_visibility_request_packet = {"request_id": 1, "player_id": 1}

    broker = str(input("TEST - Broker: "))
    port = int(input("TEST - Port: "))

    to_visualizer_queue = Queue()
    from_visualizer_queue = Queue()

    mqtt_client_process = Process(
        target=mqtt_client_process,
        args=(
            broker,
            port,
            to_visualizer_queue,
            from_visualizer_queue,
        ),
        daemon=True,
    )

    mqtt_client_process.start()

    while True:
        print()
        user_input = input(
            'Enter "v" to do a visibility request and enter "a" to send a action to visualizer:\n'
        )

        if user_input == "v":
            print(user_input)
            to_visualizer_queue.put(dummy_visibility_request_packet)
        if user_input == "a":
            to_visualizer_queue.put(dummy_action_packet)
