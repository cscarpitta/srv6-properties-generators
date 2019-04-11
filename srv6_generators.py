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

from ipaddress import IPv6Network, IPv4Network

from srv6_properties import *

RANGE_FOR_AREA_0="fd00::/8"

# Allocates loopbacks
class LoopbackAllocator(object):

  bit = 16
  net = unicode("fdff::/%d" % bit)
  prefix = 56

  def __init__(self): 
    print "*** Calculating Available Loopback Addresses"
    self.loopbacknet = (IPv6Network(self.net)).subnets(new_prefix=LoopbackAllocator.prefix)

  def nextLoopbackAddress(self):
    n_net = next(self.loopbacknet)
    n_host = next(n_net.hosts())
    return n_host.__str__()

# Allocates router ids
class RouterIdAllocator(object):

  bit = 0
  _id = unicode("0.0.0.0/%d" % bit)

  def __init__(self): 
    print "*** Calculating Available Router Ids"
    self.router_id = (IPv4Network(self._id)).hosts()

  def nextRouterId(self):
    n_id = next(self.router_id)
    return n_id.__str__()

# Allocates subnets for the links
class IPv6NetAllocator(object):

  bit = 16
  net = unicode("fdf0::/%s" % bit)
  prefix = 64
  
  def __init__(self):
    print "*** Calculating Available IP Networks"
    self.ipv6net = (IPv6Network(self.net)).subnets(new_prefix=IPv6NetAllocator.prefix)

  def nextNetAddress(self):
    n_net = next(self.ipv6net)
    return n_net

# Allocates subnets for the links
class IPv4NetAllocator(object):

  bit = 8
  net = unicode("10.0.0.0/%s" % bit)
  prefix = 16

  def __init__(self):
    print "*** Calculating Available IPv4 Networks"
    self.ipv4net = (IPv4Network(self.net)).subnets(new_prefix=IPv4NetAllocator.prefix)

  def nextNetAddress(self):
    n_net = next(self.ipv4net)
    return n_net

# Generator of
class PropertiesGenerator(object):

  def __init__(self):
    self.verbose = False
    self.loopbackAllocator = LoopbackAllocator()
    self.routerIdAllocator = RouterIdAllocator()
    self.ipv6NetAllocator = IPv6NetAllocator()
    self.ipv4NetAllocator = IPv4NetAllocator()
    self.allocated = 1

  # Generater for router properties
  def getRoutersProperties(self, nodes):
    output = []
    for node in nodes:
      if self.verbose == True:
        print node
      loopback = self.loopbackAllocator.nextLoopbackAddress()
      routerid = self.routerIdAllocator.nextRouterId()
      routerproperties = RouterProperties(loopback, routerid)
      if self.verbose == True:
        print routerproperties
      output.append(routerproperties)
    return output

  # Generator for link properties
  def getIPv6LinksProperties(self, links):
    output = []
    net = self.ipv6NetAllocator.nextNetAddress()

    if self.verbose == True:
      print net
    hosts = net.hosts()

    for link in links:
      if self.verbose == True:
        print "(%s,%s)" % (link[0], link[1])

      iplhs = next(hosts).__str__()
      iprhs = next(hosts).__str__()
      ospf6net = net.__str__()

      linkproperties = LinkProperties(iplhs, iprhs, ospf6net)
      if self.verbose == True:
        print linkproperties
      output.append(linkproperties)
    return output

  # Generator for link properties
  def getIPv4LinksProperties(self, links):
    output = []
    net = self.ipv4NetAllocator.nextNetAddress()

    if self.verbose == True:    
      print net
    hosts = net.hosts()

    for link in links:
      if self.verbose == True:    
        print "(%s,%s)" % (link[0], link[1])
        
      iplhs = next(hosts).__str__()
      iprhs = next(hosts).__str__()
      ospf6net = net.__str__()

      linkproperties = LinkProperties(iplhs, iprhs, ospf6net)
      if self.verbose == True:
        print linkproperties
      output.append(linkproperties)
    return output
