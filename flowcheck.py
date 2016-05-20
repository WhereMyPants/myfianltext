import math
flowmsg = {}
l = 2.5
h = 3.5
cu = 600
def checkflow(portid, time, pktnum):
    if time == 1:
        flowmsg.setdefault(portid, {})
        flowmsg[portid].setdefault('C', pktnum)
        flowmsg[portid].setdefault('Cmean', pktnum)
        flowmsg[portid].setdefault('Dvar', 0)
        flowmsg[portid].setdefault('U', 0)
        flowmsg[portid].setdefault('A', 0)
        flowmsg[portid].setdefault('a', 0)
        return 0
    else:
        c = flowmsg[portid]['C']
        cmean = flowmsg[portid]['Cmean']
        dvar = flowmsg[portid]['Dvar']
        u = flowmsg[portid]['U']
        attck = flowmsg[portid]['A']
        a = flowmsg[portid]['a']


        cmean = ((time - 1) * cmean + pktnum) / time
        fd1 = open(str(portid)+"cmean",'a')
        fd2 = open(str(portid)+"dvar",'a')
        fd1.write(str(cmean))
        fd2.write(str(dvar))
        fd1.close()
        fd2.close()
        
        #print(cmean)
        z = pktnum - c
        dvarnew = ((time - 2) * dvar + z * z) / (time - 1)
        if pktnum < l * cmean:
            unew = 0
        elif pktnum > h * cmean:
            unew = 1
        else:
            unew = pktnum / ((h-l) * cmean) - l / (h - l)
        #print(unew)

        if a != 0:
            print("a=", a)
        s = int( cu / pktnum )
        if s == 0:
            print("s==0")
            return 1
        else:
            if unew == 0:
                flowmsg[portid]['a'] = 0
                flowmsg[portid]['C'] = pktnum
                flowmsg[portid]['Cmean'] = cmean
                flowmsg[portid]['Dvar'] = dvarnew
                flowmsg[portid]['U'] = unew
                flowmsg[portid]['A'] = attck
                return 0
            else:
                a += 1
                print("dvar", dvar, "dvarnew", dvarnew)
                if dvarnew >= dvar:
                    attcknew = unew
                else:
                    print("choose", u, unew)
                    attcknew = max (u, unew)
                if a < s:
                    flowmsg[portid]['C'] = pktnum
                    flowmsg[portid]['Cmean'] = cmean
                    flowmsg[portid]['Dvar'] = dvarnew
                    flowmsg[portid]['U'] = unew
                    flowmsg[portid]['A'] = attcknew
                    flowmsg[portid]['a'] = a
                    return 0
                else:
                    print("attck", attck, "attcknew", attcknew)
                    if attcknew < attck:
                        a = s-1
                        flowmsg[portid]['C'] = pktnum
                        flowmsg[portid]['Cmean'] = cmean
                        flowmsg[portid]['Dvar'] = dvarnew
                        flowmsg[portid]['U'] = unew
                        flowmsg[portid]['A'] = attcknew
                        flowmsg[portid]['a'] = a
                        return 0
                    else:
                        return 1


\



