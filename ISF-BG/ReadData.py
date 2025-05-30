import pandas as pd
import os


def getDataPandas(length, start):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'HDeviceCGM.txt')
    list = pd.read_csv(filename,skiprows=start,nrows=length,sep='|',dtype={'ID':'int','Bglucose':'float','type':'string'},parse_dates=['time'],date_format="%H:%M:%S",usecols=['ID','Bglucose','time','type'],header=0,names=['0','ID','1','2','3','time','days','internaltime','type','Bglucose'])
    return list
