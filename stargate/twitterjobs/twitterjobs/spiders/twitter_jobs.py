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

class TWITTER_JOBS_SPIDER(BaseSpider) :
	
	name = 'TWITTER_JOBS'
	allowed_domains = [
	'https://about.twitter.com'
	]
	start_urls = [
	'https://about.twitter.com/careers/locations'
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
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '(//div[@class="row-fluid"])[1]')))
		package = (browser.find_element_by_xpath('(//div[@class="row-fluid"])[1]')).get_attribute('outerHTML')
		
		links=(self.myHREF(package))
		
		for joblinkpage in links :
			browser.get(joblinkpage)
			sleep(3)
			
			
			
			
