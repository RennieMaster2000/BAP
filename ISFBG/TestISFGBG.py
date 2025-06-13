import numpy as np
import math
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mpld
import csv

def getDataPandas():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'piep.csv')
    list = pd.read_csv(filename,sep=',',dtype={'id':'int','bloodglucose':'float','sensorglucose':'float','train':'bool'},parse_dates=['time'],usecols=['id','bloodglucose','time','train','sensorglucose'],header=0)#date_format="%H:%M:%S"
    return list
def isfConstant():
    Kf = 0.978
    sigmapi = 25
    Pa = 35
    Pv = 15
    Rstarling = 0.1
    Jgain=Kf*(0.5*sigmapi**2-sigmapi*Pa+0.5*Pa**2)/(Pv-Pa)
    Jloss=Kf*(0.5*sigmapi**2-sigmapi*Pv+0.5*Pv**2)/(Pv-Pa)
    return Rstarling*Jloss/(Jgain+Jloss)

def SourceConstant(Kb,timejump):
    ####returns source constant as described in paper
    SensorX = 20
    array = np.zeros(25)
    array = Simulate(timejump,array,1,Kb)
    #print(f'Array: {array}\n\n')
    return array[SensorX]
    '''
    global sourceconstantDict
    if (Kb,timejump) in sourceconstantDict:
        #reuse old constant
        return sourceconstantDict[(Kb,timejump)]
    else:
        #Generate constant through simulation
    '''

def Simulate(timejump,initial,source,Kb):
    #returns array with values of simulation with initial condition 'initial' and source amount 'source', simulated for 'timejump' time
    #print(f'Simulation with timejump={timejump}, source={source}, Kb={Kb}')
    physiclength = 40e-6
    steps = 25
    D = (2e-10)/((physiclength/steps)**2)
    T = 0.005
    array = initial
    timesteps = math.floor(timejump/T)
    Ki = isfConstant()
    for i in range(timesteps):
        buffer = np.zeros(25)
        buffer[24] = array[24]+T*D*(array[23]-array[24])
        buffer[0]= array[0]+T*(D*(array[1]-array[0])+(source*Kb+array[0]*(Ki-1)))
        for j in range(1,24):
            buffer[j]=array[j]+T*D*(array[j+1]+array[j-1]-2*array[j])
        array = buffer
    return array

def bloodConstant(P):
    Kf = 0.978
    sigmapi = 25
    Pa = 35
    Pv = 15
    Rstarling = 0.1
    F = 4
    A = 1
    Jgain=Kf*(0.5*sigmapi**2-sigmapi*Pa+0.5*Pa**2)/(Pv-Pa)
    Jloss=Kf*(0.5*sigmapi**2-sigmapi*Pv+0.5*Pv**2)/(Pv-Pa)
    return (1 - (1-math.exp(-P*A/F))*F/P)*(1-Rstarling)+Rstarling*Jgain/(Jgain+Jloss)


def CalibrateKb(Sensor,Blood):
    return (Sensor/Blood)*(1-isfConstant())

def GenerateBG(SensorG,times,InitialBG):
    ####returns BG estimates
    sensorx = 20
    EstimatedBG = np.zeros(len(SensorG))
    EstimatedBG[0]=InitialBG
    array = np.ones(25)*SensorG[0]
    #Calibration
    Kb = CalibrateKb(SensorG[0],InitialBG)
    #Cycling through array
    for i in range(1,len(SensorG)):
        print(f'Step {i}/{len(SensorG)}')
        timejump = int(times[i]-times[i-1])#*1e-9
        #simulate sourceless
        arraySL = array.copy()
        arraySL = Simulate(timejump,arraySL,0,Kb)
        #Error
        Sc = SourceConstant(Kb,timejump)
        bloodavg = (SensorG[i]-arraySL[sensorx])/Sc
        #print(f'Source constant: {Sc}, difference: {SensorG[i]-arraySL[sensorx]}, bloodavg: {bloodavg}')
        EstimatedBG[i]=1.5*bloodavg -0.5*EstimatedBG[i-1]#extrapolation
        #alpha = 0.8
        #EstimatedBG[i] = alpha * bloodavg + (1 - alpha) * EstimatedBG[i - 1]
        #update initial
        array = Simulate(timejump,array,bloodavg,Kb)
    return EstimatedBG

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

def LinearEstimates(SensorG,BG0,BG1,i0,i1):
    #determine coefficients
    a = (BG0-BG1)/(SensorG[i0]-SensorG[i1])
    b = BG0 - a*SensorG[i0]
    #apply coefficients
    results = np.zeros(len(SensorG))
    for i in range(len(SensorG)):
        results[i] = a*SensorG[i]+b
    return results

