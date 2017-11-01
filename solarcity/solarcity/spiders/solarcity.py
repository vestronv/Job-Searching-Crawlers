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

from scrapy.spiders import Spider

class SOLAR_CITY_JOBS(BaseSpider) :
	
	name = 'solarcityJobs'
	allowed_domains = ['http://www.solarcity.com']
	start_urls = [
		'http://www.solarcity.com/careers/operations/join-our-team'
	]
	
	def myHREF(self, htmlcode) :
		hrefs = []
		htmlcode = htmlcode.encode('ascii','ignore') #converted to string
		item = htmlcode
		htmllen = len(htmlcode)
		i=0
		while i < htmllen :
			if item[i]=='h' and item[i+1]=='r' and item[i+2]=='e' and item[i+3]=='f' and item[i+4]=='=' and item[i+6]=='/' :
				i=i+6
				url = ''
				while item[i] != '"' :
					url += item[i]
					i=i+1
				if 'javascript' not in url :
					hrefs.append('http://www.solarcity.com'+url)
			i=i+1
			
		return hrefs
	
	def myDATE(self, htmlcode) :
		datess = []
		htmlcode = htmlcode.encode('ascii','ignore') #converted to string
		item = htmlcode
		htmllen = len(htmlcode)
		i=0
		while i < htmllen :
			if item[i]=='d' and item[i+1]=='a' and item[i+2]=='t' and item[i+3]=='e' and item[i+4]=='"' and item[i+5]=='>' :
				i=i+6
				datee = ''
				while item[i] != '<' :
					datee += item[i]
					i=i+1
				datess.append(datee)
				
				
			i=i+1
			
		return datess
	
	
	def parse(self, response) :
		
		# storages for data
		links = []#
		titles = []#
		locations = []#
		categories = []#
		dates = []#
		offerids = []#
		descriptions = []#
		langs = []
		
		reload(sys)
		sys.setdefaultencoding("utf-8")
		
		browser = webdriver.Firefox()
		#browser = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])
		
		browser.set_window_size(1024,768)
		browser.get(self.start_urls[0])
		sleep(8) # Wait for page to load
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="jobs-listing__table"]//ul')))
		package = browser.find_element_by_xpath('//div[@class="jobs-listing__table"]').get_attribute('outerHTML')
		links = self.myHREF(package)
		dates = self.myDATE(package)
		
		for joblinkpage in links :
			browser.get(joblinkpage)
			sleep(3)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//section[@class="content-block header-text-block"]')))
			titles.append(browser.find_element_by_xpath('//section[@class="content-block header-text-block"]//div[@class="container"]//h1').text)
			
			locations.append((browser.find_element_by_xpath('//section[@class="content-block header-text-block"]//div[@class="container"]//h6').text).split('|')[0])
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//section[@class="content-block job-detail"]')))
			descriptions.append((browser.find_element_by_xpath('//section[@class="content-block job-detail"]').text).split('APPLY')[0])
		
		'''	#for testing
		for item in dates :
			print item
		print len(dates)
		print len(links)
		raw_input('?')
		'''
			
		
		
		
