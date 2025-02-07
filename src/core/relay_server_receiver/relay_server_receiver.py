import socket
import json
from src.models.sensor_packet import IMUPacket, ShootPacket
from src.utils.print_color import print_colored, COLORS
from multiprocessing import Queue


class RelayServerReceiver:
    """Class for TCP Server on Ultra 96 to receive sensor data from a TCP client on laptop"""

    def __init__(self, host: str, port: int, player_id: int, from_relay_queue: Queue):
        self.host = host
        self.port = port
        self.player_id = player_id
        self.from_relay_queue = from_relay_queue
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))

    def start(self):
        """Start the server and wait for a single client connection"""
        self.socket.listen(1)
        print_colored(
            f"Relay Server (Receiver) - Listening on {self.host}:{self.port}",
            COLORS["green"],
        )

        try:
            # Accept a single client connection
            client_socket, client_address = self.socket.accept()
            print_colored(
                f"Relay Server (Receiver) P{self.player_id} - Connection established with {client_address}",
                COLORS["green"],
            )

            while True:
                message = self.receive_packet(client_socket)
                self.from_relay_queue.put(message)
                if not message:
                    print_colored(
                        f"Relay Server (Receiver) P{self.player_id} - Client disconnected.",
                        COLORS["green"],
                    )
                    break  # Exit loop when client disconnects

                print_colored(
                    f"Relay Server (Receiver) P{self.player_id} - Received: {message}",
                    COLORS["green"],
                )

            client_socket.close()
        except (socket.error, KeyboardInterrupt) as e:
            print_colored(
                f"Relay Server (Receiver) P{self.player_id} - Server error: {e}",
                COLORS["green"],
            )
        finally:
            self.socket.close()
            print_colored(
                f"Relay Server (Receiver) P{self.player_id} - Server shut down.",
                COLORS["green"],
            )

    def receive_packet(self, client_socket) -> ShootPacket | IMUPacket:
        """Receives a message from the client"""
        try:
            # Read message length
            length_data = b""
            while not length_data.endswith(b"_"):
                chunk = client_socket.recv(1)
                if not chunk:
                    raise ConnectionError("Connection lost while receiving length.")
                length_data += chunk

            length = int(length_data[:-1].decode("utf-8"))

            # Read message content
            data = b""
            while len(data) < length:
                chunk = client_socket.recv(length - len(data))
                if not chunk:
                    raise ConnectionError("Connection lost while receiving message.")
                data += chunk

            return json.loads(data.decode("utf-8"))
        except (ValueError, socket.error, ConnectionError) as e:
            print_colored(
                f"Relay Server (Receiver) P{self.player_id} - Receive error: {e}",
                COLORS["green"],
            )
            return None
