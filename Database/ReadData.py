import pandas as pd
import os

print(list)

def getDataPandas(length, start):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'CGMData.txt')
    list = pd.read_csv(filename,skiprows=start,nrows=length,sep='|',dtype={'ID':'int','glucose':'float'},parse_dates=['time'],usecols=['ID','glucose','time'],header=0,names=['0','ID','1','2','3','time','days','internaltime','4','glucose'])