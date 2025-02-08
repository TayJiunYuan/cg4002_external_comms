from multiprocessing import Queue
from src.core.ai_service.dummy_ai_service import DummyAISerivce


def dummy_ai_service_process(to_ai_queue: Queue, from_ai_queue: Queue):
    dummy_ai_service = DummyAISerivce()
    while True:
        imu_data = to_ai_queue.get()
        if imu_data:
            action = dummy_ai_service.generate_random_action()
            from_ai_queue.put(action)
