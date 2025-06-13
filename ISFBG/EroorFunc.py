def DetermineISOErrorCounts(estimates,realvalues):
    ####returns both amount withing 95% margins and 99% margins and a bool saying if it passes
    count95 = 0
    count99 = 0
    acoef = [1,1.5,44/19,1.96,5/7,12/29,13/17,12/29]
    bcoef = [30,5,-52.1,1.2,-390/7,650/29,-1170/17,650/29]
    for i in range(len(estimates)):
        #95%
        if realvalues[i]<100:
            if abs(realvalues[i]-estimates[i])<15:
                count95=count95+1
        else:
            if abs(realvalues[i]-estimates[i])/realvalues[i]<0.15:
                count95=count95+1
        #99%
        #upperline1
        upperline1 = False
        if realvalues[i]<30:
            upperline1=(estimates[i]<60)
        elif realvalues[i]<50:
            #0
            upperline1=(estimates[i]<(realvalues[i]*acoef[0]+bcoef[0]))
        elif realvalues[i]<70:
            #1
            upperline1=(estimates[i]<(realvalues[i]*acoef[1]+bcoef[1]))
        elif realvalues[i]<260:
            #2
            upperline1=(estimates[i]<(realvalues[i]*acoef[2]+bcoef[2]))
        else:
            upperline1=True
        #upperline2
        upperline2 = False
        if realvalues[i]<30:
            upperline2=(estimates[i]<60)
        elif realvalues[i]<280:
            upperline2=(estimates[i]<(realvalues[i]*acoef[3]+bcoef[3]))
        else:
            upperline2=True
        #lowerline1
        lowerline1 = False
        if realvalues[i]<120:
            lowerline1=True
        elif realvalues[i]<260:
            lowerline1=(estimates[i]>realvalues[i]*acoef[4]+bcoef[4])
        else:
            lowerline1=(estimates[i]>realvalues[i]*acoef[5]+bcoef[5])
        #lowerline2
        lowerline2=False
        if realvalues[i]<90:
            lowerline2=True
        if realvalues[i]<260:
            lowerline2=(estimates[i]>realvalues[i]*acoef[6]+bcoef[6])
        else:
            lowerline2=(estimates[i]>realvalues[i]*acoef[7]+bcoef[7])
        if lowerline1 and lowerline2 and upperline1 and upperline2:
            count99 = count99+1
    return count95,count99

def MARD(estimates,realvalues):
    Tard = 0
    for i in range(len(estimates)):
        Tard = Tard + abs(estimates[i]-realvalues[i])/realvalues[i]
    return Tard/len(estimates)