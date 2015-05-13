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

# Contact string for the XML-RPC CLUES interface
GREEN_XML_RPC="http://localhost:8000/RPC2"

# Name of this plugin whithin CLUES environment
ONE_PLUGIN_NAME="one"

# OpenNebula credentials (it needs permission for holding and releasing machines)
ONE_AUTH_FILENAME="/usr/local/clues/plugins/one/one_auth"

# Contact string for the XML-RPC ONE interface
ONE_XML_RPC="http://localhost:2633/RPC2"

# Log file for the wrapper
ONE_WRAPPER_LOG="/usr/local/clues/log/one.wrapper.log"

# Database file that will store the state of the ONE hosts
ONE_HOST_STATUS_DB = "/usr/local/clues/plugins/one/one.nodestate.db"
