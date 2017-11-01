'''
import scrapy
from crawling.item import BebeeItem
from crawling.mapperGeoCache import MapperGeoCache
from crawling.bebeeLogger import BebeeLogger
from pprint import pprint
from datetime import datetime

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from time import time
from time import sleep
import re
import json
from w3lib.html import remove_tags
import requests
import ConfigParser
import langid

'''
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

class WARNER_BROS_SPIDER(BaseSpider):
	name = 'warnerBrosJobs'
	allowed_domains = ['http://www.warnerbroscareers.com']
	start_urls = [
		'http://www.warnerbroscareers.com/search-jobs/'
	]
	
	def myHREF(self, htmlcode) :
		hrefs = []
		htmlcode = htmlcode.encode('ascii','ignore') #converted to string
		item = htmlcode
		htmllen = len(htmlcode)
		i=0
		while i < htmllen :
			if item[i]=='h' and item[i+1]=='r' and item[i+2]=='e' and item[i+3]=='f' and item[i+4]=='=' and item[i+6]=='?':
				i=i+6
				url = ''
				while item[i] != '"' :
					url += item[i]
					i=i+1
				if 'javascript' not in url :
					hrefs.append('http://www.warnerbroscareers.com/search-jobs/'+url)
			i=i+1
			
		return hrefs
	
	def parse(self, response):
		
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
		sleep(5) # Wait for page to load
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="searchResultDiv"]')))
		package = browser.find_element_by_xpath('//div[@id="searchResultDiv"]').get_attribute('outerHTML')
		div_str = browser.find_element_by_xpath('//div[@id="searchResultDiv"]').text
		
		hrefs = []
		links = self.myHREF(package)
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//p[@class="pageingP"]')))
		btn = browser.find_element_by_xpath('//p[@class="pageingP"]//a[last()]')
		btn.click()
		i=3
		
		try:
			while 'Next' in div_str :
				sleep(3)
				hrefs = []
				
				WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="searchResultDiv"]')))
				package = browser.find_element_by_xpath('//div[@id="searchResultDiv"]').get_attribute('outerHTML')
				hrefs = self.myHREF(package)
				for link in hrefs :
					links.append(link)
				
				WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//p[@class="pageingP"]')))
				div_str = browser.find_elements_by_xpath('//p[@class="pageingP"]')[1].text
				#btn = browser.find_element_by_xpath('//p[@class="pageingP"]/a[last()]')
				xp = '//a[@onclick="asSearchPage('+`i`+'); return false;"]'
				btn = browser.find_element_by_xpath(xp)
				i+=1
				btn.click()
		except :
			pass
		
		for joblinkpage in links :
			
			browser.get(joblinkpage)
			sleep(3)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="singleJobDescDiv"]//h1[1]')))
			titles.append(browser.find_element_by_xpath('//div[@class="singleJobDescDiv"]//h1[1]').text)
			
			locations.append((browser.find_element_by_xpath('//div[@class="singleJobDescDiv"]//h2[1]').text).split('TION')[1])
			
			categories.append((browser.find_element_by_xpath('//div[@class="singleJobDescDiv"]//h2[2]').text).split('REST')[1])
			
			offerids.append((browser.find_element_by_xpath('//div[@class="singleJobDescDiv"]//h2[3]').text).split('#')[1])
			
			dates.append((browser.find_element_by_xpath('//div[@class="singleJobDescDiv"]//h2[4]').text).split('DATE')[1])
			
			descriptions.append(browser.find_element_by_xpath('//div[@class="as-singleJobDesc"]').text)
		
		
