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

from crawling.item import BebeeItem
from crawling.mapperGeoCache import MapperGeoCache
from crawling.bebeeLogger import BebeeLogger

from selenium import webdriver
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import HtmlResponse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from scrapy.spiders import Spider

class PEPSI_SPIDER(BaseSpider) :
	
	name = 'pepsiGetItems'
	allowed_domains = ['http://www.pepsicojobs.com']
	start_urls = [
		'http://www.pepsicojobs.com/en/job-search?applyableOnly=false&offset=0&limit=10'
	]
	
	def myHREF(self, htmlcode) :
		hrefs = []
		htmlcode = htmlcode.encode('ascii','ignore') #converted to string
		item = htmlcode
		htmllen = len(htmlcode)
		i=0
		while i < htmllen :
			if item[i]=='h' and item[i+1]=='r' and item[i+2]=='e' and item[i+3]=='f' and item[i+4]=='=' and item[i+6]=='/' and item[i+14]=='d':
				i=i+6
				url = ''
				while item[i] != '"' :
					url += item[i]
					i=i+1
				if 'javascript' not in url :
					hrefs.append('http://www.pepsicojobs.com'+url)
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
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="searchResults"]')))
		package = browser.find_element_by_xpath('//div[@id="searchResults"]').get_attribute('outerHTML')
		
		links = self.myHREF(package)
		links = list(set(links))
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="pagination"]')))
		div_str = browser.find_element_by_xpath('//div[@class="pagination"]').text
		
		while 'Next' in div_str :
			btn = browser.find_element_by_xpath('div[@class="pagination"]/a[last()]')
			btn.click()
			sleep(3)
			
			hrefs = []
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="searchResults"]')))
			package = browser.find_element_by_xpath('//div[@id="searchResults"]').get_attribute('outerHTML')
			hrefs = self.myHREF(package)
			hrefs = list(set(hrefs))
			for link in hrefs :
				links.append(link)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="pagination"]')))
			div_str = browser.find_element_by_xpath('//div[@class="pagination"]').text
		
		for joblinkpage in links :
			browser.get(joblinkpage)
			sleep(3)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="heading"]')))
			titles.append(browser.find_element_by_xpath('//div[@class="heading"]//h1[1]').text)
			
			locations.append(browser.find_element_by_xpath('//div[@class="heading"]//h2[1]').text)
			
			cate = (browser.find_element_by_xpath('//div[@class="heading"]//h2[2]').text)
			categories.append(cate)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="detail"]')))
			desc = ((browser.find_element_by_xpath('//div[@class="detail"]').text).split(cate))
			ndesc = ''
			i=0
			for item in desc :
				if i==0 :
					i=1
					continue
				ndesc+=item+cate
			descriptions.append(ndesc)
			offerids.append((ndesc.split('Ref: ')[1]).split('APPLY')[0])
		
		item = BeebeeItem()
		for link in links :
			item['url'] = link
			item['lang_code'] = 'en-US'
		for title in titles :
			item['title'] = title
		for location in locations :
			item['location_name'] = location
		for category in categories :
			item['category_name'] = category
		for desc in descriptions :
			item['description'] = desc
		for offerid in offerids :
			item['offer_id'] = offerid
			
		
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
		
		yield item

		return item
	
	
	# category_id Mapper function
	def categoryMapper(self, category_name):
		if category_name in self.categories:
			category_id = self.categories[category_name]
			return category_id
		else:
			# saving the unique set of categories
			self.uniqueCategoriesSet.add(category_name)
			fset = open('crawling/spiders/pepsiCategoriesMissing.json', 'w')
			json.dump(list(self.uniqueCategoriesSet), fset)
			fset.close()
			return None

