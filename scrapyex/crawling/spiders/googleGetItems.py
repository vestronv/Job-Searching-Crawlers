# -*- coding: utf-8 -*-

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


class GoogleJobsSpider(scrapy.Spider):
	name = "googleGetItems"
	allowed_domains = ["google.com"]
	start_urls = (
		"https://www.google.com/about/careers/search#t=sq&q=j&li=10&st=0&",
	)
	
	# http://stackoverflow.com/questions/25353650/scrapy-how-to-import-the-settings-to-override-it
	def set_crawler(self, crawler):
		super(GoogleJobsSpider, self).set_crawler(crawler)

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
		self.driver = webdriver.PhantomJS()
		self.driver.set_window_size(1024,768)
		
		# Mapper for geoname_id and country_code
		self.geoCache = MapperGeoCache()

		# List of unique categories
		self.uniqueCategoriesSet = set()
		
		# Erase old categories
		fset = open('crawling/spiders/googleCategoriesMissing.json', 'w')
		json.dump(list(self.uniqueCategoriesSet), fset)
		fset.close()
		# Load the dict for category mapper
		# Change this filename in each spider class
		with open('crawling/spiders/googleCategoriesMap.json') as data_file:    
			self.categories = json.load(data_file)
		
		# for counting elapsed time
		self.start_time = time()
		
		# Jobs date
		self.dt = datetime.now()
		
		self.stop_by_max_jobs = False
		
	def spider_closed(self):
		
		# Close selenium driver to avoid too much phantomJS running
		self.driver.close()
		
		# Saving the unique set of categories
		# Change this filename in each spider class
		fset = open('crawling/spiders/googleCategoriesMissing.json', 'w')
		json.dump(list(self.uniqueCategoriesSet), fset)
		fset.close()

		# Log end
		self.beBeeLogger.end()
		
		
	def parse(self,response):
		self.driver.get(response.url)	

		# URLs list
		links = []
		
		# Jobs counter
		totalJobs = 0
		
		# Filter configuration
		# We wait for the country input
		WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="primary-filters"]//input[@class="mini ghost-text"]')))

		# We take the country
		inputElement = self.driver.find_element_by_xpath('//div[@class="primary-filters"]//input[@class="mini ghost-text"]')

		# Page loop
		while True:
			print "Waiting for link page %s" % (str(self.page_index))
			try:
				# Wait 10 secs for the button (timeout)
				WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, str(self.page_index))))
				

			except:
				print "Page %s discarded" % (str(self.page_index))
				print "Page %s not exists" % (str(self.page_index))
				break
			
			# Next page
			print "-> Click page %s" % (str(self.page_index))
			
			# Wait between pages
			sleep(self.delay_crawl_page)
			self.driver.find_element_by_link_text(str(self.page_index)).click()

			# Only URLs we want
			try:
				WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[@itemprop="url"]')))
			except:
				print "Page %s discarded" % (str(self.page_index))
				continue
			idsSel = self.driver.find_elements_by_xpath('//a[@itemprop="url"]')
			
			# Links count
			print "--> %s links" % (len(idsSel))
			print

			for id in idsSel:
				links.append(str(id.get_attribute('href')))
				totalJobs += 1
				if (self.max_jobs <= totalJobs):
					self.stop_by_max_jobs = True
					print "-> Max jobs reached"
					break

			# Loop exit condition
			if (self.page_index== self.stop_index) or self.stop_by_max_jobs  or (self.max_execution_time <= (time() - self.start_time)):
				print "-> Stop process"
				break
			
			# Next page
			self.page_index += 1
		
		print "--> Links: %s items" % (totalJobs)
		
		
		# Links loop
		for i,link in enumerate(links):
			item = BebeeItem()
			item['url'] = link
			item['account_id'] = str(self.account_id)
			item['company_id'] = str(self.company_id)
			
			if ((i % 100)==0):
				print "Progress: " + str(i)
				self.beBeeLogger.progress()
			
			if True:
				sleep(self.delay_crawl_job)
				request = scrapy.Request(item['url'], callback=self.parse_item)
				request.meta['item'] = item
				yield request
			else:
				yield item

	# item parser
	def parse_item(self, response):
		error_location = False
		error_category = False
		
		item = response.meta['item']
		item['title'] = response.xpath('//a[@class="heading detail-title"]/@title').extract()[0]
		item['offer_id'] = response.xpath('//div[@itemtype="http://schema.org/JobPosting"]/@id').extract()[0]
		item['lang_code'] = 'en-US'
		item['date'] = self.dt.strftime('%Y%m%d')
		item['description'] = remove_tags(response.xpath('//div[@itemprop="description"]').extract()[0])
		item['location_name'] = response.xpath('//span[@itemprop="name"]/text()').extract()[0]
		item['category_name'] = response.xpath('//span[@itemprop="occupationalCategory"]/text()').extract()[0]
		
		# GEONAME MANAGEMENT
		try:
			item['geoname_id'] = self.geoCache.getGeonameId(item['location_name'])
			item['country_code'] = self.geoCache.getCountryCode(item['location_name'])
		except:
			error_message = "%s location not found in GeoName" % str(item['location_name'])
			print error_message
			error_location = True
			self.beBeeLogger.failure(item['offer_id'], error_message)
			
		# CATEGORY MANAGEMENT
		category_id = self.categoryMapper(item['category_name'])
		if category_id:
			item['category_id'] = category_id
		else:
			error_message = "category not found: %s" % str(item['category_name'])
			print error_message
			error_category = True
			self.beBeeLogger.failure(item['offer_id'], error_message)
			
		if not (error_location or error_category):
			self.beBeeLogger.success(item['offer_id'])

		return item


	# category_id Mapper function
	def categoryMapper(self, category_name):
		if category_name in self.categories:
			category_id = self.categories[category_name]
			return category_id
		else:
			# saving the unique set of categories
			self.uniqueCategoriesSet.add(category_name)
			fset = open('crawling/spiders/googleCategoriesMissing.json', 'w')
			json.dump(list(self.uniqueCategoriesSet), fset)
			fset.close()
			return None
