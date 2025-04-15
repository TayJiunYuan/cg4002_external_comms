from multiprocessing import Queue
from src.core.ai_service.ai_service import AIService
from src.models.sensor_packet import IMUPacket
import time
 
action_code = {
    0: "boxing",
    1: "shield",
    2: "reload",
    3: "badminton",
    4: "golf",
    5: "bomb",
    6: "logout",
    7: "fencing",
    8: "noise",
}


def process_packet(
    imu_packet,
    buffer,
    ai_service,
    from_ai_queue,
    player_id,
    last_action_time,
    time_threshold=300,
    max_packets=15,
):

    # If buffer is empty or latest packet is within time threshold and in order, then packet is valid, else it is not and buffer cleared
    if time.time() - last_action_time > 0.5 and (
        not buffer
        or (
            0
            < imu_packet["data"]["timestamp"] - buffer[-1]["data"]["timestamp"]
            <= time_threshold
        )
    ):
        buffer.append(imu_packet)
        # If buffer is full, send to ai prediction then clear buffer
        if len(buffer) == max_packets:
            action = ai_service.ai_predictor(buffer)
            if action != 8:
                last_action_time = time.time()
                from_ai_queue.put(
                    {
                        "player_id": player_id,
                        "action": action_code[action],
                        "type": "ai",
                    }
                )

            buffer.clear()
    else:
        buffer.clear()
        buffer.append(imu_packet)

    return last_action_time


def ai_service_process(to_ai_queue: Queue, from_ai_queue: Queue):
    ai_service = AIService()
    buffer_p1, buffer_p2 = [], []
    last_action_time_table = {"p1": 0, "p2": 0}

    while True:
        imu_packet: IMUPacket = to_ai_queue.get()
        if imu_packet["player_id"] == 1:
            last_action_time = process_packet(
                imu_packet,
                buffer_p1,
                ai_service,
                from_ai_queue,
                1,
                last_action_time_table["p1"],
            )
            last_action_time_table["p1"] = last_action_time

        else:
            last_action_time = process_packet(
                imu_packet,
                buffer_p2,
                ai_service,
                from_ai_queue,
                2,
                last_action_time_table["p2"],
            )
            last_action_time_table["p2"] = last_action_time
