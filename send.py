#!/usr/bin/python
from scapy.all import *
from BitVector import BitVector
from time import sleep
import pcap
import dpkt
#from pcap import *
'''
fd = open("blacklist1", 'r')
i = 1
dns_server = "10.0.0.6"
while True:

    q = fd.readline().strip()  # use strip to take off '\n'



    if not q: # to the end of file, url is null

        break

    print (i, q)

    i += 1

    send(IP(src='10.0.0.1', dst=dns_server)/UDP(sport=RandShort())/DNS(qr=0, opcode=0, rd=1, qd=DNSQR(qname=q, qtype=1, qclass=1)))

    sleep(3)
'''

#filter='ip dst 192.168.1.2 and udp'
pc = pcap.pcap('h1-eth0')
send(IP(src='10.0.0.1', dst='10.0.0.6')/TCP(sport=RandShort(), dport=80, flags='S'))

#print 1
while True:
    pc.setfilter('tcp')
    x = pc.stats()
    #print 2
    #print x
    if x[0]:
        for i, j in pc.readpkts():
            #print "find"
            tem = dpkt.ethernet.Ethernet(j)
            t2 = tem.data
            t3 = t2.data
            if t3.dport == 80:
                if t3.flags == 18:
                    send(IP(src='10.0.0.1', dst='10.0.0.6')/TCP(sport=RandShort(), dport=80, flags='A'))
                    print "send ack"
                if t3.flags == 4:
                    send(IP(src='10.0.0.1', dst='10.0.0.6')/TCP(sport=RandShort(), dport=80, flags='S'))
                    print "send syn"

#sleep(4)
#send(IP(src='10.0.0.1', dst='10.0.0.2')/UDP(sport=RandShort())/DNS(qr=0, opcode=0, rd=1, qd=DNSQR(qname='q', qtype=1, qclass=1)))