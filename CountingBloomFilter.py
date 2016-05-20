#_*_coding:utf_8_
import cmath
from BitVector import BitVector

class CountingBloomFilter(object):
    def __init__(self, error_rate, elementNum):
        #计算所需要的 bit 数
        self.bit_num = (-1) * elementNum * cmath.log(error_rate) / (cmath.log(2.0))

        #四字节对齐
        self.bit_num = self.align_4byte(self.bit_num.real)


        #chxfan: CBF needs 4 times that BF need

        self.bit_num = 4*self.bit_num

        print ('bit_num = %d' % self.bit_num)

        #分配内存
        self.bit_array = BitVector(size=self.bit_num)

        #计算 hash 函数个数, only effected by error_rate
        self.hash_num = cmath.log(2) * self.bit_num / elementNum
        self.hash_num = self.hash_num.real

        #向上取整
        self.hash_num = int(self.hash_num) + 1
        print ('hash_num = %d' % self.hash_num)

        #产生 hash 函数种子
        self.hash_seeds = self.generate_hashseeds(self.hash_num)



    def insert_element(self, element):
        tmp_c = 0
        for seed in self.hash_seeds:
            hash_val = self.hash_element(element, seed)
            # self.bit_array[hash_val] = 1
            # #设置相应的 4 比特位
            tmp = self.bit_array[4 * hash_val:4 * hash_val + 4]
            if tmp.intValue() <= 14:
                self.bit_array[4 * hash_val:4 * hash_val + 4] = BitVector( size=4, intVal= tmp.intValue() + 1)
            if tmp.intValue() > 1:
                tmp_c += 1
        if tmp_c == self.hash_num:
            print ("The new added element (%s) is not able to be deleted.", element)



        # 检查元素是否存在，存在返回 true，否则返回 false
    def has_element(self, element):
        for seed in self.hash_seeds:
            hash_val = self.hash_element(element, seed)
             # calculate hash value
            #print (hash_val)
            tmp = self.bit_array[4 * hash_val:4 * hash_val + 4]
            # if self.bit_array[hash_val] == 0:   #查看值
            if tmp.intValue() == 0:  # 查看值
                return False
        return True

        # 删除某个元素
    def delete_element(self, element):
        for seed in self.hash_seeds:
            hash_val = self.hash_element(element, seed)
            tmp = self.bit_array[4 * hash_val:4 * hash_val + 4]
                # whether element is in CBF or not, should be check by the call of has_element
                # by the user.the func in CBF should be as simple as possible.
                # if tmp.intValue() == 0:   #查看值
                # print "delete error! No such element: %s." % element
                # return
                # else:
            self.bit_array[4 * hash_val:4 * hash_val + 4] = BitVector( size=4, intVal= tmp.intValue() - 1)


            # 内存对齐
    def align_4byte(self, bit_num):
        num = int(bit_num / 32)
        num = 32 * (num + 1)
        return num

        # 产生 hash 函数种子,hash_num 个素数

    def generate_hashseeds(self, hash_num):
        count = 0
        # 连续两个种子的最小差值
        gap = 50

        hash_seeds = []
        for index in range(hash_num):  # 初始化 hash 种子为 0
            hash_seeds.append(0)
        for index in range(10, 10000):
            max_num = int(cmath.sqrt(1.0 * index).real)
            flag = 1
            for num in range(2, max_num):
                if index % num == 0:
                    flag = 0
                    break

            if flag == 1:
                # 连续两个 hash 种子的差值要大才行
                if count > 0 and (index - hash_seeds[count - 1]) < gap:
                    continue
                hash_seeds[count] = index
                count = count + 1

            if count == hash_num:
                break
        return hash_seeds


    def hash_element(self, element, seed):  # BKDR hash for string
        hash_val = 1
        for ch in str(element):
            hash_val = hash_val * seed + ord(ch)
        #print (hash_val)
        hash_val = abs(hash_val)  # 取绝对值
        #print(hash_val)
        #print(self.bit_num / 4)
        hash_val = hash_val % (int(self.bit_num / 4))  # 取模，防越界
        #print(hash_val)
        return hash_val