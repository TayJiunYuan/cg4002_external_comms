""" 
Run TCP Client (Sending) on Laptop with dummy data for testing.
Command: 'python3 -m test.tcp_relay_clients.test_tcp_client_sender' from project root.
Run after starting TCP Server (Receiving) on Ultra96.
"""

from src.core.relay_client_sender.relay_client_sender import TCPClientSender
from datetime import datetime


dummy_imu_packet = {
    "type": "imu",
    "player_id": 1,
    "data": {
        "position": "glove",
        "accelerometer": {"x": 10, "y": 10, "z": 10},
        "gyroscope": {"yaw": 10, "pitch": 10, "roll": 10},
    },
    "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.")
    + f"{datetime.utcnow().microsecond:06d}"
    + "Z",
}

dummy_shoot_packet = {
    "type": "shoot",
    "player_id": 1,
    "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.")
    + f"{datetime.utcnow().microsecond:06d}"
    + "Z",
}

host = str(input("Host: "))
port = int(input("Port: "))

client = TCPClientSender(
    host=host,
    port=port,
)

client.connect()

while True:
    user_input = input(
        'Enter "i" to send dummy IMU data or "s" to send dummy shoot data: '
    )
    if user_input == "i":
        client.send_packet(packet=dummy_imu_packet)
    if user_input == "s":
        client.send_packet(packet=dummy_shoot_packet)
