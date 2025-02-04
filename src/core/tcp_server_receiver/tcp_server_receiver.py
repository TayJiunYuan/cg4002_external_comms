import socket
import json
from src.models.sensor_packet import IMUPacket, ShootPacket


class TCPServerReceiver:
    """Class for TCP Server on Ultra 96 to receive sensor data from a TCP client on laptop"""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))

    def start(self):
        """Start the server and wait for a single client connection"""
        self.socket.listen(1)
        print(f"Receiver Server - Listening on {self.host}:{self.port}")

        try:
            # Accept a single client connection
            client_socket, client_address = self.socket.accept()
            print(f"Receiver Server - Connection established with {client_address}")

            while True:
                message = self.receive_message(client_socket)
                if not message:
                    print("Receiver Server - Client disconnected.")
                    break  # Exit loop when client disconnects

                print(f"Receiver Server - Received: {message}")

            client_socket.close()
        except (socket.error, KeyboardInterrupt) as e:
            print(f"Receiver Server - Server error: {e}")
        finally:
            self.socket.close()
            print("Receiver Server - Server shut down.")

    def receive_message(self, client_socket) -> ShootPacket | IMUPacket:
        """Receives a message from the client"""
        try:
            # Read message length
            length_data = b""
            while not length_data.endswith(b"_"):
                chunk = client_socket.recv(1)
                if not chunk:
                    raise ConnectionError(
                        "Receiver Server - Connection lost while receiving length."
                    )
                length_data += chunk

            length = int(length_data[:-1].decode("utf-8"))

            # Read message content
            data = b""
            while len(data) < length:
                chunk = client_socket.recv(length - len(data))
                if not chunk:
                    raise ConnectionError(
                        "Receiver Server - Connection lost while receiving message."
                    )
                data += chunk

            return json.loads(data.decode("utf-8"))
        except (ValueError, socket.error, ConnectionError) as e:
            print(f"Receiver Server - Receive error: {e}")
            return None
