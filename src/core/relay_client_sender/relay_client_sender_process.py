from multiprocessing import Queue
from src.core.relay_client_sender.relay_client_sender import RelayClientSender


def relay_client_sender_process(
    host: str, port: int, player_id: int, to_u96_queue: Queue
):
    client = RelayClientSender(host=host, port=port, player_id=player_id)
    client.connect()
    while True:
        sensor_packet = to_u96_queue.get()
        client.send_packet(sensor_packet)
