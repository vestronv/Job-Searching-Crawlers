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

class ESPN_CAREERS_SPIDER(BaseSpider) :
	
	name = 'ESPN_CAREERS'
	allowed_domains = [
	'http://jobs.espncareers.com'
	]
	start_urls = [
	'http://jobs.espncareers.com/careers/all-jobs'
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
					hrefs.append('http://jobs.espncareers.com'+url)
			i=i+1
			
		return hrefs
	
	def myLOC(self, htmlcode) :
		loc = []
		htmlcode = htmlcode.encode('ascii','ignore') #converted to string
		item = htmlcode
		htmllen = len(htmlcode)
		i=0
		while i < htmllen :
			if item[i]=='t' and item[i+1]=='h' and item[i+2]=='2' and item[i+3]=='"' and item[i+4]=='>':
				i=i+6
				locs = ''
				while item[i] != '<' :
					locs += item[i]
					i=i+1
				loc.append(locs)
			i=i+1
			
		return loc
	
	
	def parse(self, response) :
		
		# storages for data
		links = []#
		titles = []
		locations = []#
		categories = []
		dates = []
		offerids = []#
		descriptions = []#
		langs = []
		
		reload(sys)
		sys.setdefaultencoding("utf-8")
		
		browser = webdriver.Firefox()
		#browser = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])
		
		browser.set_window_size(1024,768)
		browser.get(self.start_urls[0])
		sleep(5) # Wait for page to load
		raw_input('Release the SPIDER')
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//table[@class="info-table"]')))
		package = browser.find_element_by_xpath('//table[@class="info-table"]').get_attribute('outerHTML')
		div_str = browser.find_element_by_xpath('//table[@class="info-table"]').text
		
		hrefs = []
		loc = []
		hrefs = self.myHREF(package)
		loc = self.myLOC(package)
		del hrefs[-1]# DELETE LAST URL
		
		while 'Next page' in div_str :
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="jobs_next_page_link"]')))
			browser.find_element_by_xpath('//*[@id="jobs_next_page_link"]').click()
			sleep(5)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//table[@class="info-table"]')))
			package = browser.find_element_by_xpath('//table[@class="info-table"]').get_attribute('outerHTML')
			div_str = browser.find_element_by_xpath('//table[@class="info-table"]').text
			
			hrefss = (self.myHREF(package))
			locs = self.myLOC(package)
		
			del hrefss[-1]
			for item in hrefss :
				hrefs.append(item)
			for item in locs :
				loc.append(item)
		
		links = hrefs
		locations = loc
		
		for joblinkpage in links :
			browser.get(joblinkpage)
			sleep(5)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="Job_JobTitle"]')))
			titles.append(browser.find_element_by_xpath('//*[@id="Job_JobTitle"]').text)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@itemprop="description"]')))
			descriptions.append(browser.find_element_by_xpath('//div[@itemprop="description"]').text)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="inbox"]')))
			offerids.append(((browser.find_element_by_xpath('//div[@class="inbox"]').text).split('Job ID: ')[1]).split('APPLY NOW')[0])
			
		
