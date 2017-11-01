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
#from scrapy.xlib.pydispatch import dispatcher
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


class NestleJobsSpider(scrapy.Spider):
	name = "nestleGetItems"
	allowed_domains = ["taleo.net"]
	start_urls = (
		'https://nestle.taleo.net/careersection/3/jobsearch.ftl?',
	)
	
	# Override settings	
	# http://stackoverflow.com/questions/25353650/scrapy-how-to-import-the-settings-to-override-it
	def set_crawler(self, crawler):
		super(NestleJobsSpider, self).set_crawler(crawler)

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
		fset = open('crawling/spiders/nestleCategoriesMissing.json', 'w')
		json.dump(list(self.uniqueCategoriesSet), fset)
		fset.close()
		# Load the dict for category mapper
		# Change this filename in each spider class
		with open('crawling/spiders/nestleCategoriesMap.json') as data_file:    
			self.categories = json.load(data_file)
		
		# for counting elapsed time
		self.start_time = time()

	def spider_closed(self):
		# Close selenium driver to avoid too much phantomJS running
		self.driver.close()
		
		# Saving the unique set of categories
		# Change this filename in each spider class
		fset = open('crawling/spiders/nestleCategoriesMissing.json', 'w')
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
		print response.url
		# ------------------- DRIVER TO CRAWL RESULTS AND GET LINKS -----------------
		self.driver.get(response.url)
		#Go to the first page
		for i in range(1, self.page_index+1):
			try:
				nextButton = self.driver.find_elements_by_xpath("//a[@id='next']")[0]
				print "On page: "+str(i)
				nextButton.click()
				WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, 
							"//a[@id='next']")))
			except:
				print "------------------------------------------"
				print "No pages found. Program will end in error."
				print "------------------------------------------"
		#If the page index is 1 then the loop above didn't run, so wait for page to load
		print "Load first page"
		#Check for presence of first job. Xpath is 1 indexed
		WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, 
				"(//ul[@id='jobList']/li/div[@class='multiline-data-container']/div/div/a)[1]")))
		
		# Results loop
		while True:
			# ------------------ Go to page_index --------------------
			print "-----------------------------------------"
			print "------------- NEW PAGE: %s --------------" % (self.page_index)
			
			# ------------------ Get links and data ---------------
			linkElems = self.driver.find_elements_by_xpath(
				"//ul[@id='jobList']/li/div[@class='multiline-data-container']/div/div/a")
			print "{} links obtained".format(len(linkElems))			

			for i in range(len(linkElems)):
				print "job {}/{}".format(i+1, len(linkElems))
				error_location = False
				error_category = False
				link = self.driver.find_elements_by_xpath(
					"//ul[@id='jobList']/li/div[@class='multiline-data-container']/div/div/a")[i]
				item = BebeeItem()
				item['url'] = link.get_attribute("href")
				item['offer_id'] = re.search("job=([0-9]+w*)", item['url']).group(1)
				item['account_id'] = str(self.account_id)
				item['company_id'] = str(self.company_id)

				#Click on the link to get the data on its page
				link.click()
				#Wait till the page loads
				print "Wait for description to load"
				WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, 
					"(//span[@id='requisitionDescriptionInterface.reqTitleLinkAction.row1'])[1]")))
				item['title'] = self.driver.find_elements_by_xpath(
					"//span[@id='requisitionDescriptionInterface.reqTitleLinkAction.row1']")[0].text
				WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, 
					"(//span[@id='requisitionDescriptionInterface.ID1644.row1'])[1]")))
				item['description'] = self.driver.find_elements_by_xpath(
					"//span[@id='requisitionDescriptionInterface.ID1644.row1']")[0].text
				language = langid.classify(item['description'])[0]
				if (language == 'en'):
					item['lang_code']= 'en-US'
				elif (language == 'es'):
					item['lang_code']= 'es-ES'
				elif (language == 'pt'):
					item['lang_code'] = 'pt-BR'
				else:
					item['lang_code'] = language

				WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, 
					"(//span[@id='requisitionDescriptionInterface.ID1712.row1'])[1]")))
				item['location_name'] = self.driver.find_elements_by_xpath(
					"//span[@id='requisitionDescriptionInterface.ID1712.row1']")[0].text
				WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, 
					"(//span[@id='requisitionDescriptionInterface.ID1762.row1'])[1]")))
				item['category_name'] = self.driver.find_elements_by_xpath(
					"//span[@id='requisitionDescriptionInterface.ID1762.row1']")[0].text
				WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, 
					"(//span[@id='requisitionDescriptionInterface.reqPostingDate.row1'])[1]")))
				item['date'] = self.driver.find_elements_by_xpath(
					"//span[@id='requisitionDescriptionInterface.reqPostingDate.row1']")[0].text

				# GEONAME MANAGEMENT
				try:
					item['geoname_id'] = self.geoCache.getGeonameId(item['location_name'])
					item['country_code'] = self.geoCache.getCountryCode(item['location_name'])
				except:
					error_message = "%s location not found in GeoName" % item['location_name']
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

				yield item

				totalJobs += 1
				if (self.max_jobs <= totalJobs):
					break
				# Break execution when reach self.max_execution_time seconds
				if (self.max_execution_time <= (time() - self.start_time)):
					break

				self.driver.back()
				print "Wait to go back to joblist"
				WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, 
					"(//ul[@id='jobList']/li/div[@class='multiline-data-container']/div/div/a)["+str(i+1)+"]")))
			
			print "--> %s Links possible" % (len(linkElems))
			print "--> %s Links obtained" % (totalJobs)
			
			# Results loop - stop condition
			if (self.page_index == self.stop_index) or (self.max_jobs <= totalJobs) or (self.max_execution_time <= (time() - self.start_time)):
				break
			
			# Go to next results page
			nextButton = self.driver.find_elements_by_xpath("//a[@id='next']")[0]
			nextButton.click()
			print "Wait to go to next page"
			WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, 
					"(//ul[@id='jobList']/li/div[@class='multiline-data-container']/div/div/a)[1]")))

			self.page_index += 1
			
	# category_id Mapper function
	def categoryMapper(self, category_name):
		if category_name in self.categories:
			category_id = self.categories[category_name]
			return category_id
		else:
			# saving the unique set of categories
			self.uniqueCategoriesSet.add(category_name)
			fset = open('crawling/spiders/amazonCategoriesMissing.json', 'w')
			json.dump(list(self.uniqueCategoriesSet), fset)
			fset.close()
			return None
