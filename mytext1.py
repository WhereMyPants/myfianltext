from mininet.topo import Topo

class MyTopo( Topo ):

    def __init__( self ):

        Topo.__init__( self )

        hostone = self.addHost( 'h1' )
        hosttwo = self.addHost( 'h2' )
        hostthree = self.addHost( 'h3' )
        hostfour = self.addHost( 'h4' )
        hostfive = self.addHost( 'h5' )
        hostsix = self.addHost( 'h6' )
        hostseven = self.addHost( 'h7' )
        hosteight = self.addHost( 'h8' )
        switchone = self.addSwitch( 's1' )


        self.addLink( hostone, switchone )
        self.addLink( hosttwo, switchone)
        self.addLink( hostthree, switchone)
        self.addLink( hostfour, switchone)
        self.addLink( hostfive, switchone)
        self.addLink( hostsix, switchone)
        self.addLink( hostseven, switchone)
        self.addLink( hosteight, switchone)

topos = { 'mytext1': ( lambda: MyTopo() ) }
