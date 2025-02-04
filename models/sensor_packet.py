from typing import Optional, Dict, Literal


class imuData:
    """Represents IMU data structure."""

    position: Literal["glove", "vest"]
    accelerometer: Dict[str, int]  # {'x': int, 'y': int, 'z': int}
    gyroscope: Dict[str, int]  # {'yaw': int, 'pitch': int, 'roll'}


class SensorPacket:
    """Base class for sensor packet."""

    type: Literal["imu", "shoot"]
    player_id: int
    data: Optional[Dict] = None
    timestamp: str


class IMUPacket(SensorPacket):
    """IMU data packet."""

    type: Literal["imu"]
    data: imuData


class ShootPacket(SensorPacket):
    """Shoot data packet."""

    type: Literal["shoot"]
    data: None
