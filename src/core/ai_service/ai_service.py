import random
from src.utils.print_color import print_colored, COLORS
from pynq import allocate
from pynq import Overlay
import numpy as np
from scipy.stats import skew, kurtosis
import joblib


class AIService:
    def __init__(self):
        print_colored("AI - AI Service Started", COLORS["blue"])
        self.ol = Overlay("/home/xilinx/external-comms/src/core/ai_service/basic_400_dropout.bit")
        self.hls_ip = self.ol.MLP_HLS_0
        self.CONTROL_REGISTER = 0x0
        self.hls_ip.write(self.CONTROL_REGISTER, 0x81)
        self.dma = self.ol.axi_dma_0
        self.scaler = joblib.load(
            "/home/xilinx/external-comms/src/core/ai_service/scaler_400.pkl"
        )

    def compute_features(self, imu_data):

        raw_data = {
            "gX_g": [],
            "gY_g": [],
            "gZ_g": [],
            "aX_g": [],
            "aY_g": [],
            "aZ_g": [],
            "gX_v": [],
            "gY_v": [],
            "gZ_v": [],
            "aX_v": [],
            "aY_v": [],
            "aZ_v": [],
        }
        x = -1
        for i in raw_data:
            x += 1
            for j in range(0, 15):
                raw_data[i].append(imu_data[x + j * 12])

        features = []
        # mean
        for key in raw_data:
            arr = np.array(raw_data[key])
            raw_data[key] = arr
            features.append(np.mean(arr))
            features.append(np.var(arr))
            features.append(skew(arr))
            features.append(kurtosis(arr))
            features.append(np.mean(arr[:5]))  # first half mean
            features.append(np.mean(arr[5:10]))  # second half mean
            features.append(np.mean(arr[10:]))
        gyro_axes = ["gX", "gY", "gZ"]
        accel_axes = ["aX", "aY", "aZ"]
        sensors = ["_v", "_g"]
        for sensor in sensors:
            energy = 0
            for axis in gyro_axes:
                energy += (np.sum(raw_data[f"{axis}{sensor}"] ** 2)) / 15
            features.append(energy)
            energy = 0
            for axis in accel_axes:
                energy += (np.sum(raw_data[f"{axis}{sensor}"] ** 2)) / 15
            features.append(energy)

        return np.array(features)

    def ai_predictor(self, buffer):
        input_buffer = allocate(shape=(88,), dtype="int32")
        output_buffer = allocate(shape=(1,), dtype="int32")
        lst = []
        lst.append([])
        for i in range(0, 15):
            lst[0].append(buffer[i]["data"]["gX_g"])
            lst[0].append(buffer[i]["data"]["gY_g"])
            lst[0].append(buffer[i]["data"]["gZ_g"])
            lst[0].append(buffer[i]["data"]["aX_g"])
            lst[0].append(buffer[i]["data"]["aY_g"])
            lst[0].append(buffer[i]["data"]["aZ_g"])
        for i in range(0,15):
            lst[0].append(buffer[i]["data"]["gX_v"])
            lst[0].append(buffer[i]["data"]["gY_v"])
            lst[0].append(buffer[i]["data"]["gZ_v"])
            lst[0].append(buffer[i]["data"]["aX_v"])
            lst[0].append(buffer[i]["data"]["aY_v"])
            lst[0].append(buffer[i]["data"]["aZ_v"])
        lst = self.scaler.transform(lst)
        features = self.compute_features(lst[0])
        features = features * 1024
        features = features.astype("int32")
        np.copyto(input_buffer, features)
        self.dma.sendchannel.transfer(input_buffer)
        self.dma.sendchannel.wait()
        self.dma.recvchannel.transfer(output_buffer)
        self.dma.recvchannel.wait()
        self.action = output_buffer[0]
        del input_buffer, output_buffer
        print_colored(f"AI - Predicted {self.action}", COLORS["blue"])
        return self.action
