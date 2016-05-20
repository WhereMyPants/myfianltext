from operator import attrgetter
import simple_switch_13
import flowcheck
import checkshannonnew
import checkhurst
from collections import deque
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub


class SimpleMonitor(simple_switch_13.SimpleSwitch13):
    def __init__(self, *args, **kwargs):
        super(SimpleMonitor, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.statemsg = {}
        self.packetcount = {}
        self.portmsg = {}
        self.monitor_thread = hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPStateChange,[MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if not datapath.id in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]
    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(3)


    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)
        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)


    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body
        dataset = {}
        for stat in sorted([flow for flow in body if flow.priority == 1],
                            key=lambda flow: (flow.match['ipv4_src'],
                                              flow.match['ipv4_dst'])):
            if stat.match['ipv4_src'] not in self.statemsg:
                self.statemsg.setdefault(stat.match['ipv4_src'], {})
                self.packetcount.setdefault(stat.match['ipv4_src'], {})
                self.statemsg[stat.match['ipv4_src']][stat.match['ipv4_dst']] = stat.packet_count
                self.packetcount[stat.match['ipv4_src']][stat.match['ipv4_dst']] = stat.packet_count
            elif stat.match['ipv4_dst'] in self.statemsg[stat.match['ipv4_src']].keys():
                t = self.packetcount[stat.match['ipv4_src']][stat.match['ipv4_dst']]
                self.statemsg[stat.match['ipv4_src']][stat.match['ipv4_dst']] = stat.packet_count - t
                #if t == 0 and stat.packet_count == 0:
                #   self.statemsg[stat.match['ipv4_src']][stat.match['ipv4_dst']] = -1
                self.packetcount[stat.match['ipv4_src']][stat.match['ipv4_dst']] = stat.packet_count
            else:
                self.statemsg[stat.match['ipv4_src']][stat.match['ipv4_dst']] = stat.packet_count
                self.packetcount[stat.match['ipv4_src']][stat.match['ipv4_dst']] = stat.packet_count
        if self.statemsg:
            #print self.statemsg
            temp = 0
            for ipsrc in self.statemsg.keys():
                for ipdst in self.statemsg[ipsrc].keys():
                    if self.statemsg[ipsrc][ipdst] != 0:
                        dataset.setdefault(temp, [])
                        dataset[temp].append(ipsrc)
                        dataset[temp].append(ipdst)
                        #if self.statemsg[ipsrc][ipdst] != 0:
                        dataset[temp].append(self.statemsg[ipsrc][ipdst])
                        '''
                        else:
                            dataset[temp].append(1)
                            self.statemsg[ipsrc][ipdst] = -1
                        '''
                        temp += 1
            #print dataset
            '''
            for ipsrc in self.rember.keys():
                for ipdst in self.rember[ipsrc].keys():
                    dataset.setdefault(temp, [])
                    dataset[temp].append(ipsrc)
                    dataset[temp].append(ipdst)
                    dataset[temp].append(2)
                    temp += 1
            '''

            while(self.rember):
                dataset.setdefault(temp, [])
                dataset[temp].append(self.rember[0][0])
                dataset[temp].append(self.rember[0][1])
                dataset[temp].append(2)
                temp += 1
                self.rember.popleft()

            #self.rember = deque([])
            #print dataset
            #print "haha"
            checkshannonnew.checkshannon(dataset)
            checkhurst.checkhurst(dataset)



    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body
        for stat in sorted(body, key=attrgetter('port_no')):
            if stat.port_no not in self.portmsg.keys():
                self.portmsg.setdefault(stat.port_no, [])
                self.portmsg[stat.port_no].append(1)
                self.portmsg[stat.port_no].append(stat.rx_packets)
            elif stat.rx_packets - self.portmsg[stat.port_no][1]:
                t = stat.rx_packets - self.portmsg[stat.port_no][1]
                x = flowcheck.checkflow(stat.port_no, self.portmsg[stat.port_no][0], t)
                self.portmsg[stat.port_no][1] = stat.rx_packets
                self.portmsg[stat.port_no][0] += 1
                #print x
        print self.portmsg[1][0]