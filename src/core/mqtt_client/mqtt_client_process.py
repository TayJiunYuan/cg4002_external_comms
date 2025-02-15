from multiprocessing import Queue
from src.core.mqtt_client.mqtt_client import MQTTClient
from src.models.visualizer_packet import VisibilityRequestPacket, VisualizerActionPacket


def mqtt_client_process(
    broker: str,
    port: int,
    username: str,
    password: str,
    to_visualizer_queue: Queue,
    from_visualizer_queue: Queue,
):
    client = MQTTClient(
        broker=broker,
        port=port,
        username=username,
        password=password,
        from_visualizer_queue=from_visualizer_queue,
    )
    while True:
        operation: VisualizerActionPacket | VisibilityRequestPacket = (
            to_visualizer_queue.get()
        )
        if "action" in operation:  # operation is send action packet
            client.send_action(operation)
        else:  # operation is request visibility
            client.request_visibility(operation)
