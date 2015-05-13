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
import xmlrpclib
import hashlib
import getpass
import xml.dom.minidom
from xmlobject import XMLObject
import os
import config
import logging

def get_auth_string(filename = None, version = ""):
	if filename is None:
		auth_file = os.getenv("ONE_AUTH")
		if (auth_file == None):
			auth_file = os.path.expanduser("~/.one/one_auth")
	else:
		auth_file = filename

	if (auth_file == None):
		return None

	try:
		one_auth_file = open(auth_file, "r")
		auth_line = one_auth_file.readline()
		(user,sep,passw) = auth_line.partition(":")
		if version == "3.2":
			auth_string = user + ":" + passw.strip()
		else:
			auth_string = user + ":" + hashlib.sha1(passw.strip()).hexdigest()
		one_auth_file.close()
		return auth_string
	except:
		return None

class NIC(XMLObject):
	values = ['BRIDGE', 'IP', 'MAC', 'NETWORK', 'VNID']

class OS(XMLObject):
	values = ['BOOT', 'ROOT']

class GRAPHICS(XMLObject):
	values = ['LISTEN', 'TYPE']

class DISK(XMLObject):
	values = ['CLONE','READONLY','SAVE','SOURCE','TARGET' ]

class TEMPLATE(XMLObject):
	values = [ 'CPU', 'MEMORY', 'NAME', 'RANK', 'REQUIREMENTS', 'VMID', 'VCPU' ]
	tuples = { 'DISK': DISK, 'GRAPHICS': GRAPHICS, 'NIC': NIC, 'OS': OS }
	numeric = [ 'CPU', 'MEMORY', 'VCPU' ]
	noneval = 0

class HISTORY(XMLObject):
	values = ['SEQ', 'HOSTNAME', 'HID', 'STIME', 'ETIME', 'PSTIME', 'PETIME', 'RSTIME', 'RETIME' ,'ESTIME', 'EETIME', 'REASON' ]

class VM(XMLObject):
	STATE_INIT=0
	STATE_PENDING=1
	STATE_HOLD=2
	STATE_ACTIVE=3
	STATE_STOPPED=4
	STATE_SUSPENDED=5
	STATE_DONE=6
	STATE_FAILED=7
	STATE_STR = {'0': 'init', '1': 'pending', '2': 'hold', '3': 'active', '4': 'stopped', '5': 'suspended', '6': 'done', '7': 'failed' }
	LCM_STATE_STR={'0':'init','1':'prologing','2':'booting','3':'running','4':'migrating','5':'saving (stop)','6':'saving (suspend)','7':'saving (migrate)', '8':'prologing (migration)', '9':'prologing (resume)', '10': 'epilog (stop)','11':'epilog', '12':'cancel','13':'failure','14':'delete','15':'unknown'}
	values = [ 'ID','UID','NAME','LAST_POLL','STATE','LCM_STATE','STIME','ETIME','DEPLOY_ID','MEMORY','CPU','NET_TX','NET_RX' ]
	tuples = { 'TEMPLATE': TEMPLATE, 'HISTORY_RECORDS': HISTORY, 'HISTORY': HISTORY }
	numeric = [ 'ID', 'UID', 'STATE', 'LCM_STATE' ]

class VM_POOL(XMLObject):
	tuples_lists = { 'VM' : VM }

class HOST_TEMPLATE(XMLObject):
	values = [ 'ARCH', 'CPUSPEED','FREECPU','FREEMEMORY','HOSTNAME','HYPERVISOR','MODELNAME','NETRX','NETTX','TOTALCPU','TOTALMEMORY','USEDCPU','USEDMEMORY' ]
	numeric = [ 'FREECPU', 'FREEMEMORY', 'TOTALCPU', 'TOTALMEMORY', 'USEDMEMORY', 'USEDCPU' ]
	noneval = 0

class HOST_SHARE(XMLObject):
	values = [ 'HID', 'DISK_USAGE', 'MEM_USAGE', 'CPU_USAGE', 'MAX_DISK', 'MAX_MEM', 'MAX_CPU', 'FREE_DISK', 'FREE_MEM', 'FREE_CPU', 'USED_DISK', 'USED_MEM', 'USED_CPU', 'RUNNING_VMS', 'HYPERVISOR' ]
	numeric = [ 'HID', 'DISK_USAGE', 'MEM_USAGE', 'CPU_USAGE', 'MAX_DISK', 'MAX_MEM', 'MAX_CPU', 'FREE_DISK', 'FREE_MEM', 'FREE_CPU', 'USED_DISK', 'USED_MEM', 'USED_CPU', 'RUNNING_VMS' ]

