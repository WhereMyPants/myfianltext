import math
from collections import deque
import flowcheck
msg = {
    'spot': {'arfa': 0.0, 'average': 0.0, 'y': 0.0},
    'deth': {'arfa': 0.0, 'average': 0.0, 'y': 0.0},
    'spotdeth': {'arfa': 0.0, 'average': 0.0, 'y': 0.0}
}
T = 1
N = 0.5
a = 2.0
weight = [0.4, 0.1, 0.2, 0.3]
shannon = {
    'spot': [0, 0, 0, 0, 0],
    'deth': [0, 0, 0, 0, 0],
    'spotdeth': [0, 0, 0, 0, 0]
}

def cacnum(dataset):
    n = 0
    for key in dataset.keys():
        n += dataset[key][2]
    return n
def cacShannonSport(dataset):
    num = 0
    dstCounts = {}
    for featVec in dataset.keys():
        currentdst = dataset[featVec][0]
        if currentdst not in dstCounts.keys():
            dstCounts[currentdst] = dataset[featVec][2]
        else:
            dstCounts[currentdst] += dataset[featVec][2]
        num += dataset[featVec][2]
    #print (dstCounts, num)

    if num == 0:
        return -1

    shannonsport = 0.0
    for key in dstCounts.keys():
        prob = float(dstCounts[key])/num
        shannonsport -= prob*math.log(prob, 2)
    return shannonsport

def cacShannonDeth(dataset):
    num = 0
    dstCounts = {}
    for featVec in dataset.keys():
        currentdst = dataset[featVec][1]
        if currentdst not in dstCounts.keys():
            dstCounts[currentdst] = dataset[featVec][2]
        else:
            dstCounts[currentdst] += dataset[featVec][2]
        num += dataset[featVec][2]
    #print (dstCounts, num)

    if num == 0:
        return -1

    shannondeth = 0.0
    for key in dstCounts.keys():
        prob = float(dstCounts[key])/num
        shannondeth -= prob*math.log(prob, 2)
    return shannondeth

def cacShannonSportDeth(dataset):
    num = 0
    spotCounts = {}
    dstCounts = {}
    for featVec in dataset.keys():
        currentdst = dataset[featVec][0]
        if currentdst not in spotCounts.keys():
            spotCounts[currentdst] = dataset[featVec][2]
        else:
            spotCounts[currentdst] += dataset[featVec][2]
        currentdst = dataset[featVec][1]
        if currentdst not in dstCounts.keys():
            dstCounts[currentdst] = dataset[featVec][2]
        else:
            dstCounts[currentdst] += dataset[featVec][2]
        num += dataset[featVec][2]

    if num == 0:
        return -1

    for featVec in dataset.keys():
        prob = float(dataset[featVec][2])/num
        dataset[featVec].append(prob)



    shannonsportdeth = 0.0
    shannonsportdethtemp = 0.0
    for key1 in dstCounts.keys():
        prob1 = float(dstCounts[key1]) / num
        for key2 in spotCounts.keys():
            prob = 0.0
            #print (key1, key2)
            for featVec in dataset.keys():
                if dataset[featVec][0] == key2 and dataset[featVec][1] == key1:
                    prob = dataset[featVec][3]
                    #print("haha")
            prob2 = prob / prob1
            if prob2:
                shannonsportdethtemp += prob2 * math.log(prob2, 2)
        shannonsportdeth -= prob1 * shannonsportdethtemp
        shannonsportdethtemp = 0.0
    return shannonsportdeth

def cacflag(name):
    times = shannon[name][4]
    i = 0
    avertemp = 0.0
    while i < 4:
        avertemp += weight[i] * shannon[name][times % 4]
        times += 1
        i += 1
    msg[name]['average'] = avertemp
    temp = 0.0
    i = 0
    while i < 4:
        temp += (shannon[name][i] - avertemp) * (shannon[name][i] - avertemp)
        i += 1
    temp /= 4
    temp = math.sqrt(temp)
    msg[name]['arfa'] = a * temp

