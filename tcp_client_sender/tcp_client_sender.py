import socket
import json
from models.sensor_packet import ShootPacket, IMUPacket


class TCPClientSender:
    """Class for TCP Client on Laptop to send sensor data to TCP Server on Ultra 96"""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            print(f"Sender Client - Connected to {self.host}:{self.port}")
        except (socket.error, ConnectionRefusedError) as e:
            print(f"Sender Client - Connection error: {e}")

    def send_packet(self, packet: IMUPacket | ShootPacket):

        encoded_json = json.dumps(packet).encode("utf-8")
        message_length = f"{len(encoded_json)}_".encode("utf-8")
        try:
            self.socket.sendall(message_length + encoded_json)
            print(f"Sender Client - Sent: {packet}")
        except socket.error as e:
            print(f"Sender Client - End error: {e}")
