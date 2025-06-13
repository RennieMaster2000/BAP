import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from ChargeISFG.SensorClass.LinearClass import GlucoseSensor
from ISFBG.TestISFGBG import GenerateBG

np.random.seed(1)
sensor_noise_var = 0
dt=300

def getDataPandas():
    script_dir = os.path.dirname(__file__)
    root_dir = os.path.dirname(script_dir)
    filename = os.path.join(root_dir, 'ISFBG', 'piep.csv')
    data = pd.read_csv(
        filename,
        sep=',',
        dtype={'id':'int', 'bloodglucose':'float', 'sensorglucose':'float', 'train':'bool'},
        parse_dates=['time'],
        usecols=['id', 'bloodglucose', 'time', 'train', 'sensorglucose'],
        header=0
    )
    return data

data = getDataPandas()
specific_id = 183
data = data[data['id'] == specific_id]
data_len = len(data)



#data = data.sort_values('time')

# Calculate time differences (in seconds) and cumulative time
data['time_diff'] = data['time'].diff().dt.total_seconds().fillna(0)  # First row has diff=0
data['cumulative_time'] = data['time_diff'].cumsum()  # t=0 for first measurement

init_sensor_sensitivity = 3
true_sensitivity = []
@np.vectorize
def sensor_sensitivity(t):
    sensor_decay = 0.02 * t / 86400
    sensitivity = init_sensor_sensitivity * (1 - sensor_decay)
    true_sensitivity.append(sensitivity)
    return sensitivity

def sensor_charge(measured_glucose, t):
    return measured_glucose * sensor_sensitivity(t)

# Apply sensor_charge to each row
data['sensorcharge'] = data.apply(
    lambda row: sensor_charge(row['sensorglucose'], row['cumulative_time']),
    axis=1
)
#print(data[['time_diff']])
#print(data[['time', 'bloodglucose', 'sensorglucose', 'sensorcharge']])

sensor_output = data['sensorcharge'].values + np.random.normal(0, sensor_noise_var, size=data_len)*init_sensor_sensitivity
true_glucose = data['bloodglucose']
ref_glucose = data['sensorglucose']
time = data['cumulative_time']


# --- GlucoseSensor Estimation ---
Sensor = GlucoseSensor()


calibration_indices = np.arange(0, data_len, int(1200*20 / dt))  # change 1200*2 to change cal. interval. 300 -> every minute, 8*60*60> every 8 hour
estimated_glucose = []

for i in range(len(time)):
    if i in calibration_indices:
        Sensor.add_reference_data(sensor_output[i], ref_glucose[i]+ 0*np.random.normal(0, 2))
    estimated_glucose.append(Sensor.calculate_glucose(sensor_output[i]))

# from scipy.signal import savgol_filter
# estimates[:, 0] = savgol_filter(estimates[:, 0], 5, 1)
# --- Plot ---
true_sensitivity = true_sensitivity[::2] # Estimated ISF Glucose
plt.figure(figsize=(12, 6))
plt.plot(time, true_glucose, label="True Glucose")
plt.plot(time, ref_glucose, label="ISF Glucose")
plt.plot(time, estimated_glucose, label="Estimated Glucose")
#plt.plot(time, GenerateBG(estimated_glucose, time, true_glucose[0]), label="Estimated BG")
plt.scatter(time, sensor_output / true_sensitivity, color='gray', alpha=0.3, s=10, label="Raw Sensor Output")
plt.scatter(time[calibration_indices], ref_glucose[calibration_indices], color='red', label="Finger Prick", zorder=5)
plt.xlabel("Time (hours)")
plt.ylabel("Glucose")
plt.title("Linear ISF Glucose Estimation")
plt.legend()
plt.grid(True)
plt.xlim(0, 8000)
plt.ylim(150, 210)
plt.show()

plt.figure(figsize=(12, 6))
plt.plot(time, np.abs(true_glucose - estimated_glucose) / true_glucose * 100)
plt.grid(True)
plt.ylim(0, 10)
plt.ylabel("Relative Error (%)")
plt.title("Glucose Estimation Error")
plt.show()

plt.figure(figsize=(12, 6))
plt.plot(time, true_sensitivity, label='True sensitivity')
arr= np.array(Sensor.history)
plt.plot(time, arr[:,2], label='Estimated Sensitivity')
plt.vlines(time[calibration_indices], 1, 2.3, alpha=0.3)
plt.legend()
plt.ylim(2.8,3.2)
plt.grid()
plt.title("Sensitivity Tracking")
plt.show()


# --- Evaluate accuracy ---
true = true_glucose
pred = estimated_glucose

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