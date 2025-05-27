import pandas as pd
import os


def getDataPandas(length, start):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'CGMData.txt')
    list = pd.read_csv(filename,skiprows=start,nrows=length,sep='|',dtype={'ID':'int','glucose':'float'},parse_dates=['time'],date_format="%H:%M:%S",usecols=['ID','glucose','time'],header=0,names=['0','ID','1','2','3','time','days','internaltime','4','glucose'])
    return list