def EstimateWriting():
    databig = getDataPandas()
    uniqueids = databig['id'].unique()
    for id in uniqueids:
        print(f'Starting on id {id}')
        data = databig[databig['id']==id]
        linear = LinearEstimates(data['sensorglucose'].values,data['bloodglucose'].values[0],data['bloodglucose'].values[len(data['bloodglucose'].values)-1],0,len(data['bloodglucose'].values)-1)
        model = GenerateBG(data['sensorglucose'].values,data['time'].values,data['bloodglucose'].values[0])
        with open('ISF-BG/estimations.csv','a') as f_object:
            print('Writing...')
            field_names = ['id','time','bloodglucose','sensorglucose','modelglucose','linearglucose']
            dictwriter_object = csv.DictWriter(f_object, fieldnames=field_names)
            for i in range(len(model)):
                dictwriter_object.writerow({'id':id,'time':data['time'].values[i],'bloodglucose':data['bloodglucose'].values[i],'sensorglucose':data['sensorglucose'].values[i],'modelglucose':model[i],'linearglucose':linear[i]})
            f_object.close()
            print('\n')
        

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'estimations.csv')
list = pd.read_csv(filename,sep=',',dtype={'id':'int','bloodglucose':'float','sensorglucose':'float','modelglucose':'float','linearglucose':'float'},parse_dates=['time'],header=0)
mardmodel = MARD(list['modelglucose'].values,list['bloodglucose'].values)
mardlinear = MARD(list['linearglucose'].values,list['bloodglucose'].values)
print(f'MARD model: {mardmodel*100}%, linear: {mardlinear*100}%')
model95,model99 = DetermineISOErrorCounts(list['modelglucose'].values,list['bloodglucose'].values)
model95 = model95*100/len(list['modelglucose'].values)
model99 = model99*100/len(list['modelglucose'].values)
print(f'Model 95%: {model95}%, model 99%: {model99}')
linear95,linear99 = DetermineISOErrorCounts(list['linearglucose'].values,list['bloodglucose'].values)
linear95 = linear95*100/len(list['modelglucose'].values)
linear99 = linear99*100/len(list['modelglucose'].values)
print(f'Linear 95%: {linear95}%, linear 99%: {linear99}')
#EstimateWriting()
'''
data = getDataPandas()
data = data[data['id']==232]
linear = LinearEstimates(data['sensorglucose'].values,data['bloodglucose'].values[0],data['bloodglucose'].values[len(data['bloodglucose'].values)-1],0,len(data['bloodglucose'].values)-1)
model = GenerateBG(data['sensorglucose'].values,data['time'].values,data['bloodglucose'].values[0])
fig, axs = plt.subplots()
axs.plot(data['time'].values,data['bloodglucose'].values,color='red')
axs.plot(data['time'].values,data['sensorglucose'].values,color='green')
axs.plot(data['time'].values,linear,color='orange')
axs.plot(data['time'].values,model,color='pink')
axs.legend(['Blood Glucose','Sensor Glucose','Linear Model','Our Model'])
axs.grid(True,which='major',linewidth='1')
axs.grid(True,axis='x',which='minor',linewidth='0.5')
axs.set_xlabel('Device time (hour:minute)')
axs.set_ylabel('Glucose (mg/L)')
axs.xaxis.set_major_formatter(mpld.DateFormatter('%H:%M'))
axs.xaxis.set_minor_locator(mpld.MinuteLocator(byminute=None,interval=5,tz=None))
plt.show()
'''
'''
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'MARDS.csv')
list = pd.read_csv(filename,sep=',',dtype={'id':'int','mardmodel':'float','mardlinear':'float','mardmodellinear':'float'},header=0)
list = list[list['id']!=232]
list = list[list['id']!=54]
mardmodel = np.average(list['mardmodel'].values)
mardlinear = np.average(list['mardlinear'].values)
mardmodellinear = np.average(list['mardmodellinear'].values)
#print(mardmodel)
print(mardlinear)
print(mardmodellinear)
'''
'''
datab = getDataPandas()
ids = datab['id'].unique()
big95 = np.zeros(len(ids))
big99 = np.zeros(len(ids))
bigmard = np.zeros(len(ids))
for i in range(len(ids)):
    idd = ids[i]
    data = datab[datab['id']==idd]
    print(f'Generating estimates for {idd}, number {i+1}/{len(ids)}')
    EstimateBG=GenerateBG(data['sensorglucose'].values,data['time'].values,data['bloodglucose'].values[0])
    postlinearisation = LinearEstimates(EstimateBG,data['bloodglucose'].values[0],data['bloodglucose'].values[len(data['bloodglucose'].values)-1],0,len(data['bloodglucose'].values)-1)
    count95,count99=DetermineISOErrorCounts(postlinearisation,data['bloodglucose'].values)
    print(f'Results of ID {idd}')
    print(f'95% standard met with {count95}/{len(postlinearisation)}, {100*count95/len(postlinearisation)}%')
    print(f'99% standard met with {count99}/{len(postlinearisation)}, {100*count99/len(postlinearisation)}%')
    mard = MARD(postlinearisation,data['bloodglucose'].values)
    print(f'MARD is {mard*100}%\n')
    big95[i]=count95
    big99[i]=count99
    bigmard[i]=mard
print('Final results')
print(f'mard: {bigmard}')
print(f'big95: {big95}')
print(f'big99: {big99}')
'''
