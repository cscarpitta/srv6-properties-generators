#!/usr/bin/python

##############################################################################################
# Copyright (C) 2018 Pier Luigi Ventre - (CNIT and University of Rome "Tor Vergata")
# Copyright (C) 2018 Stefano Salsano - (CNIT and University of Rome "Tor Vergata")
# www.uniroma2.it/netgroup - www.cnit.it
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Generators for Segment Routing IPv6
#
# @author Pier Luigi Ventre <pierventre@hotmail.com>
# @author Stefano Salsano <stefano.salsano@uniroma2.it>

from __future__ import print_function

from ipaddress import IPv6Network
from ipaddress import IPv4Network
from ipaddress import IPv6Interface
from ipaddress import IPv4Interface
from ipaddress import IPv4Address

from srv6_properties import RouterProperties
from srv6_properties import HostProperties
from srv6_properties import LinkProperties

RANGE_FOR_AREA_0=u"fc00::/8"

# Customer's networks: fd00::/8
# Operator’s networks and SIDs: fc00::/8

# fcff::/16 is the address space for router loopbacks,
# other addresses (SIDs) internal to the router,
# datacenters connected to the router

bit = 16
net = u"fcff::/%d" % bit


class SIDAllocator(object):

    # Address space for SIDs: fcff:xxxx:2:0/64
    # (e.g. fcff:xxxx:0002:0000:0000:0002:0000:tttt)
    # where 'xxxx' is the router id and tttt the vpn id

    prefix = 64

    def getSID(self, router_id, vpn_id):
        # Generate the SID
        prefix = int(IPv6Interface(net).ip)
        router_id = int(IPv4Address(router_id))
        sid = IPv6Network(prefix | router_id << 96 | 2 << 80 | vpn_id)
        # Remove /128 mask and convert to string
        sid = IPv6Interface(sid).ip.__str__()
        # Return the SID
        return sid

    def getSIDFamily(self, router_id):
        # Generate the SID
        prefix = int(IPv6Interface(net).ip)
        router_id = int(IPv4Address(router_id))
        sidFamily = IPv6Network(prefix | router_id << 96 | 2 << 80)
        # Append prefix /64
        sidFamily = sidFamily.supernet(new_prefix=SIDAllocator.prefix)
        # Convert to string
        sidFamily = IPv6Interface(sidFamily).__str__()
        # Return the SID
        return sidFamily


# Allocates loopbacks
class LoopbackAllocator(object):

  # Loopback address space for the router xxxx
  # fcff:xxxx:0:0::/64

  prefix = 64

  def getLoopbackAddress(self, router_index):
    # Generate the loopback address
    prefix = int(IPv6Interface(net).ip)
    loopbackip = IPv6Network(prefix | router_index << 96 | 1)
    # Remove /128 mask and convert to string
    loopbackip = IPv6Interface(loopbackip).ip.__str__()
    # Return the address
    return loopbackip.__str__()


# Allocates router networks
class RouterNetAllocator(object):

  # Each router exports a /32
  # fcff:xxxx::/32

  prefix = 32

  def getRouterNet(self, router_index):
      # Generate the router net
      prefix = int(IPv6Interface(net).ip)
      routernet = IPv6Network(prefix | router_index << 96)
      # Append prefix /32
      routernet = routernet.supernet(new_prefix=RouterNetAllocator.prefix)
      # Convert to string
      routernet = IPv6Interface(routernet).__str__()
      # Return the net
      return routernet


# Allocates router ids
class RouterIdAllocator(object):

  # Router IDs start from 0.0.0.1

  def getRouterId(self, router_index):
    # Generate the router id
    router_id = IPv4Address(router_index)
    # Return the address
    return router_id.__str__()


