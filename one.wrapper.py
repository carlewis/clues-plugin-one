#! /usr/bin/env python
#
# CLUES ONE Connector - ONE Connector for Cluster Energy Saving System
# Copyright (C) 2011 - GRyCAP - Universitat Politecnica de Valencia
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
import sys
import string
import xmlrpclib
import logging
from config import *
from oneconnect import *
import time

ONE_WRAPPER_LOG="/tmp/one.wrapper"

try:
	logging.basicConfig(level=logging.DEBUG,
		format='%(asctime)s %(levelname)-8s %(message)s',
		datefmt='%a, %d %b %Y %H:%M:%S',
		filename=ONE_WRAPPER_LOG,
		filemode='a')
except:
	logging.basicConfig(level=logging.DEBUG, filename=None)
	logging.error("could not create log file %s" % ONE_WRAPPER_LOG)

args = sys.argv[1:]
if len(args) != 1:
	logging.error("a virtual machine ID is expected")
	sys.exit(-1)
else:
	try:
		maq_id = int(args[0])
	except:
		logging.error("the virtual machine ID must be an integer value")
		sys.exit(-1)

	one = ONEConnect(ONE_XML_RPC)
	(result, val, string) = one.vm_hold(maq_id)

	if result == 0:
		(result, vm, txt) = one.vm_get(maq_id)
		if (result == 0):
			procs = max(vm.TEMPLATE.CPU, vm.TEMPLATE.VCPU)
			try:
				requirements = vm.TEMPLATE.REQUIREMENTS
				# when a value is not defined for a VM, the objects translate it into 0
				if requirements == 0:
					requirements = ""
			except:
				requirements = ""
			logging.info("asking for %f processors %s" % (float(procs), requirements))
			try:
				server = xmlrpclib.ServerProxy(GREEN_XML_RPC)
				server.new_job(ONE_PLUGIN_NAME, 1, False, "slots=%s;%s" % (procs, requirements))
			except Exception as e:
				logging.error("could not contact CLUES (%s)" % e)
		else:
			logging.error("could not obtain information for virtual machine (%s)" % txt)
		(result, val, string) = one.vm_release(maq_id)
		if result != 0:
			logging.error("error releasing virtual machine (%s)" % string)
	else:
		logging.error("error holding virtual machine (%s)" % string)
sys.exit(0)
