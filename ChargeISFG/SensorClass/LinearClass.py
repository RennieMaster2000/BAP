# -*- coding: utf-8 -*-
"""
Created on Tue Jun 10 11:36:41 2025

@author: tinke
"""
import numpy as np
from datetime import datetime
from typing import List, Tuple, Optional

class GlucoseSensor:
    def __init__(self, calibration_data: Optional[List[Tuple[float, float]]] = None) -> None:
        self.calibration_data = calibration_data or []
        self.a = 0
        self.b = 0
        self.history = []
        self._calibrate()
        self.cal_type = 1 # '1' one-point, otherwise set not to 1

    def add_reference_data(self, charge_coulombs: float, glucose_levels: float) -> None:
        self.calibration_data.append([charge_coulombs, glucose_levels])
        self._calibrate()

    def clear_calibration_data(self) -> None:
        self.calibration_data.clear()
        self.a = 0
        self.b = 0

    def _calibrate(self):
        if not self.calibration_data:
            return
        
        currents, glucose_levels = zip(*self.calibration_data)
        if self.cal_type == 1:
            current, glucose = self.calibration_data[-1]
            if current == 0:
                raise ValueError("Current cannot be zero in one-point calibration.")
            self.a = current / glucose
            self.b = 0 #current-glucose
        else:
            x = np.array(glucose_levels[-2:])
            y = np.array(currents[-2:])
            self.a, self.b = np.polyfit(x, y, 1)
            print(self.a, self.b)

    def calculate_glucose(self, charge_coulombs: float, time_seconds=1) -> float:
        if self.a == 0 and self.b == 0:
            raise ValueError("Model parameters are zero. Provide calibration data to enable calculation.")
        if time_seconds <= 0:
            raise ValueError("Time must be positive.")

        current = charge_coulombs / time_seconds
        glucose = (current - self.b) / self.a
        self.history.append((datetime.now(), glucose, self.a, self.b))
        return glucose

    def get_history(self) -> List[Tuple[datetime, float]] | None:
        return self.history
    