class IPv6NetAllocator(object):

    # fcf0::/16 address space for the links in the operators network

    # Link between router xxxx and yyyy
    # fcf0:0000:xxxx:yyyy::/64
    # The first two IPv6 addresses of the dataplane subnet
    #  are assigned to the two sides of the link
    # fcf0:0000:xxxx:yyyy::1/64 address of router xxxx
    # fcf0:0000:xxxx:yyyy::2/64 address of router yyyy

    bit = 16
    net = u"fcf0::/%s" % bit
    prefix = 64

    def getNet(self, l_router_index, r_router_index):
        # Generate the operator net
        prefix = int(IPv6Interface(IPv6NetAllocator.net).ip)
        operatorNet = IPv6Network(prefix | l_router_index << 80 | r_router_index << 64)
        # Append prefix to the net
        operatorNet = operatorNet.supernet(new_prefix=IPv6NetAllocator.prefix)
        # Return the net
        return operatorNet

    def getLRouterAddress(self, l_router_index, r_router_index):
        # Generate the left router address
        prefix = int(IPv6Interface(IPv6NetAllocator.net).ip)
        lRouterAddress = IPv6Network(prefix | l_router_index << 80 | r_router_index << 64 | 1)
        # Remove /128 mask from the address and convert to string
        lRouterAddress = IPv6Interface(lRouterAddress).ip.__str__()
        # Return the address
        return lRouterAddress

    def getRRouterAddress(self, l_router_index, r_router_index):
        # Generate the right router address
        prefix = int(IPv6Interface(IPv6NetAllocator.net).ip)
        rRouterAddress = IPv6Network(prefix | l_router_index << 80 | r_router_index << 64 | 2)
        # Remove /128 mask from the address and convert to string
        rRouterAddress = IPv6Interface(rRouterAddress).ip.__str__()
        # Return the address
        return rRouterAddress


class IPv4NetAllocator(object):

    # fcf0::/16 address space for the links in the operators network

    # Link between router xxxx and yyyy
    # fcf0:0000:xxxx:yyyy::/64
    # The first two IPv6 addresses of the dataplane subnet
    #  are assigned to the two sides of the link
    # fcf0:0000:xxxx:yyyy::1/64 address of router xxxx
    # fcf0:0000:xxxx:yyyy::2/64 address of router yyyy

    bit = 8
    net = u"11.0.0.0/%s" % bit
    prefix = 30

    def getNet(self, l_router_index, r_router_index):
        # Generate the operator net
        prefix = int(IPv4Interface(IPv4NetAllocator.net).ip)
        operatorNet = IPv4Network(prefix | l_router_index << 13 | r_router_index << 2)
        # Append prefix to the net
        operatorNet = operatorNet.supernet(new_prefix=IPv4NetAllocator.prefix)
        # Return the net
        return operatorNet

    def getLRouterAddress(self, l_router_index, r_router_index):
        # Generate the left router address
        prefix = int(IPv4Interface(IPv4NetAllocator.net).ip)
        lRouterAddress = IPv4Network(prefix | l_router_index << 13 | r_router_index << 2 | 1)
        # Remove /128 mask from the address and convert to string
        lRouterAddress = IPv4Interface(lRouterAddress).ip.__str__()
        # Return the address
        return lRouterAddress

    def getRRouterAddress(self, l_router_index, r_router_index):
        # Generate the right router address
        prefix = int(IPv4Interface(IPv4NetAllocator.net).ip)
        rRouterAddress = IPv4Network(prefix | l_router_index << 13 | r_router_index << 2 | 2)
        # Remove /128 mask from the address and convert to string
        rRouterAddress = IPv4Interface(rRouterAddress).ip.__str__()
        # Return the address
        return rRouterAddress


