from multiprocessing import Queue
from src.core.relay_server_receiver.relay_server_receiver import RelayServerReceiver


def relay_server_receiver_process(
    host: str, port: int, player_id: int, from_relay_queue: Queue, to_ai_queue: Queue
):
    server = RelayServerReceiver(
        host=host,
        port=port,
        player_id=player_id,
        from_relay_queue=from_relay_queue,
        to_ai_queue=to_ai_queue,
    )
    server.start()
