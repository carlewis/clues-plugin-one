#!/usr/bin/python
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
import xml.dom.minidom
import logging

class XMLObject:
	tuples = {}
	tuples_lists = {}
	values = []
	values_lists = []
	numeric = []
	noneval = None

	@staticmethod
	def getText(nodelist):
		rc = []
		for node in nodelist:
			if node.nodeType == node.TEXT_NODE or node.nodeType == node.CDATA_SECTION_NODE:
				rc.append(node.data)
		return ''.join(rc)

	@staticmethod
	def handleField(fieldName, VM):
		try:
			fieldElements = VM.getElementsByTagName(fieldName)[0]
			return XMLObject.getText(fieldElements.childNodes)
		except:
			return None

	@staticmethod
	def handleFieldAsList(fieldName, VM):
		try:
			fieldElements = VM.getElementsByTagName(fieldName)
			local_list = []
			for fieldElement in fieldElements:
				local_list.append(XMLObject.getText(fieldElement.childNodes))
			return local_list
		except:
			return []

	def __setattr__(self, name, value):
		self.__dict__[name] = value

	def __init__(self, xml_str):
		dom = xml.dom.minidom.parseString(xml_str)

		for tag, className in self.__class__.tuples.items():
			objs = dom.getElementsByTagName(tag)
			if (len(objs) > 0):
				newObj = className(objs[0].toxml())
				dom.childNodes[0].removeChild(objs[0])
			else:
				newObj = None
			self.__setattr__(tag, newObj)

		for tag, className in self.__class__.tuples_lists.items():
			objs = dom.getElementsByTagName(tag)
			obj_list = []
			for obj in objs:
				newObj = className(obj.toxml())
				dom.childNodes[0].removeChild(obj)
				obj_list.append(newObj)
			self.__setattr__(tag, obj_list)

		for tag in self.__class__.values_lists:
			self.__setattr__(tag, XMLObject.handleFieldAsList(tag, dom))

		for tag in self.__class__.values:
			value = XMLObject.handleField(tag, dom)
			if (value is None):
				value = self.noneval
			if (tag in self.__class__.numeric):
				try:
					value = float(value)
					if (value == int(value)):
						value = int(value)	
				except:
					logging.warning("numeric value expected for %s - found %s" % (tag, value))
			self.__setattr__(tag, value)