class IPv6CustomerFacingNetAllocator(object):

    # fcff:xxxx:3::/48 customer facing subnets

    # Link between router xxxx and host yyyy
    # fcff:xxxx:3:yy00:/56
    # The first two IPv6 addresses of the dataplane subnet
    #  are assigned to the two sides of the link
    # fcff:xxxx:3:yy00::1/64 address of router xxxx
    # fcff:xxxx:3:yy00::2/64 address of host yy

    bit = 48
    net = u"fcff::/%s" % bit
    prefix = 64

    def getNet(self, router_index, host_index):
        # Generate the operator net
        prefix = int(IPv6Interface(IPv6CustomerFacingNetAllocator.net).ip)
        operatorNet = IPv6Network(prefix | router_index << 96 | 3 << 80 | host_index << 64)
        # Append prefix to the net
        operatorNet = operatorNet.supernet(new_prefix=IPv6CustomerFacingNetAllocator.prefix)
        # Return the net
        return operatorNet

    def getRouterAddress(self, router_index, host_index):
        # Generate the router address
        prefix = int(IPv6Interface(IPv6CustomerFacingNetAllocator.net).ip)
        routerAddress = IPv6Network(prefix | router_index << 96 | 3 << 80 | host_index << 64 | 1)
        # Remove /128 mask from the address and convert to string
        routerAddress = IPv6Interface(routerAddress).ip.__str__()
        # Return the address
        return routerAddress

    def getHostAddress(self, router_index, host_index):
        # Generate the host address
        prefix = int(IPv6Interface(IPv6CustomerFacingNetAllocator.net).ip)
        hostAddress = IPv6Network(prefix | router_index << 96 | 3 << 80 | host_index << 64 | 2)
        # Remove /128 mask from the address and convert to string
        hostAddress = IPv6Interface(hostAddress).ip.__str__()
        # Return the address
        return hostAddress


class IPv4CustomerFacingNetAllocator(object):

    # fcff:xxxx:3::/48 customer facing subnets

    # Link between router xxxx and host yyyy
    # fcff:xxxx:3:yy00:/56
    # The first two IPv6 addresses of the dataplane subnet
    #  are assigned to the two sides of the link
    # fcff:xxxx:3:yy00::1/64 address of router xxxx
    # fcff:xxxx:3:yy00::2/64 address of host yy

    bit = 16
    net = u"192.168.0.0/%s" % bit
    prefix = 24

    def getNet(self, router_index, host_index):
        # Generate the operator net
        prefix = int(IPv4Interface(IPv4CustomerFacingNetAllocator.net).ip)
        operatorNet = IPv4Network(prefix | router_index << 9 | host_index << 2)
        # Append prefix to the net
        operatorNet = operatorNet.supernet(new_prefix=IPv4CustomerFacingNetAllocator.prefix)
        # Return the net
        return operatorNet

    def getRouterAddress(self, router_index, host_index):
        # Generate the router address
        prefix = int(IPv4Interface(IPv4CustomerFacingNetAllocator.net).ip)
        routerAddress = IPv4Network(prefix | router_index << 9 | host_index << 2 | 1)
        # Remove /128 mask from the address and convert to string
        routerAddress = IPv4Interface(routerAddress).ip.__str__()
        # Return the address
        return routerAddress

    def getHostAddress(self, router_index, host_index):
        # Generate the host address
        prefix = int(IPv4Interface(IPv4CustomerFacingNetAllocator.net).ip)
        hostAddress = IPv4Network(prefix | router_index << 9 | host_index << 2 | 2)
        # Remove /128 mask from the address and convert to string
        hostAddress = IPv4Interface(hostAddress).ip.__str__()
        # Return the address
        return hostAddress


