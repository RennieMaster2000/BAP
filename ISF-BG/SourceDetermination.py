# -*- coding: utf-8 -*-
"""
Created on Sun May 25 12:46:30 2025

@author: Renéee
"""
import BgISFg as bi
import numpy as np
import matplotlib.pyplot as plt
import math
#constants
D = 0.25
T = 0.5
K = 0.5
Xs = 0
l = 49
Xk = 45
measureperiod = 10000

# Init
bi.InitN(l+1)
bi.InitModel(D, T)
bi.InitSource(K, Xs)

# Determine B
bi.SetSource(1,0)
for i in range(l+1):
    bi.WriteN(i, 0)
for i in range(measureperiod):
    bi.StepTime()
B = bi.ReadN(Xk)
print(B)

    
# Simulate unknown source
bi.SetSource(3,0)
for i in range(l+1):
    bi.WriteN(i, 4+4*math.cos(i))
for i in range(measureperiod):
    bi.StepTime()
WithSource = bi.ReadN(Xk)
WithSourceList = bi.concentrationarray.copy()
print(WithSource)

# Simulate 'sourceless'
bi.SetSource(0, 0)
for i in range(l+1):
    bi.WriteN(i, 4+4*math.cos(i))
for i in range(measureperiod):
    bi.StepTime()
WithoutSource = bi.ReadN(Xk)
WithoutSourceList = bi.concentrationarray.copy()
print(WithoutSource)

# determine source
Result = (WithSource-WithoutSource)/B
print(Result)

plt.plot(WithSourceList,color='blue')
plt.plot(WithoutSourceList,color='red')
plt.xlabel('Space(unit steps)')
plt.ylabel('Concentration(unitless)')
plt.legend(['Source','Sourceless'])