def checkshannon(dataset):
    global msg, a, weight, shannon, N, T

    result = [0, 0, 0]
    flag = 0
    deths = cacShannonDeth(dataset)
    spots = cacShannonSport(dataset)
    spotdeths = cacShannonSportDeth(dataset)
    num = cacnum(dataset)
    #print "num=", num
    fd1 = open("Hdip", 'a')
    fd2 = open("Hsip", 'a')
    fd3 = open("Hdipsip", 'a')
    fd4 = open("pktnum", 'a')
    fd1.write(str(deths)+'\n')
    fd2.write(str(spots)+'\n')
    fd3.write(str(spotdeths)+'\n')
    fd4.write(str(num)+'\n')
    fd1.close()
    fd2.close()
    fd3.close()
    fd4.close()

    if deths == -1 or spots == -1 or spotdeths == -1:
        #print("There is no packets in this time")
        return [0, 0, 0]
    #insure the shannon be in [0, 1]
    deths /= math.log(num, 2)
    spots /= math.log(num, 2)
    spotdeths /= math.log(num, 2)

    flowcheck.checkflow(10, T, num)
    T += 1
    #print()
    #print("spotdeths = ", spotdeths)
    #print("deths = ", deths)
    #print("spots = ", spots)



    if deths > 0 and shannon['deth'][4] < 4:
        shannon['deth'][shannon['deth'][4]] = deths
        shannon['deth'][4] += 1
        flag = 1

    if spots > 0 and shannon['spot'][4] < 4:
        shannon['spot'][shannon['spot'][4]] = spots
        shannon['spot'][4] += 1
        flag = 1

    if spotdeths > 0 and shannon['spotdeth'][4] < 4:
        shannon['spotdeth'][shannon['spotdeth'][4]] = spotdeths
        shannon['spotdeth'][4] += 1
        flag = 1

    for key in shannon.keys():
        if shannon[key][4] == 4 and flag == 1:
            cacflag(key)
        elif shannon[key][4] >= 4:
            if key == 'deth':
                shannon[key][4] += 1
                if result[0] == 0:
                    temp = msg[key]['average'] - deths - msg[key]['arfa']
                    if (msg[key]['y'] + temp) > 0:
                        msg[key]['y'] += temp
                    else:
                        msg[key]['y'] = 0
                    if msg[key]['y'] > N:
                        result[0] = 1
                elif result[0] == 1:
                    temp = msg[key]['average'] - deths + msg[key]['arfa']
                    if temp < 0:
                        msg[key]['y'] += temp
                        if msg[key]['y'] <= N:
                            result[0] = 0
                            msg[key]['y'] = 0
            if key == 'spot':
                shannon[key][4] += 1
                if result[1] == 0:
                    temp = spots - msg[key]['average'] - msg[key]['arfa']
                    if (msg[key]['y'] + temp) > 0:
                        msg[key]['y'] += temp
                    else:
                        msg[key]['y'] = 0
                    if msg[key]['y'] > 0.8*N:
                        result[1] = 1
                elif result[1] == 1:
                    temp = spots - msg[key]['average'] + msg[key]['arfa']
                    if temp < 0:
                        msg[key]['y'] += temp
                        if msg[key]['y'] <= 0.8*N:
                            result[1] = 0
                            msg[key]['y'] = 0
            if key == 'spotdeth':
                shannon[key][4] += 1
                if result[2] == 0:
                    temp = spotdeths - msg[key]['average'] - msg[key]['arfa']
                    if (msg[key]['y'] + temp) > 0:
                        msg[key]['y'] += temp
                    else:
                        msg[key]['y'] = 0
                    if msg[key]['y'] > N:
                        result[2] = 1
                elif result[2] == 1:
                    temp = spotdeths - msg[key]['average'] + msg[key]['arfa']
                    if temp < 0:
                        msg[key]['y'] += temp
                        if msg[key]['y'] <= N:
                            result[2] = 0
                            msg[key]['y'] = 0
    #if result == [0, 0, 0]:
    for key in shannon.keys():
            #print(key, shannon[key][4])
        if key == 'deth' and shannon[key][4] >= 4:
            shannon[key][shannon[key][4] % 4] = deths
            #shannon[key][4] += 1
            cacflag(key)
        if key == 'spot' and shannon[key][4] >= 4:
            shannon[key][shannon[key][4] % 4] = spots
            #shannon[key][4] += 1
            cacflag(key)
        if key == 'spotdeth' and shannon[key][4] >= 4:
            shannon[key][shannon[key][4] % 4] = spotdeths
            #shannon[key][4] += 1
            cacflag(key)
    #else:
    if result != [0, 0, 0]:
        print "find ddos way2", result
    return result