class IPv6AccessNetAllocator(object):

    # fcff:xxxx:3::/48 customer facing subnets

    # Link between router xxxx and host yyyy
    # fcff:xxxx:3:yy00:/56
    # The first two IPv6 addresses of the dataplane subnet
    #  are assigned to the two sides of the link
    # fcff:xxxx:3:yy00::1/64 address of router xxxx
    # fcff:xxxx:3:yy00::2/64 address of host yy

    bit = 48
    net = u"fcfb::/%s" % bit
    prefix = 64

    def getNet(self, router_index, host_index):
        # Generate the operator net
        prefix = int(IPv6Interface(IPv6AccessNetAllocator.net).ip)
        operatorNet = IPv6Network(prefix | router_index << 96 | 3 << 80 | host_index << 64)
        # Append prefix to the net
        operatorNet = operatorNet.supernet(new_prefix=IPv6AccessNetAllocator.prefix)
        # Return the net
        return operatorNet

    def getRouterAddress(self, router_index, host_index):
        # Generate the router address
        prefix = int(IPv6Interface(IPv6AccessNetAllocator.net).ip)
        routerAddress = IPv6Network(prefix | router_index << 96 | 3 << 80 | host_index << 64 | 1)
        # Remove /128 mask from the address and convert to string
        routerAddress = IPv6Interface(routerAddress).ip.__str__()
        # Return the address
        return routerAddress

    def getHostAddress(self, router_index, host_index):
        # Generate the host address
        prefix = int(IPv6Interface(IPv6AccessNetAllocator.net).ip)
        hostAddress = IPv6Network(prefix | router_index << 96 | 3 << 80 | host_index << 64 | 2)
        # Remove /128 mask from the address and convert to string
        hostAddress = IPv6Interface(hostAddress).ip.__str__()
        # Return the address
        return hostAddress


class IPv4AccessNetAllocator(object):

    # fcff:xxxx:3::/48 customer facing subnets

    # Link between router xxxx and host yyyy
    # fcff:xxxx:3:yy00:/56
    # The first two IPv6 addresses of the dataplane subnet
    #  are assigned to the two sides of the link
    # fcff:xxxx:3:yy00::1/64 address of router xxxx
    # fcff:xxxx:3:yy00::2/64 address of host yy

    bit = 16
    net = u"10.0.0.0/%s" % bit
    prefix = 30

    def getNet(self, router_index, host_index):
        # Generate the operator net
        prefix = int(IPv4Interface(IPv4AccessNetAllocator.net).ip)
        operatorNet = IPv4Network(prefix | router_index << 9 | host_index << 2)
        # Append prefix to the net
        operatorNet = operatorNet.supernet(new_prefix=IPv4AccessNetAllocator.prefix)
        # Return the net
        return operatorNet

    def getRouterAddress(self, router_index, host_index):
        # Generate the router address
        prefix = int(IPv4Interface(IPv4AccessNetAllocator.net).ip)
        routerAddress = IPv4Network(prefix | router_index << 9 | host_index << 2 | 1)
        # Remove /128 mask from the address and convert to string
        routerAddress = IPv4Interface(routerAddress).ip.__str__()
        # Return the address
        return routerAddress

    def getHostAddress(self, router_index, host_index):
        # Generate the host address
        prefix = int(IPv4Interface(IPv4AccessNetAllocator.net).ip)
        hostAddress = IPv4Network(prefix | router_index << 9 | host_index << 2 | 2)
        # Remove /128 mask from the address and convert to string
        hostAddress = IPv4Interface(hostAddress).ip.__str__()
        # Return the address
        return hostAddress


class IPv6CustomerNetAllocator(object):

  # fd00::/8 customers’ networks
  # e.g. fd00:x:y::/48 is a network
  # connecting host y for the customer VPN x
  # fd00:x:y::1 address of the PE router
  # fd00:x:y::2 address of the host

    bit = 8
    net = u"fd00::/%s" % bit
    prefix = 48

    def getNet(self, vpn_id, host_id):
        # Generate the customer net
        prefix = int(IPv6Interface(IPv6CustomerNetAllocator.net).ip)
        customerNet = IPv6Network(prefix | vpn_id << 96 | host_id << 80)
        # Append prefix to the net
        customerNet = customerNet.supernet(new_prefix=IPv6CustomerNetAllocator.prefix)
        # Return the net
        return customerNet

    def getRouterAddress(self, vpn_id, host_id):
        # Generate the router address
        prefix = int(IPv6Interface(IPv6CustomerNetAllocator.net).ip)
        routerAddress = IPv6Network(prefix | vpn_id << 96 | host_id << 80 | 1)
        # Remove /128 mask from the address and convert to string
        routerAddress = IPv6Interface(routerAddress).ip.__str__()
        #routerAddress = "%s/%s" % (routerAddress, IPv6CustomerNetAllocator.prefix)
        # Return the address
        return routerAddress

    def getHostAddress(self, vpn_id, host_id):
        # Generate the host address
        prefix = int(IPv6Interface(IPv6CustomerNetAllocator.net).ip)
        hostAddress = IPv6Network(prefix | vpn_id << 96 | host_id << 80 | 2)
        # Remove /128 mask from the address and convert to string
        hostAddress = IPv6Interface(hostAddress).ip.__str__()
        #hostAddress = "%s/%s" % (hostAddress, IPv6CustomerNetAllocator.prefix)
        # Return the address
        return hostAddress


