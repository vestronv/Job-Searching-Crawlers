import scrapy
from time import time
from time import sleep
import re
import json
from w3lib.html import remove_tags
import requests
import ConfigParser
import scrapy
import os
import sys
from crawling.item import BebeeItem
from crawling.mapperGeoCache import MapperGeoCache
from crawling.bebeeLogger import BebeeLogger
from pprint import pprint
from datetime import datetime

from selenium import webdriver
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

class EXXON_MOBIL_SPIDER(BaseSpider) :
	
	name = 'EXXON_MOBIL'
	allowed_domain = ['http://corporate.exxonmobil.com']
	start_urls = [
	'http://corporate.exxonmobil.com/en/company/careers/career-opportunities'
	]
	
	def parse(self, response) :
		reload(sys)
		sys.setdefaultencoding("utf-8")
		print response.url
		raw_input('Release the SPIDER')
		#response.xpath('//*[@id="maincontent_0_pagecontent_0_topiccontent_0_rptRegionGroup_rptRegion_0_rptCountry_2_aCountry_2"]/@href').extract()
		#response.xpath('//li[contains(@class,"careers-country")]/text()').extract()

		#rawJobLinks = response.xpath('//@href|text()').extract()
		rawJobLinks = response.xpath('//h3[@class="careers-country-title"]/a/@href').extract()
		countryAll = response.xpath('//h3[@class="careers-country-title"]//text()').extract()
		jobLinks = []
		countrys = []
		for jobLink,country in zip(rawJobLinks,countryAll) :
			if 'jobs.brassring.com' in jobLink and 'remoteip' not in jobLink : 
				jobLinks.append(jobLink)
				countrys.append(country)
		raw_input('Do u like it ?')
		if not os.path.exists('./output') :
			os.makedirs('./output')
		outputFile = open('./output/output.txt', 'w')
		
		for cnt,job in zip(countrys,jobLinks) :
			print cnt,job
			outputFile.write("%s\t" % cnt)
			outputFile.write("%s\n" % job)
			
