from multiprocessing import Queue
from src.core.tcp_server_receiver.tcp_server_receiver import TCPServerReceiver


def tcp_server_receiver_process(host: str, port: int, from_beetle_queue: Queue):
    server = TCPServerReceiver(host=host, port=port, queue=from_beetle_queue)
    server.start()