'''
def CreateDataSet():
    dataset = {1: [1, '10.0.0.2', 56] ,
               2: [2, '10.0.0.1', 56] ,
               3: [1, '10.0.0.3', 30] ,
               4: [3, '10.0.0.1', 25] }
               #[0, 1, 'yes']]
    #labels = ['no surfacing', 'flippers']
    return dataset
    #, labels
myDat = CreateDataSet()

checkshannon(myDat)
#print(shannon)

myDat = {1: [1, '10.0.0.2', 50],
         2: [2, '10.0.0.1', 45],
         3: [1, '10.0.0.3', 32],
         4: [3, '10.0.0.1', 32]
        }
checkshannon(myDat)
#print(shannon)

myDat = {1: [1, '10.0.0.2', 40],
         2: [2, '10.0.0.1', 45],
         3: [1, '10.0.0.3', 32],
         4: [3, '10.0.0.1', 32],
         5: [4, '10.0.0.1', 30],
         6: [1, '10.0.0.4', 25]
         }
checkshannon(myDat)
#print(shannon)

myDat = {1: [1, '10.0.0.2', 40],
         2: [2, '10.0.0.1', 45],
         3: [1, '10.0.0.3', 32],
         4: [3, '10.0.0.1', 32],
         5: [4, '10.0.0.1', 30],
         6: [1, '10.0.0.4', 25],
         7: [5, '10.0.0.2', 40],
         8: [2, '10.0.0.5', 38]
         }
print(checkshannon(myDat))
#print(shannon)
#print(msg)

myDat = {1: [1, '10.0.0.2', 20],
         2: [2, '10.0.0.1', 25],
         3: [1, '10.0.0.3', 40],
         4: [3, '10.0.0.1', 45],
         5: [4, '10.0.0.1', 20],
         6: [1, '10.0.0.4', 18],
         7: [5, '10.0.0.2', 40],
         8: [2, '10.0.0.5', 40]
         }
print(checkshannon(myDat))
#print(shannon)
#print(msg)

myDat = {1: [1, '10.0.0.2', 20],
         2: [2, '10.0.0.1', 50],
         3: [1, '10.0.0.3', 40],
         4: [3, '10.0.0.1', 90],
         5: [4, '10.0.0.1', 40],
         6: [1, '10.0.0.4', 18],
         7: [5, '10.0.0.1', 80],
         8: [1, '10.0.0.5', 40]
         }
print(checkshannon(myDat))
#print(shannon)
#print(msg)

myDat = {1: [1, '10.0.0.2', 20],
         2: [2, '10.0.0.1', 50],
         3: [1, '10.0.0.3', 40],
         4: [3, '10.0.0.1', 90],
         5: [4, '10.0.0.1', 40],
         6: [1, '10.0.0.4', 18],
         7: [5, '10.0.0.1', 80],
         8: [1, '10.0.0.5', 40]
         }
print(checkshannon(myDat))
#print(shannon)
#print(msg)

myDat = {1: [1, '10.0.0.2', 20],
         2: [2, '10.0.0.1', 25],
         3: [1, '10.0.0.3', 40],
         4: [3, '10.0.0.1', 45],
         5: [4, '10.0.0.1', 20],
         6: [1, '10.0.0.4', 18],
         7: [5, '10.0.0.2', 40],
         8: [2, '10.0.0.5', 40]
         }
print(checkshannon(myDat))
#print(shannon)
#print(msg)

myDat = {1: [1, '10.0.0.2', 20],
         2: [2, '10.0.0.1', 25],
         3: [1, '10.0.0.3', 40],
         4: [3, '10.0.0.1', 45],
         5: [4, '10.0.0.1', 20],
         6: [1, '10.0.0.4', 18],
         7: [5, '10.0.0.2', 40],
         8: [2, '10.0.0.5', 40]
         }
print(checkshannon(myDat))
#print(shannon)
#print(msg)
myDat = {1: [1, '10.0.0.2', 20],
         2: [2, '10.0.0.1', 25],
         3: [1, '10.0.0.3', 40],
         4: [3, '10.0.0.1', 45],
         5: [4, '10.0.0.1', 20],
         6: [1, '10.0.0.4', 18],
         7: [5, '10.0.0.2', 40],
         8: [2, '10.0.0.5', 40]
         }
print(checkshannon(myDat))
#print(shannon)
#print(msg)
myDat = {1: [1, '10.0.0.2', 20],
         2: [2, '10.0.0.1', 25],
         3: [1, '10.0.0.3', 40],
         4: [3, '10.0.0.1', 45],
         5: [4, '10.0.0.1', 20],
         6: [1, '10.0.0.4', 18],
         7: [5, '10.0.0.2', 40],
         8: [2, '10.0.0.5', 40]
         }
print(checkshannon(myDat))
#print(shannon)
#print(msg)
myDat = {1: [1, '10.0.0.2', 20],
         2: [2, '10.0.0.1', 25],
         3: [1, '10.0.0.3', 40],
         4: [3, '10.0.0.1', 45],
         5: [4, '10.0.0.1', 20],
         6: [1, '10.0.0.4', 18],
         7: [5, '10.0.0.2', 40],
         8: [2, '10.0.0.5', 40]
         }
print(checkshannon(myDat))
#print(shannon)
#print(msg)

myDat = {1: [1, '10.0.0.2', 50],
         2: [2, '10.0.0.1', 45],
         3: [1, '10.0.0.3', 32],
         4: [3, '10.0.0.1', 32]
         }
print(checkshannon(myDat))
#print(shannon)
#print(msg)
myDat = {1: [1, '10.0.0.2', 50],
         2: [2, '10.0.0.1', 45],
         3: [1, '10.0.0.3', 32],
         4: [3, '10.0.0.1', 32]
         }
print(checkshannon(myDat))
#print(shannon)
#print(msg)
myDat = {1: [1, '10.0.0.2', 50],
         2: [2, '10.0.0.1', 45],
         3: [1, '10.0.0.3', 32],
         4: [3, '10.0.0.1', 32]
         }
print(checkshannon(myDat))
#print(shannon)
#print(msg)
'''
'''
datasets = {1: [1, '10.0.0.1', 0],
           2: [2, '10.0.0.1', 0],
           3: [3, '10.0.0.3', 0],
           4: [1, '10.0.0.1', 0]}
dataset1 = {1: ['10.0.0.1', 20],
            2: ['10.0.0.1', 40],
            3: ['10.0.0.3', 15],
            4: ['10.0.0.1', 17]}
dataset2 = {1: ['10.0.0.1', 20],
            2: ['10.0.0.1', 40],
            3: ['10.0.0.1', 15],
            4: ['10.0.0.1', 17]}
myDat = CreateDataSet()
print(checkshannon(datasets))
print (arr)
print(checkshannon(myDat))
print (arr)
print(checkshannon(myDat))
print (arr)
print(checkshannon(dataset1))
print (arr)
print(checkshannon(dataset1))
print (arr)
print(checkshannon(dataset2))
print (arr)
'''
