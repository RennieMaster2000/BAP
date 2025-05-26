import numpy as np
import math
##Array interface
def ReadN(index):
    #give back concentration at index
    return concentrationarray[index]
def WriteN(index,value):
    #write concentration at index
    concentrationarray[index] = value
def InitN(length):
    #make global concentration array
    global concentrationarray
    global conclength
    conclength = length
    concentrationarray = np.zeros(length)

##Buffer
def ReadBuf(index):
    #give back concentration at index
    return buffer[index]
def WriteBuf(index,value):
    #write concentration at index
    buffer[index]=value
def InitBuf():
    #(re-)initialise array
    global buffer 
    buffer = np.zeros(conclength)
def CopyOverBuf():
    #copy buffer into array
    for i in range(conclength):
        WriteN(i,ReadBuf(i))

##Externals
def InitSource(K,S):
    global Kconst
    global SourceIndex
    Kconst = K
    SourceIndex = S
def SetSource(Amount,mode):
    global SourceAm
    global modesource
    SourceAm = Amount
    modesource = mode
def source(index=0,time=0):
    #return source value
    result = 0
    if index==SourceIndex:
        result = Kconst*(SourceAm-ReadN(0))
        if modesource==1:
            result = Kconst*SourceAm
    return result

##Model
timemoment = 0
def InitModel(D,T):
    global diffusion
    global timestep
    diffusion = D
    timestep = T
    timemoment = 0
def secondspatial(index):
    #Approx d/dx^2 of that index of the global array
    if index==0:
        #lower bound
        return ReadN(1)-ReadN(0)
    elif index==conclength-1:
        return ReadN(index-1)-ReadN(index)
    else: 
        return ReadN(index+1)+ReadN(index-1)-2*ReadN(index)
def StepTime():
    #Apply a timestep through buffer, then write to array
    InitBuf()
    global timemoment
    for i in range(conclength):
        WriteBuf(i,ReadN(i)+timestep*(diffusion*secondspatial(i)+source(i,timemoment)))
    timemoment = timemoment+1
    CopyOverBuf()

        