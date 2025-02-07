from multiprocessing import Queue
from src.core.relay_client_receiver.relay_client_receiver import RelayClientReceiver


def relay_client_receiver_process(
    host: str, port: int, player_id: int, from_u96_queue: Queue
):
    client = RelayClientReceiver(host=host, port=port, player_id=player_id)
    client.connect()
    while True:
        hp_and_bullets = client.receive_hp_and_bullets()
        from_u96_queue.put(hp_and_bullets)
