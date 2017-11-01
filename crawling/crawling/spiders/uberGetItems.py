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
from scrapy.settings import Settings

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
class UberJobsSpider(Spider):
	name = "uberGetItems"
	allowed_domains = ["uber.com"]
	start_urls = (
		'https://www.uber.com/jobs/list',
	)
	
	# Override settings	
	# http://stackoverflow.com/questions/25353650/scrapy-how-to-import-the-settings-to-override-it
	def set_crawler(self, crawler):
		super(UberJobsSpider, self).set_crawler(crawler)

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
		dispatcher.connect(self.spider_closed, signal=signals.spider_closed)
		# Selenium driver 
		self.driver = webdriver.PhantomJS() #Firefox()
		self.driver.set_window_size(1024,768)
		
		# Mapper for geoname_id and country_code
		self.geoCache = MapperGeoCache()

		# List of unique categories
		self.uniqueCategoriesSet = set()
		
		# Erase old categories
		fset = open('crawling/spiders/uberCategoriesMissing.json', 'w')
		json.dump(list(self.uniqueCategoriesSet), fset)
		fset.close()
		# Load the dict for category mapper
		# Change this filename in each spider class
		with open('crawling/spiders/uberCategoriesMap.json') as data_file:    
			try :
				self.categories = json.load(data_file)
			except ValueError:
				pass
		
		# for counting elapsed time
		self.start_time = time()

	def spider_closed(self):
		# Close selenium driver to avoid too much phantomJS running
		self.driver.close()
		
		# Saving the unique set of categories
		# Change this filename in each spider class
		fset = open('crawling/spiders/uberCategoriesMissing.json', 'w')
		json.dump(list(self.uniqueCategoriesSet), fset)
		fset.close()

		# Log end
		self.beBeeLogger.end()
		
		
	def parse(self, response):
		# storages for data
		links = []
		titles = []
		locations = []
		categories = []
		
		# Total job links crawled
		totalJobs = 0
		
		# ------------------- DRIVER TO CRAWL RESULTS AND GET LINKS -----------------
		print response.url
		
		self.driver.get(response.url)


		# Results loop
		while True:
			# ------------------ Go to page_index --------------------
			print "-----------------------------------------"
			print "------------- PAGE: %s --------------" % (self.page_index)
			# ------------------ Get links and data ---------------
			print " Getting links in page %s" % (str(self.page_index))
			WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, "html/body/div[@class='web global-container js-global-container']/section/section[@class='jobs-listings']//div/ul/li/div[1]/a")))
			linkElems 	= self.driver.find_elements_by_xpath("//section[@class='jobs-listings']/div/ul[@class='listing']/li/div[1]/a")
			categoryElems 	= self.driver.find_elements_by_xpath("//section[@class='jobs-listings']/div/ul[@class='listing']/li/div[2]/a")
			locationElems 	= self.driver.find_elements_by_xpath("//section[@class='jobs-listings']/div/ul[@class='listing']/li/div[3]/a")

			print " Save results data and links in arrays "
			for i,link in enumerate(linkElems):
				links.append(link.get_attribute("href"))
				titles.append(link.text)
				categories.append(categoryElems[i].get_attribute("innerHTML"))
				locations.append(locationElems[i].get_attribute("innerHTML"))
				# Break execution when reach max_jobs
				totalJobs += 1
				if (self.max_jobs <= totalJobs):
					break
				# Break execution when reach self.max_execution_time seconds
				if (self.max_execution_time <= (time() - self.start_time)):
					break
			
			print "--> %s Links possible" % (len(linkElems))
			print "--> %s Links obtained" % (totalJobs)

			
			# Results loop - stop condition
			if (self.page_index == self.stop_index) or (self.max_jobs <= totalJobs) or (self.max_execution_time <= (time() - self.start_time)):
				break
			
			# Next results page
			self.page_index += 1
			
			
		# --------------------------------- Download job data ---------------------------------------------
		# Job date (we take now because Amazon doesn't publish the date)
		dt = datetime.now()
		
		# Data loop (foreach link)
		for i,link in enumerate(links):
			error_location = False
			error_category = False
			
			# Object to create XML
			item = BebeeItem()
			item['title'] = titles[i]
			item['offer_id'] = re.search("^https://www.uber.com/jobs/([0-9]*)/.*", link).group(1)
			#item['lang_code'] = 'en-US'
			item['url'] = link
			#item['date'] = dt.strftime('%Y%m%d')
			item['account_id'] = str(self.account_id)
			item['company_id'] = str(self.company_id)
			item['location_name'] = locations[i]
			item['category_name'] = categories[i]
			
			# GEONAME MANAGEMENT
			try:
				item['geoname_id'] = self.geoCache.getGeonameId(locations[i])
				item['country_code'] = self.geoCache.getCountryCode(locations[i])
			except:
				error_message = "%s location not found in GeoName" % locations[i]
				print error_message
				error_location = True
				self.beBeeLogger.failure(item['offer_id'], error_message)
			
			# CATEGORY MANAGEMENT
			category_id = self.categoryMapper(item['category_name'])
			if category_id:
				item['category_id'] = category_id
			else:
				error_message = "category not found: %s" % item['category_name']
				print error_message
				error_category = True
				self.beBeeLogger.failure(item['offer_id'], error_message)
			
			# Count success jobs
			if not (error_location or error_category):
				self.beBeeLogger.success(item['offer_id'])
			
			# Print progress
			if ((i % 100)==0):
				print "-------------------"
				print "Jobs crawled: " + str(i)
				self.beBeeLogger.progress()
		
			# Crawl job description
			request = scrapy.Request(item['url'], callback=self.parse_description)
			request.meta['item'] = item
			yield request
				
			# Delay between each job
			print "%s secs delayed" % str(self.delay_crawl_job)
			sleep(self.delay_crawl_job)

	# Get job descripcion
	def parse_description(self, response):
		item = response.meta['item']
		description = ""
		
		descriptionDivList = response.xpath("//span[@itemprop='description']").re(r'(?s)Description(.*)')
		for desc in descriptionDivList:
			description += unicode.strip(remove_tags(desc))
		item['description'] = description
		language = langid.classify(description)[0]
		if (language == 'en'):
			item['lang_code']= 'en-US'
		elif (language == 'es'):
			item['lang_code']= 'es-ES'
		elif (language == 'pt'):
			item['lang_code'] = 'pt-BR'
		else:
			item['lang_code'] = language
	
		item['date'] = response.xpath("//div[@class='jobDisplay']/p[@class='jobDate']/span/text()").extract()[0].strip()
		return item

	# category_id Mapper function
	def categoryMapper(self, category_name):
		if category_name in self.categories:
			category_id = self.categories[category_name]
			return category_id
		else:
			# saving the unique set of categories
			self.uniqueCategoriesSet.add(category_name)
			fset = open('uberCategoriesMissing.json', 'w')
			json.dump(list(self.uniqueCategoriesSet), fset)
			fset.close()
			return None
