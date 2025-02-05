from multiprocessing import Queue
from src.core.tcp_server_sender.tcp_server_sender import TCPServerSender


def tcp_server_sender_process(host: str, port: int, to_beetle_queue: Queue):
    server = TCPServerSender(host=host, port=port, queue=to_beetle_queue)
    server.start()
    while True:
        hp_and_bullets = to_beetle_queue.get()
        server.send_hp_and_bullets(hp_and_bullets)
