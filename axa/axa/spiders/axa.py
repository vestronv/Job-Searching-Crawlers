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

class AXA_SPIDER(BaseSpider) :
	
	name = 'axaJobs'
	allowed_domains = ['http://www.axa.com']
	start_urls = [
		'http://www.axa.com/en/careers/join-us/?s=date&o=desc&page=0'
	]
	
	def myHREF(self, htmlcode) :
		hrefs = []
		htmlcode = htmlcode.encode('ascii','ignore') #converted to string
		item = htmlcode
		htmllen = len(htmlcode)
		i=0
		while i < htmllen :
			if item[i]=='h' and item[i+1]=='r' and item[i+2]=='e' and item[i+3]=='f' and item[i+4]=='=' and item[i+6]=='h':
				i=i+6
				url = ''
				while item[i] != '"' :
					url += item[i]
					i=i+1
				if 'javascript' not in url :
					hrefs.append(url)
			i=i+1
			
		return hrefs
	
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
		sleep(3) # Wait for page to load
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="table _styled"]')))
		package = browser.find_element_by_xpath('//div[@class="table _styled"]//tbody').get_attribute('outerHTML')
		
		links = self.myHREF(package)
		WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '//div[@class="offersCount"]')))
		totalPage = ((browser.find_element_by_xpath('//div[@class="offersCount"]').text).encode('ascii','ignore'))
		totalPage = int(re.findall(r"\D(\d{4})\D", " "+totalPage+" ")[0])
		if totalPage % 30 != 0 :
			totalPage = (totalPage)/12
			totalPage += 1
		else  :
			totalPage = (totalPage)/12
		start = 1
		
		while start <= totalPage :
			new_url = 'http://www.axa.com/en/careers/join-us/?s=date&o=desc&page='+`start`
			start+=1
			browser.get(new_url)
			sleep(3)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="table _styled"]')))
			package = browser.find_element_by_xpath('//div[@class="table _styled"]//tbody').get_attribute('outerHTML')
			hrefs = []
			hrefs = self.myHREF(package)
			for href in hrefs :
				links.append(href)
				
		for joblinkpage in links :
			browser.get(joblinkpage)
			sleep(3)
			
			
