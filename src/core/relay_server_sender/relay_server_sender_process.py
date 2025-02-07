from multiprocessing import Queue
from src.core.relay_server_sender.relay_server_sender import RelayServerSender


def relay_server_sender_process(
    host: str, port: int, player_id: int, to_relay_queue: Queue
):
    server = RelayServerSender(
        host=host, port=port, player_id=player_id, to_relay_queue=to_relay_queue
    )
    server.start()
    while True:
        hp_and_bullets = to_relay_queue.get()
        server.send_hp_and_bullets(hp_and_bullets)
