#!/usr/bin/env python
# coding: utf-8
# Authors: Matt Harlos, Paul Vilevac
# Last Updated: 2019-01-12

import os, settings, re, time, threading, psutil
import pandas as pd
import numpy as np
from dataConfig import catList
from dataConfig import importantPorts
from progress.bar import Bar
from NIKEutil.logger import logger
from os import path
from datetime import datetime


class nikeVMsplitter:
	def __init__(self):
		self.DATA_PATH = os.getenv("data_path")
		logger.log("Initiating model with data path: {0}".format(self.DATA_PATH))

	def saveToCSV(self, file_path, file_name, dataFrame):
		outputFile = os.path.join(file_path,file_name)
		dataFrame.to_csv(outputFile)
		logger.log("Data frame was saved as csv to {0}".format(outputFile))

	def loadDataForSplitting(self):
		startTime = datetime.now()
		final_parquet = os.path.join(self.DATA_PATH,"final_results.parquet")
		final_csv = os.path.join(self.DATA_PATH,"final_results.csv")
		logger.log("Starting data load")
		if path.isfile(final_parquet):
			self.df = pd.read_parquet(final_parquet)
			logger.log("Loading our parquet data took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))
		elif path.isfile(final_csv):
			self.df = pd.read_csv(final_csv)
			logger.log("Loading our csv data took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))
		else:
			logger.log("Could not load data, neither {0} nor {1} was found".format(final_parquet,final_csv))

	def runSplitter(self):
		self.loadDataForSplitting()
		df = self.df
		startTime = datetime.now()
		confidence = range(2,-1,-1)
		severity = range(10,-1, -1)
		for i in severity:
			for j in confidence:
				print("Generating file for severity {0} confidence {1}".format(i,j))
				new_df = df.loc[(df["normalized_cvss"].ge(i)) & (df["normalized_cvss"].lt(i+1)) & (df["predictions"].eq(j)),:]
				new_file_name = "final_results_sev_{0:02d}_conf_{1}.csv".format(i,str(j))
				print("Total records found: {0}".format(new_df.shape[0]))
				self.saveToCSV(self.DATA_PATH, new_file_name, new_df)
		logger.log("Completed data splitting. Processing took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))
				
				





# Reference of DF Columns

# normalized_cvss
# CAT-Active Directory
# CAT-Adobe
# CAT-Adobe Acrobat/Reader
# CAT-Adobe AIR
# CAT-Adobe ColdFusion
# CAT-Adobe Digital Editions
# CAT-Adobe Flash
# CAT-Adobe Shockwave
# CAT-Alpine Linux
# CAT-Amazon
# CAT-Amazon Linux AMI
# CAT-Anti-virus
# CAT-Apache
# CAT-Apache HTTP Server
# CAT-Apache Struts
# CAT-Apache Tomcat
# CAT-APC
# CAT-Apple
# CAT-Apple iOS
# CAT-Apple iTunes
# CAT-Apple Java
# CAT-Apple Mac OS X
# CAT-Apple QuickTime
# CAT-Apple Safari
# CAT-Atlassian
# CAT-Atlassian JIRA
# CAT-Backdoor
# CAT-Backup
# CAT-Beanbag Review Board
# CAT-Browsers
# CAT-Canonical
# CAT-CentOS
# CAT-CGI
# CAT-Check Point
# CAT-Check Point Firewall
# CAT-CIFS
# CAT-Cisco
# CAT-Cisco ASA
# CAT-Cisco AsyncOS
# CAT-Cisco IOS
# CAT-Cisco IronPort
# CAT-Cisco NX
# CAT-Cisco PIX
# CAT-Cisco SAN
# CAT-Cisco TelePresence
# CAT-Cisco UCS
# CAT-Citect
# CAT-Citrix
# CAT-Citrix XenDesktop
# CAT-Conexant Systems
# CAT-CSRF
# CAT-Custom Web Application
# CAT-CVS
# CAT-Database
# CAT-DCE/RPC
# CAT-Debian Linux
# CAT-Default Account
# CAT-Denial of Service
# CAT-DHCP
# CAT-Directory Browsing
# CAT-Directory Traversal
# CAT-DNS
# CAT-Dnsmasq
# CAT-Docker
# CAT-Drupal
# CAT-EulerOS
# CAT-Exim
# CAT-F5
# CAT-F5 BIG-IP
# CAT-Fedora
# CAT-Fedora Core Linux
# CAT-FFmpeg
# CAT-Finger
# CAT-Fortinet
# CAT-Fortinet FortiAnalyzer
# CAT-Fortinet FortiGate
# CAT-Fortinet FortiManager
# CAT-Fortinet FortiOS
# CAT-FreeBSD
# CAT-FTP
# CAT-Game
# CAT-General Remote Services
# CAT-Gentoo Linux
# CAT-Google
# CAT-Google Android
# CAT-Google Chrome
# CAT-HP
# CAT-HP Data Protector
# CAT-HP iLO
# CAT-HP System Management Homepage
# CAT-HP Systems Insight Manager
# CAT-HTTP
# CAT-HTTP Response Splitting
# CAT-Huawei
# CAT-IAVM
# CAT-IBM
# CAT-IBM AIX
# CAT-IBM AS/400
# CAT-IBM DB2
# CAT-IBM Lotus Notes/Domino
# CAT-IMail
# CAT-IMAP
# CAT-Information Gathering
# CAT-Insecure Remote Access
# CAT-Intel
# CAT-Intel AMT
# CAT-IPMI
# CAT-IPSEC
# CAT-ISC
# CAT-ISC BIND
# CAT-J2EE
# CAT-Jenkins
# CAT-Joomla!
# CAT-jQuery
# CAT-Juniper
# CAT-Juniper Junos OS
# CAT-Juniper ScreenOS
# CAT-LDAP
# CAT-lighttpd
# CAT-Linux
# CAT-Mail
# CAT-MediaWiki
# CAT-Microsoft
# CAT-Microsoft .NET Framework
# CAT-Microsoft ASP
# CAT-Microsoft ASP.NET
# CAT-Microsoft Exchange
# CAT-Microsoft IIS
# CAT-Microsoft Internet Explorer
# CAT-Microsoft MSXML
# CAT-Microsoft Office
# CAT-Microsoft Office for Mac
# CAT-Microsoft Outlook
# CAT-Microsoft Patch
# CAT-Microsoft SharePoint
# CAT-Microsoft Silverlight
# CAT-Microsoft SQL Server
# CAT-Microsoft Windows
# CAT-Mobile
# CAT-MongoDB
# CAT-Moodle
# CAT-Mozilla
# CAT-Mozilla Bugzilla
# CAT-Mozilla Firefox
# CAT-Mozilla SeaMonkey
# CAT-Mozilla Thunderbird
# CAT-NAT
# CAT-NDMP
# CAT-NetWare
# CAT-Network
# CAT-News
# CAT-NFS
# CAT-Nginx
# CAT-NTP
# CAT-Obsolete OS
# CAT-Obsolete Software
# CAT-OpenSSH
# CAT-OpenSSL
# CAT-Oracle
# CAT-Oracle Database
# CAT-Oracle iPlanet
# CAT-Oracle Java
# CAT-Oracle Linux
# CAT-Oracle MySQL
# CAT-Oracle Solaris
# CAT-Oracle WebLogic
# CAT-OWASP_2010
# CAT-OWASP_2013
# CAT-Palo Alto Networks
# CAT-PAN
# CAT-pfSense
# CAT-PHP
# CAT-PHPMyAdmin
# CAT-Point of Sale
# CAT-Policy Violation
# CAT-POP
# CAT-Postfix
# CAT-PostgreSQL
# CAT-PPTP
# CAT-Privilege Escalation
# CAT-Proxy
# CAT-Rapid7 Critical
# CAT-RealNetworks
# CAT-RealNetworks Helix
# CAT-Red Hat
# CAT-Red Hat Enterprise Linux
# CAT-Red Hat JBoss
# CAT-Remote Execution
# CAT-Remote Shell
# CAT-RPC
# CAT-rsync
# CAT-Ruby on Rails
# CAT-Samba
# CAT-SCADA
# CAT-Sendmail
# CAT-SMTP
# CAT-SNMP
# CAT-Spyware
# CAT-SQL Injection
# CAT-Squid
# CAT-SSH
# CAT-SuSE
# CAT-Symantec
# CAT-Symantec Endpoint Protection
# CAT-Symantec Endpoint Protection Manager
# CAT-Symantec pcAnywhere
# CAT-Symantec Scan Engine
# CAT-TDS
# CAT-Telnet
# CAT-TFTP
# CAT-Trojan
# CAT-Ubuntu Linux
# CAT-UNIX
# CAT-UPnP
# CAT-VideoLAN
# CAT-VideoLAN VLC
# CAT-Virus
# CAT-VMware
# CAT-VMware ESX/ESXi
# CAT-VMware Fusion
# CAT-VMware Player
# CAT-VMware Workstation
# CAT-VPN
# CAT-Web
# CAT-Web Spider
# CAT-Wireless
# CAT-Wireshark
# CAT-WordPress
# CAT-Worm
# CAT-X Window System
# CAT-XnSoft
# CAT-XnSoft XnView
# CAT-XSS
# CAT-Zone Transfer
# is_microsoft
# is_linux
# is_network
# is_apple
# is_other
# External
# Internal
# Unknown
# cvss_access_vector_A
# cvss_access_vector_L
# cvss_access_vector_N
# cvss_authentication_M
# cvss_authentication_N
# cvss_authentication_S
# cvss_v3_attack_vector_A
# cvss_v3_attack_vector_L
# cvss_v3_attack_vector_N
# cvss_v3_attack_vector_P
# cvss_v3_privileges_required_H
# cvss_v3_privileges_required_L
# cvss_v3_privileges_required_N
# cvss_v3_user_interaction_N
# cvss_v3_user_interaction_R
# Credential Fail
# Credential Success
# exploit_count
# has_windows_exploit
# has_web_exploit
# has_remote_exploit
# has_metasploit_exploit
# malwarekit
# port_443
# port_80
# port_8080
# port_3306
# port_8000
# port_135
# port_22
# port_21
# port_139
# port_110
# port_25
# port_53
# port_3389
# port_23
# port_161
# port_8443
# port_5000
# port_1337
# port_123
# port_162
# port_5432
# port_9443
# port_name
# predictions

