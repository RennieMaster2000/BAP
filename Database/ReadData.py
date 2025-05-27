import pandas as pd
list = pd.read_csv('C:\\Users\\Renéee\\Documents\\GitHub\\BAP\\Dataset\\Data Tables\\HDeviceCGM.txt',nrows=30,sep='|',dtype={'ID':'int','glucose':'float'},parse_dates=['time'],usecols=['ID','glucose','time'],header=0,names=['0','ID','1','2','3','time','days','internaltime','4','glucose'])
print(list)