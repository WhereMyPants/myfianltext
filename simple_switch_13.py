from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ether
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import tcp
from ryu.lib.packet import udp
from ryu.lib.packet import ipv4
import dpkt
from collections import deque
from checkout import *
from CountingBloomFilter import CountingBloomFilter

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        #init_sys()
        self.mac_to_port = {}
        self.rember = deque([])
        self.tcpflag = 0
        self.tcpcheck = CountingBloomFilter(0.001, 7500)
        self.times = 0

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
# install table-miss flow entry
#
# We specify NO BUFFER to max_len of the output action due to
# OVS bug. At this moment, if we specify a lesser number, e.g.,
# 128, OVS will send Packet-In with invalid buffer_id and
# truncated packet data. In that case, we cannot output packets
# correctly.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        match = parser.OFPMatch(eth_type=ether.ETH_TYPE_IP, ipv4_dst='10.0.0.6', ip_proto=06)
        self.add_flow(datapath, 2, match, actions)
        match = parser.OFPMatch(eth_type=ether.ETH_TYPE_IP, ipv4_dst='10.0.0.6', ip_proto=021)
        self.add_flow(datapath, 2, match, actions)


    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        datapath.send_msg(mod)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        dst = eth.dst
        src = eth.src
        dpid = datapath.id

        ip = pkt.get_protocol(ipv4.ipv4)
        mytcp = pkt.get_protocol(tcp.tcp)
        myudp = pkt.get_protocol(udp.udp)
        if myudp:
            t1 = dpkt.ethernet.Ethernet(msg.data)
            t2 = dpkt.ip.IP(str(t1.data))
            t3 = dpkt.udp.UDP(str(t2.data))
            t4 = dpkt.dns.DNS(str(t3.data))
            print t4.qd[0].name
            if checkblacklist(t4.qd[0].name):
                return
            elif checkhostname(t4.qd[0].name):
                return

        if mytcp:
            t1 = dpkt.ethernet.Ethernet(msg.data)
            t2 = dpkt.ip.IP(str(t1.data))
            t3 = dpkt.tcp.TCP(str(t2.data))
            ipsrc = '%d.%d.%d.%d' % tuple(map(ord, list(t2.src)))
            ipdst = '%d.%d.%d.%d' % tuple(map(ord, list(t2.dst)))
            #print ipsrc, ipdst, t3.dport, t3.flags
            if t3.dport == 80 and t3.flags == 2 and ipdst != '10.0.0.1' and ipsrc != '10.0.0.7':
                print "SYN find"
                self.tcpflag = 1
                if self.tcpcheck.has_element(ipsrc):
                    self.tcpflag = 0
                    print "syn pass"
            elif t3.dport == 80 and t3.flags == 16 and ipdst != '10.0.0.1' and ipsrc != '10.0.0.7':
                self.tcpflag = 2
                if self.tcpcheck.has_element(ipsrc):
                    self.tcpflag = 0
                    print "ack pass"
                else:
                    self.tcpcheck.insert_element(ipsrc)
                    print ipsrc, "is frienfly"

        self.mac_to_port.setdefault(dpid, {})
        #self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)
# learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD
        actions = [parser.OFPActionOutput(out_port)]
# install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            if ip:
                #print "add flow", ip.src, ip.dst
                '''
                if ip.src not in self.rember:
                    self.rember.setdefault(ip.src, {})
                    self.rember[ip.src][ip.dst] = 2
                elif ip.dst not in self.rember[ip.src].keys():
                    self.rember[ip.src][ip.dst] = 2
                '''
                if ip.src != '10.0.0.6' and ip.src != '10.0.0.7' and ip.src != '10.0.0.8':
                    self.rember.append([ip.src, ip.dst])
                    if self.times <= 20:
                        self.times += 1
                if self.times <= 20:
                    match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_type=ether.ETH_TYPE_IP,
                                            ipv4_src=ip.src, ipv4_dst=ip.dst)
                    self.add_flow(datapath, 1, match, actions)



        data = None
        if self.tcpflag == 0:
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                      in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)
        elif self.tcpflag == 1:
            pkt = packet.Packet()
            pkt.add_protocol(ethernet.ethernet(ethertype=0x0800, dst='00:00:00:00:00:07', src=eth.src))
            pkt.add_protocol(ipv4.ipv4(src=ip.src, dst='10.0.0.7', proto=17))
            pkt.add_protocol(udp.udp(dst_port=9990))
            pkt.serialize()
            data = pkt.data
            out_port = ofproto.OFPP_FLOOD
            actions = [parser.OFPActionOutput(out_port)]
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                      in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=data)
            datapath.send_msg(out)
            self.tcpflag = 0
            #print "haha"
        elif self.tcpflag == 2:
            pkt = packet.Packet()
            pkt.add_protocol(ethernet.ethernet(ethertype=0x0800, dst='00:00:00:00:00:07', src=eth.src))
            pkt.add_protocol(ipv4.ipv4(src=ip.src, dst='10.0.0.7', proto=17))
            pkt.add_protocol(udp.udp(dst_port=8880))
            pkt.serialize()
            data = pkt.data
            out_port = ofproto.OFPP_FLOOD
            actions = [parser.OFPActionOutput(out_port)]
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                      in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=data)
            datapath.send_msg(out)
            self.tcpflag = 0