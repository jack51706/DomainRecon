#!/usr/bin/python

#Files used to get subdomains using recon-ng and sublist3r
import sys
import datetime
import os
from Sublist3r import sublist3r
import csv
import string

cloudEnum = "./cloudflare_enum/"
sys.path.insert(0,cloudEnum)
from cloudflare_enum import *

reconPath = "./recon-ng/"
sys.path.insert(0,reconPath)
from recon.core import base
from recon.core.framework import Colors

class EnumSubDomain(object):

	def __init__(self):
		#self.wordList = "./Resource/words.txt"
		self.wordList = "./recon-ng/data/hostnames.txt"

	#subdomain bruteforcing
	def RunBruteForce(self, reconb, domain):
		module = reconb.do_load("recon/domains-hosts/brute_hosts")
		module.do_set("WORDLIST " + self.wordList)
		module.do_set("SOURCE " + domain)
		module.do_run(None)

	def RunModule(self, reconBase, module, domain):
	    module = reconBase.do_load(module)
	    module.do_set("SOURCE " + domain)
	    module.do_run(None)

	def RunRecon(self, domain, subDomains, bruteForce):
		stamp = datetime.datetime.now().strftime('%M:%H-%m_%d_%Y')
		wspace = domain+stamp

		reconb = base.Recon(base.Mode.CLI)
		reconb.init_workspace(wspace)
		reconb.onecmd("TIMEOUT=100")
		module_list = ["recon/domains-hosts/bing_domain_web", "recon/domains-hosts/google_site_web", "recon/domains-hosts/netcraft", "recon/domains-hosts/shodan_hostname", "recon/netblocks-companies/whois_orgs", "recon/hosts-hosts/resolve"]
	
		for module in module_list:
			self.RunModule(reconb, module, domain)
	
		if bruteForce:
			self.RunBruteForce(reconb, domain)
	
		#reporting output
		outFile = "FILENAME "+os.getcwd()+"/"+domain
		module = reconb.do_load("reporting/csv")
		module.do_set(outFile+".csv")
		module.do_run(None)

		reconNgOutput=domain+'.csv'
		with open(reconNgOutput, 'r') as csvfile:
			for row in csv.reader(csvfile, delimiter=','):
				subDomains.append(row[0])
		os.remove(reconNgOutput)

	def runSublist3r(self, domain, subDomains):	
		#Sublister enumeration
		sublisterOutput = sublist3r.main(domain, 30, None, None, False, False, False, None)
		for strDomain in sublisterOutput:
			subDomains.append(strDomain)

	def runCloudflareEnum(self, domain, subDomains, username, password):
		#CloudFlare enumeration
		cloud = cloudflare_enum()
		cloud.print_banner()
		cloud.log_in( username, password)
		cloud.get_spreadsheet( domain )
		cloudEnumOutput=string.replace(domain, '.', '_')+'.csv'
		with open(cloudEnumOutput, 'r') as csvfile:
			for row in csv.reader(csvfile, delimiter=','):
				if not row[0] in subDomains:
					subDomains.append(row[0])
		os.rename(cloudEnumOutput, "./Output/cloud_enum_"+cloudEnumOutput)

	def GetSubDomains(self, domain, isRunCloudFlare, coudFlareUserName, cloudFlarePassword, isBruteForce):
		subDomains=list()
		#Recon NG enumeration
		self.RunRecon(domain, subDomains, isBruteForce)
		self.runSublist3r(domain, subDomains)
		if isRunCloudFlare:
			self.runCloudflareEnum(domain, subDomains, coudFlareUserName, cloudFlarePassword)

		file = './Output/' + domain+'.txt'
		with open (file, 'w') as fp:
			for subDomain in subDomains:
				fp.write("%s\n" % subDomain)
		
