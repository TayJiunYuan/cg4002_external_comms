from multiprocessing import Queue
from src.core.eval_client.evaluation_client import EvaluationClient


def evaluation_client_process(
    host: str, port: int, to_eval_queue: Queue, from_eval_queue: Queue
):
    client = EvaluationClient(host=host, port=port)
    client.connect()
    while True:
        predicted_game_state = to_eval_queue.get()
        client.send_game_state_prediction(predicted_game_state)
        correct_game_state = client.receive_correct_game_state()
        if correct_game_state:
            from_eval_queue.put(correct_game_state)
