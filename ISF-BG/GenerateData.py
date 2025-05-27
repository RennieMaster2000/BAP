import numpy as np
import math
import datetime
import ReadData

def Timestep(source,array,length,isfK,bloodK,T,D):
    buffer = np.zeros(length)
    for i in range(length):
        if i==0:
            buffer[0]=array[0]+T*(D*(array[1]-array[0])+(source*bloodK-array[0]*isfK))
        elif i==length-1:
            buffer[i]=array[i]+T*D*(array[i-1]-array[i])
        else:
            buffer[i]=array[i]+T*D*(array[i+1]+array[i-1]-2*array[i])
    return buffer

def DetermineBloodISFConstant(P,F,A,Rstarling,sigmapi,Pv,Pa,Kf):
    '''
    if Rstarling!=0:
        Jgain=Kf*(0.5*sigmapi^2-sigmapi*Pa+0.5*Pa^2)/(Pv-Pa)
        Jloss=Kf*(0.5*sigmapi^2-sigmapi*Pv+0.5*Pv^2)/(Pv-Pa)
        Kblood=(1 - (1-math.exp(-P*A/F))*F/P)*(1-Rstarling)+Rstarling*Jgain/(Jgain+Jloss)
        Kisf=Rstarling*Jloss/(Jgain+Jloss)
    else:
        Kblood=1 - (1-math.exp(-P*A/F))*F/P
        Kisf=0
    '''
    Kblood=0.5
    Kisf=0.5
    return Kblood, Kisf
    
def CreateISFData(BloodGlucose,Times, D,T,P,F,A,Rstarling,sigmapi,Pv,Pa,Kf):
    #Setup
    arraylength = 100
    sensordistance = 95
    array = BloodGlucose[0]*np.ones(arraylength) #Initial Value
    SensorGlucose = np.zeros(len(BloodGlucose))
    #constants
    bloodK, isfK = DetermineBloodISFConstant(P,F,A,Rstarling,sigmapi,Pv,Pa,Kf)
    print(bloodK)
    #loop
    for i in range(len(BloodGlucose)):
        SensorGlucose[i]=array[sensordistance]
        if i!=(len(BloodGlucose)-1):
            timejump = math.floor(int(Times[i+1]-Times[i])/(T*1e9))
            for j in range(timejump):
                array=Timestep(BloodGlucose[i],array,arraylength,isfK,bloodK,T,D)
    return SensorGlucose

data = ReadData.getDataPandas(100,0)
data= data[data['ID']==782]
timelist = np.flip(data['time'].values)
bloodlist = np.flip(data['glucose'].values)
isfdata = CreateISFData(bloodlist,timelist,2e-10,0.01,15,3,1,0,25,15,35,0.978)
print(bloodlist)
print(isfdata)