class HOST(XMLObject):
	STATE_INIT = 0
	STATE_MONITORING = 1
	STATE_MONITORED = 2
	STATE_ERROR = 3
	STATE_DISABLED = 4
	values = [ 'ID', 'NAME', 'STATE', 'IM_MAD', 'VM_MAD', 'TM_MAD', 'LAST_MON_TIME' ]
	tuples = { 'HOST_SHARE': HOST_SHARE, 'TEMPLATE' : HOST_TEMPLATE }
	numeric = [ 'ID', 'STATE' ]

class HOST_POOL(XMLObject):
	tuples_lists = { 'HOST': HOST }

class OP:
	HOLD = "hold"
	RELEASE = "release"
	KILL = "finalize"
	avail = [HOLD, RELEASE, KILL]

class ONEConnect:
	serverStr = ""
	server = None
	auth_string = ""
	def __init__(self, serverStr, auth_string = None):
		self.serverStr = serverStr
		self.auth_string = ""
		self._version = ""
		if self.get_server_ref():
			if auth_string is None:
				self.auth_string = get_auth_string(config.ONE_AUTH_FILENAME, self._version)
			else:
				self.auth_string = auth_string
			if self.auth_string is None:
				self.auth_string = ""
				logging.error("could not open AUTH_FILE")
		else:
			logging.error("could not connect to ONE server")

	def get_hosts_full_info(self, hids):
		hosts = []
		for hid in hids:
			(result, host, _) = self.get_host(hid)
			if (result == 0):
				hosts.append(host)
		return hosts

	def get_host(self, hid):
		if (not self.get_server_ref()):
			return (1, None, "not connected to server")

		call_res = self.server.one.host.info(self.auth_string, hid)
		result = call_res[0]
		host = call_res[1]

		if not result:
			return (2, None, "operation error " + host)
		return (0, HOST(host), host)

	def get_hosts(self):
		if (not self.get_server_ref()):
			return (1, None, "not connected to server")

		call_res = self.server.one.hostpool.info(self.auth_string)
		result = call_res[0]
		hosts = call_res[1]
		
		if not result:
			return (2, None, "operation error " + hosts)
		return (0, HOST_POOL(hosts), hosts)

	def get_machine_list(self):
		if (not self.get_server_ref()):
			return (1, None, "not connected to server")

		if self._version == "2":
			call_res = self.server.one.vmpool.info(self.auth_string, -2)
		else:
			call_res = self.server.one.vmpool.info(self.auth_string, -2, -1, -1, -1)
			
		result = call_res[0]
		machines = call_res[1]

		if not result:
			return (2, None, "operation error " + machines)

		return (0, VM_POOL(machines), machines)

	def get_server_ref(self):
		if (self.server is not None):
			return True
		try:
			self.server = xmlrpclib.ServerProxy(self.serverStr)
			self._version = "2"
			methods = self.server.system.listMethods()
			
			# Trying to 
			if "one.acl.info" in methods:
				self._version = "3.0"
				if "one.vm.chmod" in methods:
					self._version = "3.2"
			logging.debug("OpenNebula version: " + self._version)
			return True
		except:
			self.server = None
			self._version = None
			return False

	def vm_deploy(self, id_vm, id_host):
		if (not self.get_server_ref()):
			return (1, None, "not connected to server")
		
		call_res = self.server.one.vm.deploy(self.auth_string, id_vm, id_host)
		result = call_res[0]
		
		if not result:
			return (2, None, "operation error")
			
		return (0, "", "")

	def vm_get(self, id_vm):
		if (not self.get_server_ref()):
			return (1, None, "not connected to server")
		
		call_res = self.server.one.vm.info(self.auth_string, id_vm)
		result = call_res[0]
		vm_info = call_res[1]
		
		if not result:
			return (2, None, "operation error")
		
		return (0, VM(vm_info), vm_info)

	def vm_start(self, templatePath):
		if (not self.get_server_ref()):
			return (1, None, "not connected to server")
		try:
			template = open(templatePath,'r').read()
		except:
			return (3, None, "cannot use template")
		
		call_res = self.server.one.vm.allocate(self.auth_string, template)
		result = call_res[0]
		id_vm = call_res[1]
		
		if not result:
			return (2, None, "operation error")

		return self.vm_get(id_vm)

	def vm_operate(self, id_vm, operation = ""):
		if (not self.get_server_ref()):
			return (1, None, "not connected to server")
		if operation in OP.avail:
			call_res = self.server.one.vm.action(self.auth_string, operation, id_vm)
			result = call_res[0]
			
			if not result:
				return (2, None, "operation error")
			return (0, None, "")
		else:
			return (1, None, "operation not available (%s)" % operation)

	def vm_hold(self, id_vm):
		return self.vm_operate(id_vm, OP.HOLD)
	def vm_release(self, id_vm):
		return self.vm_operate(id_vm, OP.RELEASE)
	def vm_kill(self, id_vm):
		return self.vm_operate(id_vm, OP.KILL)
