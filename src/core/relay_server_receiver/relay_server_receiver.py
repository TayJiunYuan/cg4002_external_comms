import socket
import json
from src.models.sensor_packet import IMUPacket, ShootPacket
from src.utils.print_color import print_colored, COLORS
from multiprocessing import Queue


class RelayServerReceiver:
    """Class for TCP Server on Ultra 96 to receive sensor data from a TCP client on a laptop."""

    def __init__(self, host: str, port: int, player_id: int, from_relay_queue: Queue):
        self.host = host
        self.port = port
        self.player_id = player_id
        self.from_relay_queue = from_relay_queue
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )  # Allow reuse of the same port
        self.socket.bind((self.host, self.port))
        self.client_socket = None

    def start(self):
        """Start the server and continuously accept client connections."""
        self.socket.listen(0)
        print_colored(
            f"Relay Server (Receiver) - Listening on {self.host}:{self.port}",
            COLORS["green"],
        )

        while True:
            try:
                # Accept a client connection
                client_socket, client_address = self.socket.accept()
                self.client_socket = client_socket
                print_colored(
                    f"Relay Server (Receiver) P{self.player_id} - Connection established with {client_address}",
                    COLORS["green"],
                )

                # Handle the client in a loop
                self.handle_client()

            except KeyboardInterrupt:
                print_colored(
                    f"Relay Server (Receiver) P{self.player_id} - Shutting down due to keyboard interrupt.",
                    COLORS["green"],
                )
                break
            except socket.error as e:
                print_colored(
                    f"Relay Server (Receiver) P{self.player_id} - Server error: {e}",
                    COLORS["green"],
                )

        self.socket.close()
        print_colored(
            f"Relay Server (Receiver) P{self.player_id} - Server shut down.",
            COLORS["green"],
        )

    def handle_client(self):
        """Handles a single client connection."""
        try:
            while True:
                message = self.receive_packet(self.client_socket)
                if not message:
                    print_colored(
                        f"Relay Server (Receiver) P{self.player_id} - Client disconnected.",
                        COLORS["green"],
                    )
                    break  # Exit loop when client disconnects

                self.from_relay_queue.put(message)
                print_colored(
                    f"Relay Server (Receiver) P{self.player_id} - Received: {message}",
                    COLORS["green"],
                )

        except (socket.error, ConnectionError) as e:
            print_colored(
                f"Relay Server (Receiver) P{self.player_id} - Connection error: {e}",
                COLORS["green"],
            )
        finally:
            self.client_socket.close()

    def receive_packet(self, client_socket) -> ShootPacket | IMUPacket | None:
        """Receives a message from the client."""
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
