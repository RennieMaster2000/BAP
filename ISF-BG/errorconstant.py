# -*- coding: utf-8 -*-
"""
Created on Wed May 21 14:05:25 2025

@author: Renéee
"""
import math
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

def GiveErrorConstant(sensorx,sourcex,wallleft,wallright,nodestepconstant):
    #returns the errorconstant for the given parameters
    #We only consider that r=k-s
    
    #create matrix
    height = abs(sensorx-sourcex)+1
    width = 2*height-1
    matrix = np.zeros((height,width))
    
    sourceadjusted = math.floor(width/2)
    adjustedwallL = wallleft-sourcex+sourceadjusted
    adjustedwallR = wallright-sourcex+sourceadjusted
    
    #set first node
    matrix[0,math.floor(width/2)] = 1
    
    #spread
    for i in range(height-1):
        for j in range(width):
            if matrix[i,j]!=0:
                ####spread up from this node
                if j==adjustedwallL:
                    matrix[i+1,j]=matrix[i+1,j]+matrix[i,j]*(1-nodestepconstant) #up
                    matrix[i+1,j+1]=matrix[i+1,j+1]+matrix[i,j]*nodestepconstant #diag right
                elif j==adjustedwallR:
                    matrix[i+1,j]=matrix[i+1,j]+matrix[i,j]*(1-nodestepconstant) #up
                    matrix[i+1,j-1]=matrix[i+1,j-1]+matrix[i,j]*nodestepconstant #diag left
                else:
                    matrix[i+1,j]=matrix[i+1,j]+matrix[i,j]*(1-2*nodestepconstant) #up
                    matrix[i+1,j+1]=matrix[i+1,j+1]+matrix[i,j]*nodestepconstant #diag right
                    matrix[i+1,j-1]=matrix[i+1,j-1]+matrix[i,j]*nodestepconstant #diag left
    
    #return the constant
    result = matrix[height-1,0]
    if sourcex<sensorx:
        result = matrix[height-1,width-1]
    return result, matrix

############Test code
resu, matrixi = GiveErrorConstant(20,0,0,50,0.25)
print(resu)
spring = mpl.colormaps['autumn']
fig, ax = plt.subplots()
ax.set_xlabel('time(step units)')
ax.set_ylabel('space(step units)')
ax.pcolormesh(matrixi,cmap=spring,norm='log')#,vmin=0,vmax=1)