class IPv4CustomerNetAllocator(object):

    # 10.0.0.0/8 customers’ networks
    # e.g. 10.x.y.0/24 is a network
    # connecting host y for the customer VPN x
    # 10.x.y.1 address of the PE router
    # 10.x.y.2 address of the host

    bit = 8
    net = u"10.0.0.0/%s" % bit
    prefix = 30

    def getNet(self, vpn_id, host_id):
        # Generate the customer net
        prefix = int(IPv4Interface(IPv4CustomerNetAllocator.net).ip)
        customerNet = IPv4Network(prefix | vpn_id << 16 | host_id << 8)
        # Append prefix to the net
        customerNet = customerNet.supernet(new_prefix=IPv4CustomerNetAllocator.prefix)
        # Return the net
        return customerNet

    def getRouterAddress(self, vpn_id, host_id):
        # Generate the router address
        prefix = int(IPv4Interface(IPv4CustomerNetAllocator.net).ip)
        routerAddress = IPv4Network(prefix | vpn_id << 16 | host_id << 8 | 1)
        # Remove /128 mask from the address and convert to string
        routerAddress = IPv4Interface(routerAddress).ip.__str__()
        # Return the address
        return routerAddress

    def getHostAddress(self, vpn_id, host_id):
        # Generate the host address
        prefix = int(IPv4Interface(IPv4CustomerNetAllocator.net).ip)
        hostAddress = IPv4Network(prefix | vpn_id << 16 | host_id << 8 | 2)
        # Remove /128 mask from the address and convert to string
        hostAddress = IPv4Interface(hostAddress).ip.__str__()
        # Return the address
        return hostAddress


# Allocates mgmt address
class IPv6MgmtAllocator(object):

    bit = 16
    net = u"2000::/%d" % bit
    prefix = 64

    def getNet(self, controller_index, router_index):
        # Generate the customer net
        prefix = int(IPv4Interface(IPv6MgmtAllocator.net).ip)
        customerNet = IPv4Network(prefix | controller_index << 80 | router_index << 64)
        # Append prefix to the net
        customerNet = customerNet.supernet(new_prefix=IPv6MgmtAllocator.prefix)
        # Return the net
        return customerNet

    def getControllerAddress(self, controller_index, router_index):
        # Generate the host address
        prefix = int(IPv4Interface(IPv6MgmtAllocator.net).ip)
        hostAddress = IPv4Network(prefix | controller_index << 80 | router_index << 64 | 2)
        # Remove /128 mask from the address and convert to string
        hostAddress = IPv4Interface(hostAddress).ip.__str__()
        # Return the address
        return hostAddress

    def getRouterAddress(self, controller_index, router_index):
        # Generate the router address
        prefix = int(IPv4Interface(IPv6MgmtAllocator.net).ip)
        routerAddress = IPv4Network(prefix | controller_index << 80 | router_index << 64 | 1)
        # Remove /128 mask from the address and convert to string
        routerAddress = IPv4Interface(routerAddress).ip.__str__()
        # Return the address
        return routerAddress


