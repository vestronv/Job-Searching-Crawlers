# DAMN IT . . .
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
import langid
import json

from selenium import webdriver
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import HtmlResponse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class PUMA_JOBS_SPIDER(BaseSpider) :
	name = 'PUMA_JOBS'
	allowed_domains = [
	'http://about.puma.com'
	]
	start_urls = [
	'http://about.puma.com/en/careers/jobs-at-puma'
	]
	
	def myHREF(self, htmlcode) :
		hrefs = []
		htmlcode = htmlcode.encode('ascii','ignore') #converted to string
		item = htmlcode
		htmllen = len(htmlcode)
		i=0
		while i < htmllen :
			if item[i]=='h' and item[i+1]=='r' and item[i+2]=='e' and item[i+3]=='f' and item[i+4]=='=':
				i=i+6
				url = ''
				while item[i] != '"' :
					url += item[i]
					i=i+1
				if 'javascript' not in url :
					hrefs.append('http://about.puma.com'+url)
			i=i+1
			
		return hrefs
	
	def myCATE(self, htmlcode) :
		category = []
		htmlcode = htmlcode.encode('ascii','ignore') #converted to string
		item = htmlcode
		htmllen = len(htmlcode)
		i=0
		while i < htmllen :
			if item[i]=='m' and item[i+1]=='e' and item[i+2]=='n' and item[i+3]=='t' and item[i+4]=='=' and item[i+5]=='"' :
				i=i+6
				cate = ''
				while item[i] != '"' :
					cate += item[i]
					i=i+1
				category.append(cate)
			
			i=i+1
			
		return category
	
	
	def parse(self, response) :
		
		# storages for data
		links = []
		titles = []
		locations = []
		categories = []
		dates = []
		offerids = []
		descriptions = []
		langs = []
		
		reload(sys)
		sys.setdefaultencoding("utf-8")
		
		browser = webdriver.Firefox()
		#browser = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])
		
		browser.set_window_size(1024,768)
		browser.get('http://about.puma.com/en/careers/jobs-at-puma')
		sleep(5) # Wait for page to load
		raw_input('Release the SPIDER')
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="jobs-list large"]')))
		package = browser.find_element_by_xpath('//div[@class="jobs-list large"]').get_attribute('outerHTML') # HTML CODE 
		
		links = self.myHREF(package)
		
		for joblinkpage in links :
			browser.get(joblinkpage)
			sleep(5)
			
			# TITLE
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//h1[@class="page-title jtitle"]')))
			titles.append(browser.find_element_by_xpath('//h1[@class="page-title jtitle"]').text)
			
			# OFFER-ID
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//h2[@class="page-sub-title"]')))
			offerids.append((browser.find_element_by_xpath('//h2[@class="page-sub-title"]').text).split('#')[1])
			
			# LOCATION + DATE
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="press-release-infos"]')))
			locdat = browser.find_element_by_xpath('//div[@class="press-release-infos"]').text
			loc = ''; dat = ''
			comma = 0
			for item in locdat :
				if comma >=2 :
					break
				if item==',' :
					comma+=1
					if comma < 2 :
						loc+=item
				else :
					loc+=item
			dat = locdat.split(loc+',')[1]
			locations.append(loc)
			dates.append(dat)
			
			# DESCRIPTION
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="jdesc"]')))
			descriptions.append(browser.find_element_by_xpath('//div[@class="jdesc"]').text)
			
