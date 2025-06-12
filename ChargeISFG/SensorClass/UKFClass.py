# -*- coding: utf-8 -*-
"""
Created on Tue Jun 10 12:04:59 2025

@author: tinke
"""

import numpy as np
from datetime import datetime
from typing import List, Tuple, Optional
from filterpy.kalman import UnscentedKalmanFilter as UKF
from filterpy.kalman import MerweScaledSigmaPoints

class GlucoseUKF:
    def __init__(self,
                 initial_glucose: float = 100.0,
                 initial_a: float = 0.0,
                 dt: float = 1.0,
                 process_noise: Tuple[float, float, float] = (1.0, 1.0, 0.0),
                 measurement_noise: float = 0):
        self.dt = dt
        self.points = MerweScaledSigmaPoints(n=3, alpha=1e-3, beta=2.0, kappa=0)
        self.ukf = UKF(dim_x=3, dim_z=1, fx=self.fx, hx=self.hx, dt=dt, points=self.points)

        # Initial state: [Glucose, Glucose change rate, sensor gain 'a']
        self.ukf.x = np.array([initial_glucose, 0.0, initial_a])
        self.ukf.P *= 100

        self.ukf.Q = np.diag(process_noise)
        self.ukf.R = np.array([[measurement_noise]])

        self.history = []

    @staticmethod
    def fx(x, dt):
        G, G_dot, a = x
        G_new = G + G_dot * dt
        return np.array([G_new, G_dot, a])

    @staticmethod
    def hx(x):
        G, _, a = x
        return np.array([a * G])

    def update(self, sensor_output: float, dt: Optional[float] = None) -> float:
        if dt is not None and dt != self.dt:
            self.dt = dt
            self.ukf.dt = dt

        self.ukf.predict()
        self.ukf.predict()
        self.ukf.predict()
        self.ukf.update(np.array([sensor_output]))

        est_glucose = self.ukf.x[0]
        self.history.append((datetime.now(), est_glucose, self.ukf.x.copy()))
        return est_glucose

    def calibrate(self, true_glucose: float) -> None:
        self.ukf.x[0] = true_glucose
        self.ukf.P = np.diag([1e-10, self.ukf.P[1,1], self.ukf.P[2,2]])  # very low uncertainty in glucose after calibration

    def get_current_estimate(self) -> Tuple[float, float, float]:
        """Returns the current estimate of [Glucose, Glucose_dot, Gain a]."""
        return tuple(self.ukf.x)

    def get_history(self) -> List[Tuple[datetime, float, np.ndarray]]:
        return self.history
