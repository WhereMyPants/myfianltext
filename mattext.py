import matplotlib.pyplot as plt
import pylab as ax
import sys
import numpy as np

#To draw y=x^2(-3<=x<=3)
def darw(name):
    t = 0
    x = []
    y = []
    fd = open(name, 'r')
    while True:
        data = fd.readline().strip()
        if not data:
            break

        #print t
        #data = float(data)
        y.append(data)
        x.append(t)
        t += 1
    #print y
    fd.close()
    #fig = plt.figure(1)

    #ax = fig.add_subplot(111)

    ax.plot(x, y, 'g-')
    ax.title(name)
    ax.xlabel('times')
    ax.ylabel(str(name))
    #'ro-'

    #ax = fig.add_subplot(212)

    #line2 = ax.plot(x, z, 'g-')
    plt.show()

if __name__ == '__main__':

    darw(sys.argv[1])