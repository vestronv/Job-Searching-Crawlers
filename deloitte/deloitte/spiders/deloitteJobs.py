
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

from scrapy.spiders import Spider

class DELOITTE_SPIDER(Spider) :
	name = 'deloitteJobs'
	allowed_domains = ['www.deloitte.com']
	start_urls = (
		'https://careers.deloitte.com/jobs/eng-global/results/n/20000'
	)
	
	# Override settings	
	# http://stackoverflow.com/questions/25353650/scrapy-how-to-import-the-settings-to-override-it
	def set_crawler(self, crawler):
		super(DELOITTE_SPIDER, self).set_crawler(crawler)

		# Getting the BEBEE CONFIGURATION PARAMETERS from .ini
		# Second level configuration file takes precedence over settings.py
		config = ConfigParser.ConfigParser()
		if config.read('./crawling/spiders/' + self.name + '.ini'):
			for name, value in config.items('DEFAULT'):
				crawler.settings.set(name.upper(), value)
		else:
			# NO .ini configuration file
			print "WARNING: no %s.ini config. using default values" % self.name
		
		# Getting the BEBEE CONFIGURATION PARAMETERS 
		self.page_index 	= crawler.settings.getint('BEBEE_SPIDER_FIRST_PAGE', 1)
		self.stop_index 	= crawler.settings.getint('BEBEE_SPIDER_LAST_PAGE', 1)
		self.max_jobs 	= crawler.settings.getint('BEBEE_SPIDER_MAX_ITEMS', 3)
		self.delay_crawl_page = crawler.settings.getint('BEBEE_SPIDER_CRAWL_DELAY_PAGE', 5)
		self.delay_crawl_job 	= crawler.settings.getint('BEBEE_SPIDER_CRAWL_DELAY_ITEM', 1)
		self.max_execution_time = crawler.settings.getint('BEBEE_SPIDER_MAX_EXECUTION_TIME', 1800)
		self.account_id 	= crawler.settings.get('BEBEE_SPIDER_ACCOUNT_ID', '0')
		self.company_id 	= crawler.settings.get('BEBEE_SPIDER_COMPANY_ID', '')

		# Logger start. This code need account_id 
		self.beBeeLogger = BebeeLogger(account_id=self.account_id, botName=self.name)
		self.beBeeLogger.init()

	def __init__(self):
		# signal for closing method: 
		dispatcher.connect(self.spider_closed, signals.spider_closed)
		# Selenium driver 
		self.driver = webdriver.PhantomJS() #Firefox()
		self.driver.set_window_size(1024,768)
		
		# Mapper for geoname_id and country_code
		self.geoCache = MapperGeoCache()

		# List of unique categories
		self.uniqueCategoriesSet = set()
		
		# Erase old categories
		fset = open('crawling/spiders/deloitteCategoriesMissing.json', 'w')
		json.dump(list(self.uniqueCategoriesSet), fset)
		fset.close()
		# Load the dict for category mapper
		# Change this filename in each spider class
		with open('crawling/spiders/deloitteCategoriesMap.json') as data_file:    
			self.categories = json.load(data_file)
		
		# for counting elapsed time
		self.start_time = time()

	def spider_closed(self):
		# Close selenium driver to avoid too much phantomJS running
		self.driver.close()
		
		# Saving the unique set of categories
		# Change this filename in each spider class
		fset = open('crawling/spiders/deloitteCategoriesMissing.json', 'w')
		json.dump(list(self.uniqueCategoriesSet), fset)
		fset.close()

		# Log end
		self.beBeeLogger.end()
	
	def myHREF(self, htmlcode) :
		hrefs = []
		htmlcode = htmlcode.encode('ascii','ignore') #converted to string
		item = htmlcode
		htmllen = len(htmlcode)
		i=0
		while i < htmllen :
			if item[i]=='h' and item[i+1]=='r' and item[i+2]=='e' and item[i+3]=='f' and item[i+4]=='=' and item[i+6]=='/':
				i=i+6
				url = ''
				while item[i] != '"' :
					url += item[i]
					i=i+1
				if 'javascript' not in url :
					hrefs.append('https://careers.deloitte.com'+url)
			i=i+1
			
		return hrefs
	
	def parse(self, response):
			
		# storages for data
		links = []#
		titles = []#
		locations = []#
		categories = []#
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
		sleep(15) # Wait for page to load... its huge data
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_content_SearchGridView"]')))
		package = browser.find_element_by_xpath('//*[@id="ctl00_content_SearchGridView"]').get_attribute('outerHTML')	
		
		links = self.myHREF(package)
		
		for jobLinkPage in links :
			browser.get(jobLinkPage)
			sleep(3)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_content_DetailsTitle"]')))
			titles.append(browser.find_element_by_xpath('//*[@id="ctl00_content_DetailsTitle"]').text)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="job-overview"]')))
			locations.append(((browser.find_element_by_xpath('//div[@class="job-overview"]').text).split('tion:')[1]).split('Firm')[0])
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="job-overview"]')))
			categories.append(((browser.find_element_by_xpath('//div[@class="job-overview"]').text).split('vice:')[1]).split('Ref')[0])
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="job-post"]')))
			descriptions.append(browser.find_element_by_xpath('//*[@id="job-post"]').text)
			
