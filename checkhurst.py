import math
import checkshannonnew
from collections import deque
sipentropy = deque([])
dipentropy = deque([])
sipHurst = deque([])
dipHurst = deque([])
N = 20
M = [3, 4, 5, 6, 7]
temp = 0
var = []
sipDH = 0
dipDH = 0
sipdh = deque([])
dipdh = deque([])


def linefit(x, y):
    N = float(len(x))
    sx, sy, sxx, syy, sxy = 0, 0, 0, 0, 0
    for i in range(0, int(N)):
        sx += x[i]
        sy += y[i]
        sxx += x[i] * x[i]
        syy += y[i] * y[i]
        sxy += x[i] * y[i]
    a = (sy * sx / N - sxy)/(sx * sx / N - sxx)
    #b = (sy - a * sx) / N
    #r = abs(sy * sx / N - sxy) / math.sqrt((sxx - sx * sx / N) * (syy - sy * sy / N))
    return a



def cacvar(list):
    L = len(list)
    i = 0
    t1 = 0
    while i < L:
        t1 += list[i] * list[i]
        i += 1
    t1 = t1 / L
    i = 0
    t2 = 0
    while i < L:
        t2 += list[i]
        i += 1
    t2 = (t2 / L) * (t2 / L)
    return t1 - t2


def check(list):
    L = len(list)
    i = 0
    t1 = 0
    while i < L:
        t1 += list[i]
        i += 1
    avg = t1 / L
    i = 0
    t2 = 0
    while i < L:
        t2 += (list[i] - avg) * (list[i] - avg)
        i += 1
    return t2 / L



def cachurst(dataset):
    var = []
    for m in M:
        block = int(N / m)
        err = N % block
        i = 0
        x = []
        while i < block:
            t = 0
            j = 0
            while j < m:
                t += dataset[i * m + j]
                j += 1
            t = t / m
            x.append(t)
            i += 1
        if err != 0:
            t = 0
            j = 0
            while j < err:
                t += dataset[i * m + j]
                j += 1
            t = t / err
            x.append(t)
        #dvar = cacvar(x)
        dvar = check(x)
        #print dvar
        if dvar <= 0:
            dvar = 1
        var.append(math.log(dvar, 2))
    i = 0
    X = []
    while i < len(M):
        X.append(math.log(M[i], 2))
        i += 1
    beta = -linefit(X, var)
    hurst = 1 - (beta / 2)
    return hurst

def checkhurst(dataset):
    global sipDH, dipDH, temp, sipdh, dipdh
    sip = checkshannonnew.cacShannonSport(dataset)
    dip = checkshannonnew.cacShannonDeth(dataset)

    if len(sipentropy) < N:
        sipentropy.append(sip)
        dipentropy.append(dip)
        #print len(sipentropy)
        temp += 1
    if len(sipentropy) == N and temp == N:
        temp += 1
        hurst = cachurst(sipentropy)
        sipHurst.append(hurst)
        fd = open("siphurst", 'a')
        fd.write(str(hurst)+'\n')
        fd.close()
        hurst = cachurst(dipentropy)
        dipHurst.append(hurst)
        fd = open("diphurst", 'a')
        fd.write(str(hurst)+'\n')
        fd.close()
    elif len(sipentropy) == N and temp > N:
        sipentropy.popleft()
        sipentropy.append(sip)
        dipentropy.popleft()
        dipentropy.append(dip)
        siphurst = cachurst(sipentropy)
        fd = open("siphurst", 'a')
        fd.write(str(siphurst)+'\n')
        fd.close()
        diphurst = cachurst(dipentropy)
        fd = open("diphurst", 'a')
        fd.write(str(diphurst)+'\n')
        fd.close()

        if len(sipHurst) < 10:
            sipHurst.append(siphurst)
            dipHurst.append(diphurst)
            #print len(sipHurst)
        else:

            sipHurst.popleft()
            sipHurst.append(siphurst)
            dipHurst.popleft()
            dipHurst.append(diphurst)

        if len(sipHurst) == 10:


            if sipDH == 0:
                i = 0
                while i < 9:
                    sipdh.append(abs(sipHurst[i + 1] - sipHurst[i]))
                    dipdh.append(abs(dipHurst[i + 1] - dipHurst[i]))
                    i += 1
                #sipdhnow = cacvar(sipdh)
                #dipdhnow = cacvar(dipdh)
                sipdhnow = check(sipdh)
                dipdhnow = check(dipdh)
                sipDH = sipdhnow
                dipDH = dipdhnow
                print "succee"
            else:
                sipdh.append(abs(sipHurst[9]-sipHurst[8]))
                sipdh.popleft()
                dipdh.append(abs(dipHurst[9]-dipHurst[8]))
                dipdh.popleft()
                #print len(sipdh)
                sipdhnow = check(sipdh)
                dipdhnow = check(dipdh)
                #sipdhnow = cacvar(sipdh)
                #dipdhnow = cacvar(dipdh)
            if abs(sipdhnow) >= 1.5:
                if abs(sipdhnow / sipDH - 1) >= 0.8:
                    print("find ddos way3 sip")
            elif abs(dipdhnow) >= 1.7:
                if abs(dipdhnow / dipDH - 1) >= 0.8:
                    print("find ddos way3 dip")
            else:
                sipDH = sipdhnow
                dipDH = dipdhnow
            #print sipDH, dipDH


'''
b = deque([1.0, 2.3, 2.5, 2.1, 2.0, 2.2, 2.3, 1.9, 1.8, 2.3,
            2.4, 2.7, 3.5, 3.2, 3.3, 3.0, 3.5, 2.9, 2.7, 2.5])
print((math.log2(20) / 2 - 1/2) * (math.log2(20) / 2 - 1/2))
print((math.log2(20) / 2 + 1/2) * (math.log2(20) / 2 + 1/2))
print( 20 * 0.05)
t = 9
t /= 3

print(cachurst(b))
'''