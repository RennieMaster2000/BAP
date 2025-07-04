import numpy as np
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mpld
import random
import sys
import pandas as pd
import os
import csv

def getDataPandas(length, start):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'HandalteredCGM.txt')
    list = pd.read_csv(filename,skiprows=start,nrows=length,sep='|',dtype={'ID':'int','Bglucose':'float','type':'string'},parse_dates=['time'],date_format="%H:%M:%S",usecols=['ID','Bglucose','time','type'],header=0,names=['0','1','ID','2','3','time','days','internaltime','type','Bglucose'])
    return list
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
        Kblood=(1 - (1-math.exp(-P*A/F))*F/P)*(1-Rstarling)+Rstarling*Jgain/(Jgain+Jloss)
        Kisf=Rstarling*Jloss/(Jgain+Jloss)
    else:
        Kblood=1 - (1-math.exp(-P*A/F))*F/P
        Kisf=0
    #Kblood=1
    #Kisf=1
    return Kblood, Kisf
    
def CreateISFData(BloodGlucose,Times, skindistanceum, D,T,P,F,A,Rstarling,sigmapi,Pv,Pa,Kf):
    #Setup
    arraylength = 25
    sensordistance = 20
    D = D*1e12/((skindistanceum/arraylength)**2)#adjusting diffusion
    
    bloodK, isfK = DetermineBloodISFConstant(P,F,A,Rstarling,sigmapi,Pv,Pa,Kf)
    array = (BloodGlucose[0]*bloodK/(1-isfK))*np.ones(arraylength) #Initial Value
    SensorGlucose = np.zeros(len(BloodGlucose))
    #loop
    for i in range(len(BloodGlucose)):
        SensorGlucose[i]=array[sensordistance]
        #sys.stdout.write("\033[F")#clear line
        print(f'Processing: {i+1}/{len(BloodGlucose)} steps')
        if i!=(len(BloodGlucose)-1):
            timejump = math.floor(int(Times[i+1]-Times[i])/(T*1e9))#1e9
            if timejump<0:
                print('Error: Timejump negative')
            #print(timejump)
            for j in range(timejump):
                source = BloodGlucose[i]+(j/timejump)*(BloodGlucose[i+1]-BloodGlucose[i])
                array=Timestep(source,array,arraylength,isfK,bloodK,T,D)
                #print(array[sensordistance])
    return SensorGlucose

def CreateISFData2(BloodGlucose,Times, skindistanceum, D,T,P,F,A,Rstarling,sigmapi,Pv,Pa,Kf):
    #Setup
    arraylength = 25
    sensordistance = 20
    D = D*1e12/((skindistanceum/arraylength)**2)#adjusting diffusion
    
    bloodK, isfK = DetermineBloodISFConstant(P,F,A,Rstarling,sigmapi,Pv,Pa,Kf)
    array = (BloodGlucose[0]*bloodK/(1-isfK))*np.ones(arraylength) #Initial Value
    SensorGlucose = np.zeros(4*len(BloodGlucose)-1)
    #Times2 = np.empty_like(np.zeros(2*len(BloodGlucose)-1),type(Times[0]))
    #loop
    for i in range(len(BloodGlucose)):
        SensorGlucose[4*i]=array[sensordistance]
        #Times2[2*i] = Times[i]
        #sys.stdout.write("\033[F")#clear line
        print(f'Processing: {i+1}/{len(BloodGlucose)} steps')
        if i!=(len(BloodGlucose)-1):
            timejump = math.floor(int(Times[i+1]-Times[i])/(T*1e9))#1e9
            if timejump<0:
                print('Error: Timejump negative')
            #print(timejump)
            for j in range(timejump):
                source = BloodGlucose[i]+(j/timejump)*(BloodGlucose[i+1]-BloodGlucose[i])
                array=Timestep(source,array,arraylength,isfK,bloodK,T,D)
                #print(array[sensordistance])
                if j==math.floor(timejump/2):
                    #Times2[2*i+1] = Times[i]+(Times[i+1]-Times[i])/2
                    SensorGlucose[4*i+2]=array[sensordistance]
                if j==math.floor(timejump/4):
                    #Times2[2*i+1] = Times[i]+(Times[i+1]-Times[i])/2
                    SensorGlucose[4*i+1]=array[sensordistance]
                if j==math.floor(3*timejump/4):
                    #Times2[2*i+1] = Times[i]+(Times[i+1]-Times[i])/2
                    SensorGlucose[4*i+3]=array[sensordistance]
                
    return SensorGlucose#, Times2

