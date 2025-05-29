import numpy as np
import math
import datetime
import ReadData
import matplotlib.pyplot as plt
import matplotlib.dates as mpld

def Timestep(source,array,length,isfK,bloodK,T,D):
    buffer = np.zeros(length)
    for i in range(length):
        if i==0:
            buffer[0]=array[0]+T*(D*(array[1]-array[0])+(source*bloodK+array[0]*(isfK-1)))
        elif i==length-1:
            buffer[i]=array[i]+T*D*(array[i-1]-array[i])
        else:
            buffer[i]=array[i]+T*D*(array[i+1]+array[i-1]-2*array[i])
    return buffer

def DetermineBloodISFConstant(P,F,A,Rstarling,sigmapi,Pv,Pa,Kf):
    if Rstarling!=0:
        Jgain=Kf*(0.5*sigmapi**2-sigmapi*Pa+0.5*Pa**2)/(Pv-Pa)
        Jloss=Kf*(0.5*sigmapi**2-sigmapi*Pv+0.5*Pv**2)/(Pv-Pa)
        print(f"Jgain: {Jgain}")
        print(f"Jloss: {Jloss}")
        Kblood=(1 - (1-math.exp(-P*A/F))*F/P)*(1-Rstarling)+Rstarling*Jgain/(Jgain+Jloss)
        Kisf=Rstarling*Jloss/(Jgain+Jloss)
    else:
        Kblood=1 - (1-math.exp(-P*A/F))*F/P
        Kisf=0
    #Kblood=1
    #Kisf=1
    print(f'Kblood: {Kblood}')
    print(f'Kisf: {Kisf}')
    return Kblood, Kisf
    
def CreateISFData(BloodGlucose,Times, skindistanceum, D,T,P,F,A,Rstarling,sigmapi,Pv,Pa,Kf):
    #Setup
    arraylength = 25
    sensordistance = 20
    D = D*1e12/((skindistanceum/arraylength)**2)#adjusting diffusion
    print(f'diffusion: {D}')
    
    bloodK, isfK = DetermineBloodISFConstant(P,F,A,Rstarling,sigmapi,Pv,Pa,Kf)
    array = (BloodGlucose[0]*bloodK/(1-isfK))*np.ones(arraylength) #Initial Value
    SensorGlucose = np.zeros(len(BloodGlucose))
    #loop
    for i in range(len(BloodGlucose)):
        SensorGlucose[i]=array[sensordistance]
        if i!=(len(BloodGlucose)-1):
            timejump = math.floor(int(Times[i+1]-Times[i])/(T*1e9))#1e9
            for j in range(timejump):
                source = BloodGlucose[i]+(j/timejump)*(BloodGlucose[i+1]-BloodGlucose[i])
                array=Timestep(source,array,arraylength,isfK,bloodK,T,D)
    return SensorGlucose

def BigGeneration():
    #Data finding
    data = ReadData.getDataPandas(None,0)
    #ID finding
    UniqueIDs=data['ID'].unique()
    print(len(UniqueIDs))
    #train/test split
    #ID processing
    #make file

BigGeneration()
'''
data = ReadData.getDataPandas(100,0)
data= data[data['ID']==782]
timelist = np.flip(data['time'].values)
bloodlist = np.flip(data['glucose'].values)
isfdata = CreateISFData(bloodlist,timelist,40,1e-10,0.01,25,5,1,0.2,25,15,35,0.978)#so problem is x is in meters rn, 100meters in total, so go to 1cm which is 10^4 smaller
fig, axs = plt.subplots()
axs.plot(timelist,bloodlist,color='red')
axs.plot(timelist,isfdata,color='green')
axs.legend(['Blood Glucose','Sensor Glucose'])
axs.grid(True,which='major',linewidth='1')
axs.grid(True,axis='x',which='minor',linewidth='0.5')
axs.xaxis.set_major_formatter(mpld.DateFormatter('%H:%M'))
axs.xaxis.set_minor_locator(mpld.MinuteLocator(byminute=None,interval=5,tz=None))
plt.show()
'''