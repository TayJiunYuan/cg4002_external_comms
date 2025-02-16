import os
from multiprocessing import Process, Queue

from dotenv import load_dotenv

from src.core.ai_service.dummy_ai_service_process import \
    dummy_ai_service_process
from src.core.eval_client.evaluation_client_process import \
    evaluation_client_process
from src.core.game_engine.one_player_game_engine_process import \
    one_player_game_engine_process
from src.core.mqtt_client.mqtt_client_process import mqtt_client_process
from src.core.relay_server_receiver.relay_server_receiver_process import \
    relay_server_receiver_process
from src.core.relay_server_sender.relay_server_sender_process import \
    relay_server_sender_process

load_dotenv()

username = os.getenv("MQTT_USERNAME")
password = os.getenv("MQTT_PASSWORD")

if __name__ == "__main__":
    try:

        eval_server_port = int(input("Enter evaluation server port:\n"))

        to_game_engine_queue = Queue()
        to_relay_queue_p1 = Queue()
        to_relay_queue_p2 = Queue()
        to_ai_queue = Queue()
        from_eval_queue = Queue()
        to_eval_queue = Queue()
        from_visualizer_queue = Queue()
        to_visualizer_queue = Queue()

        relay_server_receiver_process_p1 = Process(
            target=relay_server_receiver_process,
            args=(
                "127.0.0.1",
                8002,
                1,
                to_game_engine_queue,
            ),
            daemon=True,
        )

        relay_server_sender_process_p1 = Process(
            target=relay_server_sender_process,
            args=(
                "127.0.0.1",
                8003,
                1,
                to_relay_queue_p1,
            ),
            daemon=True,
        )

        relay_server_receiver_process_p2 = Process(
            target=relay_server_receiver_process,
            args=(
                "127.0.0.1",
                8004,
                2,
                to_game_engine_queue,
            ),
            daemon=True,
        )

        relay_server_sender_process_p2 = Process(
            target=relay_server_sender_process,
            args=(
                "127.0.0.1",
                8005,
                2,
                to_relay_queue_p2,
            ),
            daemon=True,
        )

        ai_process = Process(
            target=dummy_ai_service_process,
            args=(to_ai_queue, to_game_engine_queue),
            daemon=True,
        )

        eval_client_process = Process(
            target=evaluation_client_process,
            args=(
                "127.0.0.1",
                eval_server_port,
                to_eval_queue,
                from_eval_queue,
            ),
            daemon=True,
        )

        mqtt_client_processs = Process(
            target=mqtt_client_process,
            args=(
                "9751cef7cdab4b7789aa3266429daf60.s1.eu.hivemq.cloud",
                8883,
                username,
                password,
                to_visualizer_queue,
                from_visualizer_queue,
            ),
            daemon=True,
        )

        game_engine_processs = Process(
            target=one_player_game_engine_process,
            args=(
                to_game_engine_queue,
                to_relay_queue_p1,
                to_relay_queue_p2,
                to_ai_queue,
                from_eval_queue,
                to_eval_queue,
                from_visualizer_queue,
                to_visualizer_queue,
            ),
            daemon=True,
        )

        relay_server_receiver_process_p1.start()
        relay_server_sender_process_p1.start()
        relay_server_receiver_process_p2.start()
        relay_server_sender_process_p2.start()
        ai_process.start()
        eval_client_process.start()
        mqtt_client_processs.start()
        game_engine_processs.start()

        relay_server_receiver_process_p1.join()
        relay_server_sender_process_p1.join()
        relay_server_receiver_process_p2.join()
        relay_server_sender_process_p2.join()
        ai_process.join()
        eval_client_process.join()
        mqtt_client_processs.join()
        game_engine_processs.join()

    except (KeyboardInterrupt, SystemExit):

        relay_server_receiver_process_p1.terminate()
        relay_server_sender_process_p1.terminate()
        relay_server_receiver_process_p2.terminate()
        relay_server_sender_process_p2.terminate()
        ai_process.terminate()
        eval_client_process.terminate()
        mqtt_client_processs.terminate()
        game_engine_processs.terminate()
