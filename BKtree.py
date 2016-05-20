#!/usr/bin/python

# -*- coding: utf-8 -*-

findOne = False

##==================calculate edit distance====================
def calculateDist(str1, str2):
    len1 = len(str1)
    len2 = len(str2)

    # 初始化矩阵
    diff = [[i+j for j in range(len2 + 1)] for i in range(len1 + 1)]
    #print(diff)
    for row in range(1, len1+1):
      for col in range(1, len2+1):
        if str1[row-1] == str2[col-1]:
            f = 0
        else:
            f = 1
        diff[row][col] = min(diff[row][col-1]+1, diff[row-1][col]+1, diff[row-1][col-1]+f)
        #print ('row=', row, 'col=', col, diff[row][col])
        #print (diff)
        #print (diff[row][col-1]+1, diff[row-1][col]+1, diff[row-1][col-1]+f)
    #print (diff)
        #sim = 1 - float(diff[len1][len2])/float(max(len1,len2)) 相似度
    return diff[len1][len2] # edit distance

##======================BK tree nod======================

class TreeNode(object):
    #data: its string
    #children: N>=0 children
    #dist: distance from father node
    def __init__(self, data = '0', children = None, dist = 0):
        self.data = data
        self.children = children
        self.dist = dist

    ##-------------get/set-------------------
    def setData(self, data):
        self.data = data

    def getData(self):
        return self.data

    def setChildren(self, children):
        self.children = children

    def getChildren(self):
        return self.children

    def setDist(self, dist):
        self.dist = dist

    def getDist(self):
        return self.dist


##-------------traversal/insert/findMinDist-------------------

    def DFStraversal(self):
        #print (self.data, self.dist)
        if self.children == None:
            return
        else:
            for i in range(len(self.children)):
                self.children[i].DFStraversal()


    def insert(self, node):
        if (self.data == node.getData()):
            return
            # print "%s is already in BK tree." % self.data
        elif self.children == None:  # 无子节点
            node.setDist(calculateDist(self.data, node.getData()))
            self.children = [node]
        else:  # 当前节点的 data 和插入节点的不同，而且当前节点有子节点
            dist = calculateDist(self.data, node.getData())
            for i in range(len(self.children)):
                if self.children[i].getDist() == dist:
                    self.children[i].insert(node)
                    return
            # 所有直接子节点的 dist 都不一样
            node.setDist(dist)
            self.children.append(node)

    # 寻找 node.data 对应的最小 edit dist 和相应节点的 data

    def findMinDist(self, node, minDist, minData, beta):
        dist = calculateDist(self.data, node.getData())
            # print self.data,dist
            # 更新到目前为止 （当前节点也算进去）的最小 dist 与对应的 hostname
        if dist < minDist:
            minDist = dist
            minData = self.data
            # print dist, self.data, node.getData(),minDist,minData
        # 找到相同 data 的节点（dist==0）或者 发现编辑距离的最小差异(dist==1)，则返回，并结束递归循环
        global findOne
        if dist == 0 or dist == 1:
            findOne = True
            return [minDist, minData]
        elif self.children == None: # 当前节点没有子节点，则返回
            return [minDist, minData]
        else: # 与 self.data 不匹配，而且有子节点
            min_x = max(1, abs(dist - beta))
            max_x = dist + beta
            for i in range(len(self.children)):
                if self.children[i].getDist() >= min_x and self.children[i].getDist()<= max_x:
                    [minDist, minData]=self.children[i].findMinDist(node,minDist,minData,beta)
                    if findOne:
                        break
            return [minDist,minData]

##==========================BK tree==========================

class BKtree(object):
    def __init__(self, root = None):
        self.root = root

    def setRoot(self,root):
        self.root = root

    def getRoot(self):
        return self.root

    def isEmpty(self):
        if self.root == None:
            return True
        else:
            return False

    def DFStraversal(self):
        if self.isEmpty():
            print ("empty BK tree")
            return
        else:
            self.root.DFStraversal()

    def insert(self, node):
        if self.isEmpty():
            self.setRoot(node)
        else:
            self.root.insert(node)

    def findMinDist(self, s, beta):
        if self.isEmpty():
            print ("empty BK tree")
            return [-1.-1]
        else:
            global findOne
            findOne = False
            node = TreeNode(s)
            return self.root.findMinDist(node, calculateDist(self.root.getData(), s), self.root.getData(), beta)