# Allocates mgmt address
class IPv4MgmtAllocator(object):

    bit = 12
    net = u"172.0.0.0/%d" % bit
    prefix = 30

    def getNet(self, controller_index, router_index):
        # Generate the customer net
        prefix = int(IPv4Interface(IPv4MgmtAllocator.net).ip)
        customerNet = IPv4Network(prefix | controller_index << 11 | router_index << 2)
        # Append prefix to the net
        customerNet = customerNet.supernet(new_prefix=IPv4MgmtAllocator.prefix)
        # Return the net
        return customerNet

    def getControllerAddress(self, controller_index, router_index):
        # Generate the host address
        prefix = int(IPv4Interface(IPv4MgmtAllocator.net).ip)
        hostAddress = IPv4Network(prefix | controller_index << 11 | router_index << 2 | 1)
        # Remove /128 mask from the address and convert to string
        hostAddress = IPv4Interface(hostAddress).ip.__str__()
        # Return the address
        return hostAddress

    def getRouterAddress(self, controller_index, router_index):
        # Generate the router address
        prefix = int(IPv4Interface(IPv4MgmtAllocator.net).ip)
        routerAddress = IPv4Network(prefix | controller_index << 11 | router_index << 2 | 2)
        # Remove /128 mask from the address and convert to string
        routerAddress = IPv4Interface(routerAddress).ip.__str__()
        # Return the address
        return routerAddress


# Generator of
class IPv6PropertiesGenerator(object):

  def __init__(self):
    self.verbose = False
    self.index = 0
    self.loopbackAllocator = LoopbackAllocator()
    self.routerIdAllocator = RouterIdAllocator()
    self.netAllocator = IPv6NetAllocator()
    self.customerFacingNetAllocator = IPv6CustomerFacingNetAllocator()
    self.accessNetAllocator = IPv6AccessNetAllocator()
    self.routerNetAllocator = RouterNetAllocator()
    self.mgmtNetAllocator = IPv6MgmtAllocator()
    self.node_to_index = dict()
    self.allocated = 1

  # Generater for router properties
  def getRoutersProperties(self, nodes):
    output = []
    for node in nodes:
      if self.verbose == True:
        print(node)
      self.index += 1
      loopback = self.loopbackAllocator.getLoopbackAddress(self.index)
      routerid = self.routerIdAllocator.getRouterId(self.index)
      routernet = self.routerNetAllocator.getRouterNet(self.index)
      mgmtip = None
      #mgmtip = self.mgmtNetAllocator.getMgmtAddress(self.index)
      routerproperties = RouterProperties(loopback, routerid, routernet, mgmtip, self.index)
      self.node_to_index[node] = self.index
      if self.verbose == True:
        print(routerproperties)
      output.append(routerproperties)
    return output

  # Generater for router properties
  def getHostsProperties(self, nodes):
    output = []
    for node in nodes:
      if self.verbose == True:
        print(node)
      self.index += 1
      loopback = self.loopbackAllocator.getLoopbackAddress(self.index)
      mgmtip = None
      #mgmtip = self.mgmtNetAllocator.getMgmtAddress(self.index)
      hostproperties = HostProperties(loopback, mgmtip, self.index)
      self.node_to_index[node] = self.index
      if self.verbose == True:
        print(hostproperties)
      output.append(hostproperties)
    return output

  # Generator for link properties
  def getCoreLinksProperties(self, links):
    output = []

    if self.verbose == True:
      print(net)

    for link in links:
      if self.verbose == True:
        print("(%s,%s)" % (link[0], link[1]))

      _lrouter = self.node_to_index[link[0]]
      _rrouter = self.node_to_index[link[1]]

      _net = self.netAllocator.getNet(_lrouter, _rrouter)
      l_router = self.netAllocator.getLRouterAddress(_lrouter, _rrouter)
      r_router = self.netAllocator.getRRouterAddress(_lrouter, _rrouter)

      iplhs = l_router.__str__()
      iprhs = r_router.__str__()
      ospf6net = _net.__str__()

      linkproperties = LinkProperties(iplhs, iprhs, ospf6net, self.netAllocator.prefix)
      if self.verbose == True:
        print(linkproperties)
      output.append(linkproperties)
    return output

  # Generator for link properties
  def getEdgeLinksProperties(self, links):
    output = []

    if self.verbose == True:
      print(net)

    for link in links:
      if self.verbose == True:
        print("(%s,%s)" % (link[0], link[1]))

      _lnode = self.node_to_index.get(link[0])
      _rnode = self.node_to_index.get(link[1])
      _net = self.customerFacingNetAllocator.getNet(_lnode, _rnode)
      l_node = self.customerFacingNetAllocator.getRouterAddress(_lnode, _rnode)
      r_node = self.customerFacingNetAllocator.getHostAddress(_lnode, _rnode)

      iplhs = l_node.__str__()
      iprhs = r_node.__str__()
      ospf6net = _net.__str__()

      linkproperties = LinkProperties(iplhs, iprhs, ospf6net, self.customerFacingNetAllocator.prefix)
      if self.verbose == True:
        print(linkproperties)
      output.append(linkproperties)
    return output

  # Generator for link properties
  def getAccessLinksProperties(self, links):
    output = []

    for link in links:
      if self.verbose == True:
        print("(%s,%s)" % (link[0], link[1]))

      _lnode = self.node_to_index.get(link[0])
      _rnode = self.node_to_index.get(link[1])
      _net = self.accessNetAllocator.getNet(_lnode, _rnode)
      l_node = self.accessNetAllocator.getRouterAddress(_lnode, _rnode)
      r_node = self.accessNetAllocator.getHostAddress(_lnode, _rnode)

      iplhs = l_node.__str__()
      iprhs = r_node.__str__()
      net = _net.__str__()

      linkproperties = LinkProperties(iplhs, iprhs, net, self.accessNetAllocator.prefix)
      if self.verbose == True:
        print(linkproperties)
      output.append(linkproperties)
    return output

  # Generator for link properties
  def getMgmtLinksProperties(self, links):
    output = []

    for link in links:
      if self.verbose == True:
        print("(%s,%s)" % (link[0], link[1]))

      _lnode = self.node_to_index.get(link[0])
      _rnode = self.node_to_index.get(link[1])
      _net = self.mgmtNetAllocator.getNet(_lnode, _rnode)
      l_node = self.mgmtNetAllocator.getControllerAddress(_lnode, _rnode)
      r_node = self.mgmtNetAllocator.getRouterAddress(_lnode, _rnode)

      iplhs = l_node.__str__()
      iprhs = r_node.__str__()
      net = _net.__str__()

      linkproperties = LinkProperties(iplhs, iprhs, net, self.mgmtNetAllocator.prefix)
      if self.verbose == True:
        print(linkproperties)
      output.append(linkproperties)
    return output

  '''
  # Generator for mgmt station address
  def nextMgmtAddress(self):
    self.index += 1
    mgmtip = self.mgmtAllocator.getMgmtAddress(self.index)
    return mgmtip
  '''


