from typing import Optional, Dict, Literal


class imuData:
    """Represents IMU data structure."""

    aX_g: int
    aY_g: int
    aZ_g: int
    gX_g: int
    gY_g: int
    gZ_g: int
    aX_v: int
    aY_v: int
    aZ_v: int
    gX_v: int
    gY_v: int
    gZ_v: int
    timestamp: int


class SensorPacket:
    """Base class for sensor packet."""

    type: Literal["imu", "shoot", "dc"]
    player_id: int
    data: Optional[Dict] = None


class IMUPacket(SensorPacket):
    """IMU data packet."""

    type: Literal["imu"]
    data: imuData


class ShootPacket(SensorPacket):
    """Shoot data packet."""

    type: Literal["shoot"]
    data: None


class DisconnectPacket(SensorPacket):
    """Client disconnect Packet"""

    type: Literal["dc"]
    data = None