def BigGeneration(trainfrac):
    #Data finding
    data = getDataPandas(1000000,0)
    data = data[data['type']=='CGM']
    #ID finding
    UniqueIDs=data['ID'].unique()
    print(f'Amount of recordings: {len(UniqueIDs)}')
    #train/test split
    np.random.shuffle(UniqueIDs)
    traincutoff = math.ceil(trainfrac*len(UniqueIDs))
    trainIDs = UniqueIDs[:traincutoff]
    testIDs = UniqueIDs[traincutoff:]
    print(f'Train recordings: {len(trainIDs)}')
    print(f'Test recordings: {len(testIDs)}')
    #Add column
    data.insert(4,'Sglucose',0)
    data.insert(5,'train',0)
    data.insert(6,'sporting',0)
    
    data.insert(7,'D',0)
    data.insert(8,'Rstar',0)
    data.insert(9,'P',0)
    data.insert(10,'F',0)
    #ID processing
    random.seed()
    for i in UniqueIDs[:2]:
        print(f'\n\nStarting on ID {i}')
        #parameters
        Dconst = random.uniform(1,3)*1e-10
        Rstar = random.uniform(0,0.2)
        Pconst = random.uniform(15,30)
        Sporting = (random.random()<0.5)
        if Sporting:
            Fconst = random.uniform(5,15)
        else:
            Fconst = random.uniform(1,3)
        print(f'Parameters:\n\tD: {Dconst}\n\tRstar: {Rstar}\n\tP: {Pconst}\n\tSport: {Sporting}\n\tF: {Fconst}')
        #simulate
        FilteredData = data[data['ID']==i]
        ISFRec = CreateISFData(np.flip(FilteredData['Bglucose'].values),np.flip(FilteredData['time'].values),40,Dconst,0.01,Pconst,Fconst,1,Rstar,25,15,35,0.978)
        #record(train,sport,param,ISFRec)
        FDindexes = FilteredData.index
        ISFRec=np.flip(ISFRec)
        for j in range(len(FDindexes)):
            data.at[FDindexes[j],'Sglucose',ISFRec[j]]
            data.at[FDindexes[j],'D',Dconst]
            data.at[FDindexes[j],'F',Fconst]
            data.at[FDindexes[j],'P',Pconst]
            data.at[FDindexes[j],'Rstar',Rstar]
            data.at[FDindexes[j],'sporting',Sporting]
            if np.isin(i,trainIDs):
                data.at[FDindexes[j],'train',True]
            else:
                data.at[FDindexes[j],'train',False]
        print(f'Finishing on ID {i}')
    #make file
    print(data)

def GenerateID(id,train):
    data = getDataPandas(None,0)
    data = data[data['type']=='CGM']
    #get data of ID
    data=data[data['ID']==id]
    bg = np.flip(data['Bglucose'].values)
    times = np.flip(data['time'].values) #pls reorder them

    #Determine parameters
    Dconst = random.uniform(1,3)*1e-10
    Rstar = random.uniform(0,0.2)
    Pconst = random.uniform(15,30)
    Sporting = (random.random()<0.5)
    if Sporting:
        Fconst = random.uniform(5,15)
    else:
        Fconst = random.uniform(1,3)
    print(f'Parameters:\n\tD: {Dconst}\n\tRstar: {Rstar}\n\tP: {Pconst}\n\tSport: {Sporting}\n\tF: {Fconst}')
    #Generate data
    sg = CreateISFData(bg,times,40,Dconst,0.0025,Pconst,Fconst,1,Rstar,25,15,35,0.978)#1.5e-10,0.005,25,5,1,0.2,25,15,35,0.978)
    #write data
    field_names = ['id','time','bloodglucose','sensorglucose','D','P','F','Rstarling','Sport','train']
    with open('ISF-BG/piep.csv','a') as f_object:
        print('Writing...')
        dictwriter_object = csv.DictWriter(f_object, fieldnames=field_names)
        for i in range(len(bg)):
            dictwriter_object.writerow({'id':id,'time':times[i],'bloodglucose':bg[i],'sensorglucose':sg[i],'D':Dconst,'P':Pconst,'F':Fconst,'Rstarling':Rstar,'Sport':Sporting,'train':train})
        f_object.close()


'''
#BigGeneration(0.8)
data = getDataPandas(None,0)
uniqueids = data['ID'].unique()[10:]
for id in uniqueids:
    GenerateID(id,False)
'''
data = getDataPandas(None,0)
data= data[data['ID']==216]
timelist = np.flip(data['time'].values)
bloodlist = np.flip(data['Bglucose'].values)
isfdata = CreateISFData2(bloodlist,timelist,40,1e-10,0.01,25,5,1,0.2,25,15,35,0.978)#so problem is x is in meters rn, 100meters in total, so go to 1cm which is 10^4 smaller
#isfdata = isfdata + bloodlist[0] - isfdata[0]
fig, axs = plt.subplots()
times1 = np.linspace(0,(timelist[-1]-timelist[0])/np.timedelta64(1,'m'), len(bloodlist))
times2 = np.linspace(0,(timelist[-1]-timelist[0])/np.timedelta64(1,'m'), len(isfdata))

axs.plot(times1,bloodlist,color='red')
axs.plot(times2[:len(isfdata)-2],isfdata[:len(isfdata)-2],color='green')
axs.legend(['Blood Glucose Concentration','Sensor Glucose Concentration'])
axs.grid(True)
#axs.grid(True,which='major',linewidth='1')
#axs.grid(True,axis='x',which='minor',linewidth='0.5')
axs.set_xlabel('Time (minutes)')
axs.set_ylabel('Glucose concentration (mg/L)')
axs.set_xlim(0,110)
#axs.xaxis.set_major_formatter(mpld.DateFormatter('%H:%M'))
#axs.xaxis.set_minor_locator(mpld.MinuteLocator(byminute=None,interval=5,tz=None))
plt.show()
