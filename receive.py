#!/usr/bin/python
import pcap
import dpkt
from scapy.all import *
from time import sleep

pc = pcap.pcap('h7-eth0')
#print 1
while True:
    pc.setfilter('udp')
    x = pc.stats()
    #print 2
    #print x
    if x[0]:
        for i, j in pc.readpkts():
            #print "find"
            tem = dpkt.ethernet.Ethernet(j)
            t2 = tem.data
            t3 = t2.data
            #print t3.dport
            if t3.dport == 9990:
                print "controller msg"
                ipsrc = '%d.%d.%d.%d' % tuple(map(ord, list(t2.src)))
                ipdst = '%d.%d.%d.%d' % tuple(map(ord, list(t2.dst)))
                sleep(3)
                send(IP(src='10.0.0.6', dst=ipsrc)/TCP(sport=RandShort(), dport=80, flags='SA'))
                print "send SYN/ACK"
                #sleep(5)
                #send(IP(src='10.0.0.3', dst=ipsrc)/TCP(sport=RandShort(), dport=80, flags='SA'))
            #print t3.flags
            if t3.dport == 8880:
                print "controller msg"
                ipsrc = '%d.%d.%d.%d' % tuple(map(ord, list(t2.src)))
                ipdst = '%d.%d.%d.%d' % tuple(map(ord, list(t2.dst)))
                sleep(3)
                send(IP(src='10.0.0.6', dst=ipsrc)/TCP(sport=RandShort(), dport=80, flags='R'))
                print "send RST"
                #sleep(5)
                #send(IP(src='10.0.0.3', dst=ipsrc)/TCP(sport=RandShort(), dport=80, flags='R'))