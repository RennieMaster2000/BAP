# -*- coding: utf-8 -*-
"""
Created on Mon Jun  9 21:55:57 2025

@author: tinke
"""

import numpy as np
import matplotlib.pyplot as plt
from ChargeISFG.SensorClass.LinearClass import GlucoseSensor

np.random.seed(3)

# --- Simulation Parameters ---
dt = 5 / 60  # 5 minutes in hours
T = 24 * 14  # total hours
time = np.arange(0, T, dt)
sensor_noise_var = 6

# --- Simulated True Glucose ---
base_glucose = 100 + 1 * np.sin(2 * np.pi * time / (24 * 7))  # 7-day rhythm

meal_times = {'breakfast': 8, 'lunch': 13, 'dinner': 19}
def meal_spike(t, meal_hour, amplitude=40, width=1.5):
    return amplitude * np.exp(-0.5 * ((t - meal_hour) / width) ** 2)

true_glucose = base_glucose.copy()
for day in range(14):
    for meal, hour in meal_times.items():
        amp = np.random.normal(35, 5)
        width = np.random.normal(1.2, 0.3)
        center = day * 24 + hour + np.random.normal(0, 0.2)
        true_glucose += meal_spike(time, center, amp, width)

true_glucose_dot = np.gradient(true_glucose, dt)
true_sensitivity = 2 - (2 * 0.02 * time / 24)**1
sensor_output = true_sensitivity * true_glucose + np.random.normal(0, sensor_noise_var, size=len(time))

# --- GlucoseSensor Estimation ---
Sensor = GlucoseSensor()
calibration_indices = np.arange(0, len(time), int(8 / dt))
estimated_glucose = []

for i in range(len(time)):
    if i in calibration_indices:
        Sensor.add_reference_data(sensor_output[i], true_glucose[i]+ 1*np.random.normal(0, 2))
    estimated_glucose.append(Sensor.calculate_glucose(sensor_output[i]))

# from scipy.signal import savgol_filter
# estimates[:, 0] = savgol_filter(estimates[:, 0], 5, 1)
# --- Plot ---
plt.figure(figsize=(12, 6))
plt.plot(time, true_glucose, label="True Glucose")
plt.plot(time, estimated_glucose, label="Estimated Glucose")
plt.scatter(time, sensor_output / true_sensitivity, color='gray', alpha=0.3, s=10, label="Raw Sensor Output")
plt.scatter(time[calibration_indices], true_glucose[calibration_indices], color='red', label="Finger Prick", zorder=5)
plt.xlabel("Time (hours)")
plt.ylabel("Glucose")
plt.title("Linear Glucose Estimation")
plt.legend()
plt.grid(True)
plt.xlim(24 * 0, 24 * 5)
plt.ylim(80, 160)
plt.show()

plt.figure(figsize=(12, 6))
plt.plot(time, np.abs(true_glucose - estimated_glucose) / true_glucose * 100)
plt.grid(True)
plt.ylim(0, 10)
plt.ylabel("Relative Error (%)")
plt.xlabel("Time (hours)")
plt.title("Glucose Estimation Error")
plt.show()

plt.figure(figsize=(12, 6))
plt.plot(time, true_sensitivity, label='True sensitivity')
arr= np.array(Sensor.history)
plt.plot(time, arr[:,2], label='Estimated Sensitivity')
plt.vlines(time[calibration_indices], 1, 2.3, alpha=0.3)
plt.legend()
plt.ylim(1.2, 2.2)
plt.xlabel("Time (hours)")
plt.grid()
plt.title("Sensitivity Tracking")
plt.show()

# --- Evaluate accuracy ---
true = true_glucose
pred = estimated_glucose

# --- MARD ---
mard = np.mean(np.abs(true - pred) / true) * 100
print("MARD: {:.2f}%".format(mard))

# --- ISO 15197 compliance ---
iso_thresholds = np.where(true < 100, 15, 0.15 * true)
abs_errors = np.abs(pred - true)
iso_compliant = abs_errors <= iso_thresholds
iso95 = np.mean(iso_compliant) * 100
print("ISO95 compliant: {:.2f}%".format(iso95))