# Generator of
class IPv4PropertiesGenerator(object):

  def __init__(self):
    self.verbose = False
    self.index = 0
    self.routerIdAllocator = RouterIdAllocator()
    self.netAllocator = IPv4NetAllocator()
    self.customerFacingNetAllocator = IPv4CustomerFacingNetAllocator()
    self.accessNetAllocator = IPv4AccessNetAllocator()
    self.mgmtNetAllocator = IPv4MgmtAllocator()
    self.node_to_index = dict()
    self.allocated = 1

  # Generater for router properties
  def getRoutersProperties(self, nodes):
    output = []
    for node in nodes:
      if self.verbose == True:
        print(node)
      self.index += 1
      loopback = None
      routerid = self.routerIdAllocator.getRouterId(self.index)
      routernet = None
      mgmtip = None
      #mgmtip = self.mgmtAllocator.getMgmtAddress(self.index)
      routerproperties = RouterProperties(loopback, routerid, routernet, mgmtip, self.index)
      self.node_to_index[node] = self.index
      if self.verbose == True:
        print(routerproperties)
      output.append(routerproperties)
    return output

  # Generater for router properties
  def getHostsProperties(self, nodes):
    output = []
    for node in nodes:
      if self.verbose == True:
        print(node)
      self.index += 1
      loopback = None
      mgmtip = None
      #mgmtip = self.mgmtAllocator.getMgmtAddress(self.index)
      hostproperties = HostProperties(loopback, mgmtip, self.index)
      self.node_to_index[node] = self.index
      if self.verbose == True:
        print(hostproperties)
      output.append(hostproperties)
    return output

  # Generator for link properties
  def getCoreLinksProperties(self, links):
    output = []

    for link in links:
      if self.verbose == True:
        print("(%s,%s)" % (link[0], link[1]))

      _lrouter = self.node_to_index[link[0]]
      _rrouter = self.node_to_index[link[1]]

      _net = self.netAllocator.getNet(_lrouter, _rrouter)
      l_router = self.netAllocator.getLRouterAddress(_lrouter, _rrouter)
      r_router = self.netAllocator.getRRouterAddress(_lrouter, _rrouter)

      iplhs = l_router.__str__()
      iprhs = r_router.__str__()
      net = _net.__str__()

      linkproperties = LinkProperties(iplhs, iprhs, net, self.netAllocator.prefix)
      if self.verbose == True:
        print(linkproperties)
      output.append(linkproperties)
    return output

  # Generator for link properties
  def getEdgeLinksProperties(self, links):
    output = []

    for link in links:
      if self.verbose == True:
        print("(%s,%s)" % (link[0], link[1]))

      _lnode = self.node_to_index.get(link[0])
      _rnode = self.node_to_index.get(link[1])
      _net = self.customerFacingNetAllocator.getNet(_lnode, _rnode)
      l_node = self.customerFacingNetAllocator.getRouterAddress(_lnode, _rnode)
      r_node = self.customerFacingNetAllocator.getHostAddress(_lnode, _rnode)

      iplhs = l_node.__str__()
      iprhs = r_node.__str__()
      net = _net.__str__()

      linkproperties = LinkProperties(iplhs, iprhs, net, self.customerFacingNetAllocator.prefix)
      if self.verbose == True:
        print(linkproperties)
      output.append(linkproperties)
    return output

  # Generator for link properties
  def getAccessLinksProperties(self, links):
    output = []

    for link in links:
      if self.verbose == True:
        print("(%s,%s)" % (link[0], link[1]))

      _lnode = self.node_to_index.get(link[0])
      _rnode = self.node_to_index.get(link[1])
      _net = self.accessNetAllocator.getNet(_lnode, _rnode)
      l_node = self.accessNetAllocator.getRouterAddress(_lnode, _rnode)
      r_node = self.accessNetAllocator.getHostAddress(_lnode, _rnode)

      iplhs = l_node.__str__()
      iprhs = r_node.__str__()
      net = _net.__str__()

      linkproperties = LinkProperties(iplhs, iprhs, net, self.accessNetAllocator.prefix)
      if self.verbose == True:
        print(linkproperties)
      output.append(linkproperties)
    return output

  # Generator for link properties
  def getMgmtLinksProperties(self, links):
    output = []

    for link in links:
      if self.verbose == True:
        print("(%s,%s)" % (link[0], link[1]))

      _lnode = self.node_to_index.get(link[0])
      _rnode = self.node_to_index.get(link[1])
      _net = self.mgmtNetAllocator.getNet(_lnode, _rnode)
      l_node = self.mgmtNetAllocator.getControllerAddress(_lnode, _rnode)
      r_node = self.mgmtNetAllocator.getRouterAddress(_lnode, _rnode)

      iplhs = l_node.__str__()
      iprhs = r_node.__str__()
      net = _net.__str__()

      linkproperties = LinkProperties(iplhs, iprhs, net, self.mgmtNetAllocator.prefix)
      if self.verbose == True:
        print(linkproperties)
      output.append(linkproperties)
    return output
  
  '''
  # Generator for mgmt station address
  def nextMgmtAddress(self):
    self.index += 1
    mgmtip = self.mgmtAllocator.getMgmtAddress(self.index)
    return mgmtip
  '''