import BgISFg as bi
import math
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

def FillConcentrationExpSpike(length):
    for i in range(length):
        bi.WriteN(i,math.exp(-abs(i-length/2)/10))

def FillConcentrationHomo(length,amount):
    for i in range(length):
        bi.WriteN(i,amount)


############main
l = 50
bi.InitN(l)
bi.InitModel(0.5,0.25)
FillConcentrationHomo(l,1)
duration = 8000
spring = mpl.colormaps['autumn']
matrix = np.zeros((l,duration))
for i in range(duration):
    matrix[:,i]=bi.concentrationarray.copy()
    bi.StepTime()
    #matrix[:,i]= np.ones(l)*i/duration
fig, ax = plt.subplots()
ax.set_xlabel('time(step units)')
ax.set_ylabel('space(step units)')
ax.pcolormesh(matrix,cmap=spring)#,vmin=0,vmax=1)
xskin = 45

fig1, ax1 = plt.subplots()
ax1.set_xlabel('time(step units)')
ax1.set_ylabel('sensor concentration(unitless)')
sourcedata = np.zeros(duration)
for i in range(duration-1):
    sourcedata[i]=bi.source(0,i)+matrix[0,i]#compensate the concentration-driven component
ax2 = ax1.twinx()
ax2.set_ylabel('source flux(unitless)')
ax1.plot(matrix[45,:],color='blue')
#ax1.plot(matrix[0,:],color='orange')
ax2.plot(sourcedata,color='red')
