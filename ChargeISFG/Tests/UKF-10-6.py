# -*- coding: utf-8 -*-
"""
Created on Tue Jun 10 11:51:57 2025

@author: tinke
"""
import numpy as np
import matplotlib.pyplot as plt
from ChargeISFG.SensorClass.UKFClass import GlucoseUKF

np.random.seed(3)

# --- Simulation Parameters ---
dt = 5 / 60  # 5 minutes in hours
T = 24 * 14  # total hours
time = np.arange(0, T, dt)
sensor_noise_var = 6

# --- Simulated True Glucose ---
base_glucose = 100 + 0 * np.sin(2 * np.pi * time / (24 * 7))  # 7-day rhythm

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


true_sensitivity = 2 - (2 * 0.02 * time / 24)**2
sensor_output = true_sensitivity * true_glucose + 1*np.random.normal(0, sensor_noise_var, size=len(time))


# --- UKF Initialization ---
ukf_model = GlucoseUKF(initial_glucose=90, initial_a=0.0, dt=dt, measurement_noise=sensor_noise_var**2)


# --- Run UKF with periodic calibration ---
estimates = np.zeros((len(time), 3))
calibration_indices = np.arange(0, len(time), int(8 / dt))  # calibrate every 8 hours

for k in range(len(time)):
    est_glucose = ukf_model.update(sensor_output[k])
    if k in calibration_indices:
        ukf_model.calibrate(true_glucose[k] + 1*np.random.normal(0, 2))
    estimates[k] = ukf_model.get_current_estimate()

# --- Plotting ---
plt.figure(figsize=(12, 6))
plt.plot(time, true_glucose, label="True Glucose")
plt.plot(time, estimates[:, 0], label="Estimated Glucose")
plt.scatter(time, sensor_output / true_sensitivity, color='gray', alpha=0.3, s=10, label="Raw Sensor Output")
plt.scatter(time[calibration_indices], true_glucose[calibration_indices], color='red', label="Finger Prick", zorder=5)
plt.xlabel("Time (hours)")
plt.ylabel("Glucose")
plt.title("UKF Glucose Estimation with Sensor Drift and Slope Tracking")
plt.legend()
plt.grid(True)
plt.xlim(24 * 0, 24 * 5)
plt.ylim(80, 160)
plt.show()

plt.figure(figsize=(12, 6))
plt.plot(time, np.abs(true_glucose - estimates[:, 0]) / true_glucose * 100)
plt.grid(True)
plt.ylim(0, 10)
plt.ylabel("Relative Error (%)")
plt.title("Glucose Estimation Error")
plt.show()

plt.figure(figsize=(12, 6))
plt.plot(time, true_sensitivity, label='True sensitivity')
plt.plot(time, estimates[:, 2], label='Estimated Sensitivity')
plt.vlines(time[calibration_indices], 1, 2.3, alpha=0.3)
plt.legend()
plt.ylim(1.5, 2.3)
plt.grid()
plt.title("Sensitivity Tracking")
plt.show()


# --- Evaluate accuracy ---
true = true_glucose
pred = estimates[:, 0]

# # --- MARD ---
# mard = np.mean(np.abs(true - pred) / true) * 100
# print("MARD: {:.2f}%".format(mard))

# # --- ISO 15197 compliance ---
# iso_thresholds = np.where(true < 100, 15, 0.15 * true)
# abs_errors = np.abs(pred - true)
# iso_compliant = abs_errors <= iso_thresholds
# iso95 = np.mean(iso_compliant) * 100
# print("ISO95: {:.2f}%".format(iso95))

def DetermineISOErrorCounts(estimates,realvalues):
    ####returns both amount withing 95% margins and 99% margins and a bool saying if it passes
    count95 = 0
    count99 = 0
    acoef = [1,1.5,44/19,1.96,5/7,12/29,13/17,12/29]
    bcoef = [30,5,-52.1,1.2,-390/7,650/29,-1170/17,650/29]
    for i in range(len(estimates)):
        #95%
        if realvalues[i]<100:
            if abs(realvalues[i]-estimates[i])<15:
                count95=count95+1
        else:
            if abs(realvalues[i]-estimates[i])/realvalues[i]<0.15:
                count95=count95+1
        #99%
        #upperline1
        upperline1 = False
        if realvalues[i]<30:
            upperline1=(estimates[i]<60)
        elif realvalues[i]<50:
            #0
            upperline1=(estimates[i]<(realvalues[i]*acoef[0]+bcoef[0]))
        elif realvalues[i]<70:
            #1
            upperline1=(estimates[i]<(realvalues[i]*acoef[1]+bcoef[1]))
        elif realvalues[i]<260:
            #2
            upperline1=(estimates[i]<(realvalues[i]*acoef[2]+bcoef[2]))
        else:
            upperline1=True
        #upperline2
        upperline2 = False
        if realvalues[i]<30:
            upperline2=(estimates[i]<60)
        elif realvalues[i]<280:
            upperline2=(estimates[i]<(realvalues[i]*acoef[3]+bcoef[3]))
        else:
            upperline2=True
        #lowerline1
        lowerline1 = False
        if realvalues[i]<120:
            lowerline1=True
        elif realvalues[i]<260:
            lowerline1=(estimates[i]>realvalues[i]*acoef[4]+bcoef[4])
        else:
            lowerline1=(estimates[i]>realvalues[i]*acoef[5]+bcoef[5])
        #lowerline2
        lowerline2=False
        if realvalues[i]<90:
            lowerline2=True
        if realvalues[i]<260:
            lowerline2=(estimates[i]>realvalues[i]*acoef[6]+bcoef[6])
        else:
            lowerline2=(estimates[i]>realvalues[i]*acoef[7]+bcoef[7])
        if lowerline1 and lowerline2 and upperline1 and upperline2:
            count99 = count99+1
    return count95,count99

def MARD(estimates,realvalues):
    Tard = 0
    for i in range(len(estimates)):
        Tard = Tard + abs(estimates[i]-realvalues[i])/realvalues[i]
    return Tard/len(estimates)

iso = DetermineISOErrorCounts(pred, true)
print('ISO95:', iso[0]/len(pred)*100,'%')
print('ISO99:', iso[1]/len(pred)*100,'%')
print('MARD: {:.2f}%'.format(MARD(pred, true)*100))
