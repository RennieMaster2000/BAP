# -*- coding: utf-8 -*-
"""
Created on Wed May 14 15:30:21 2025

@author: Renéee
"""
import math
#Constants
xmeas = 0.025#? m
P = 15#-30mL/100g/min
F = 3#mL/100g/min
D = 2e-10#m^2/s
Rstarling = 0#fuck starling
A = 1#unit
Pa = 35#mmHg
Pv = 15#mmHg
sigmapi = 25#mmHg
Kf = 0.978#mL/min/mmHg

def JgainConst(Pa, Pv, Kf, sigmapi):
    return Kf*(0.5*sigmapi^2-sigmapi*Pa+0.5*Pa^2)/(Pv-Pa)
Jgain = JgainConst(Pa,Pv,Kf,sigmapi)

def JlossConst(Pa, Pv, Kf, sigmapi):
    return Kf*(0.5*sigmapi^2-sigmapi*Pv+0.5*Pv^2)/(Pv-Pa)
Jloss = JlossConst(Pa,Pv,Kf,sigmapi)


FickConstant = 1 - (1-math.exp(-P*A/F))*F/P
def Cfick(Cb):
    return Cb*FickConstant

gainconst = Jgain/(Jgain+Jloss)
lossconst = Jloss/(Jgain+Jloss)
def Cstarling(Cb,Ci):
    return gainconst*Cb+lossconst*Ci

def Cbi(Cb,Ci):
    return (1-Rstarling)*Cfick(Cb)+Rstarling*Cstarling(Cb,Ci)

def Cisf(x,t,Cb,Cisf0):
    Cbival = Cbi(Cb,Cisf0)
    return Cbival-(Cbival-Cisf0)*math.erf(x/(2*math.sqrt(D*t)))

