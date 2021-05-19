####################################################
# DVrouter.py
# Name:
# JHED ID:
#####################################################

from packet import Packet
import sys
from collections import defaultdict
from router import Router
from json import dumps, loads

INF = 10000

class DVrouter(Router):
    """Distance vector routing protocol implementation."""

    def __init__(self, addr, heartbeatTime):
        """TODO: add your own class fields and initialization code here"""
        Router.__init__(self, addr)  # initialize superclass - don't remove
        self.heartbeatTime = heartbeatTime
        self.last_time = 0
        # Hints: initialize local state
        self.dis_vec = defaultdict(lambda: INF)
        self.dis_vec[self.addr] = 0
        self.forward_table = defaultdict(lambda: None)
        self.neigbours = defaultdict(lambda: None)

    def broadcastDisVec(self, table):
        for neighbour in self.neigbours.keys():
            if neighbour in table:
                dis_vec = self.dis_vec.copy()
                dis_vec[table[neighbour]] = INF
                packet = Packet(kind=Packet.ROUTING, srcAddr=self.addr, dstAddr=neighbour, content=dumps(dis_vec))
            else:
                packet = Packet(kind=Packet.ROUTING, srcAddr=self.addr, dstAddr=neighbour, content=dumps(self.dis_vec))
            self.send(self.neigbours[neighbour], packet)


    def handlePacket(self, port, packet):
        """TODO: process incoming packet"""
        if packet.isTraceroute():
            # Hints: this is a normal data packet
            # if the forwarding table contains packet.dstAddr
            #   send packet based on forwarding table, e.g., self.send(port, packet)
            if self.dis_vec[packet.dstAddr] < INF:
                self.send(self.forward_table[packet.dstAddr], packet)
        else:
            # Hints: this is a routing packet generated by your routing protocol
            # if the received distance vector is different
            #   update the local copy of the distance vector
            #   update the distance vector of this router
            #   update the forwarding table
            #   broadcast the distance vector of this router to neighbors
            neighbour = packet.srcAddr
            neighbour_dis_vec = loads(packet.content)
            poisoned_rev_table = {}
            for addr, dis in neighbour_dis_vec.items():
                new_dis = self.dis_vec[neighbour] + dis
                if self.dis_vec[addr] > new_dis:
                    self.dis_vec[addr] = new_dis
                    self.forward_table[addr] = self.forward_table[neighbour]
                    poisoned_rev_table[neighbour] = addr
            if poisoned_rev_table:
                self.broadcastDisVec(poisoned_rev_table)


    def handleNewLink(self, port, endpoint, cost):
        """TODO: handle new link"""
        # update the distance vector of this router
        # update the forwarding table
        # broadcast the distance vector of this router to neighbors
        self.neigbours[endpoint] = port
        if self.dis_vec[endpoint] > cost:
            self.dis_vec[endpoint] = cost
            self.forward_table[endpoint] = port
            self.broadcastDisVec({}) 


    def handleRemoveLink(self, port):
        """TODO: handle removed link"""
        # update the distance vector of this router
        # update the forwarding table
        # broadcast the distance vector of this router to neighbors
        for neighbour, port_num in self.neigbours.items():
            if port_num == port:
                self.neigbours[neighbour] = None
        for addr, port_num in self.forward_table.items():
            if port_num == port:
                self.forward_table[addr] = None
                self.dis_vec[addr] = INF
        self.broadcastDisVec({})


    def handleTime(self, timeMillisecs):
        """TODO: handle current time"""
        if timeMillisecs - self.last_time >= self.heartbeatTime:
            self.last_time = timeMillisecs
            # broadcast the distance vector of this router to neighbors
            self.broadcastDisVec({})


    def debugString(self):
        """TODO: generate a string for debugging in network visualizer"""
        return "router: addr {}".format(self.addr)
