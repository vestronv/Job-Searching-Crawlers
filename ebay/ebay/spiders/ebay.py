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

class EBAY_SPIDER(BaseSpider) :
	
	name = 'ebayJobs'
	allowed_domains = ['https://jobs.ebayinc.com']
	start_urls = [
		'https://jobs.ebayinc.com/jobs?page=1'
	]
	
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
					hrefs.append('https://jobs.ebayinc.com'+url)
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
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//table[@class="job-listings table table-striped"]')))
		package = browser.find_element_by_xpath('//table[@class="job-listings table table-striped"]').get_attribute('outerHTML')
		links = self.myHREF(package)	
		links = list(set(links))
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//span[@class="search-meta ng-scope"]')))
		package = browser.find_element_by_xpath('//span[@class="search-meta ng-scope"]').text
		package = package.encode('ascii','ignore')
		totalJob = (package.split(' ')[0])
		totalJob = int(totalJob)
		pages = totalJob/10
		if totalJob % 10 != 0 :
			pages+=1
		start=2
		while start <= pages :
			if start ==2 :
				break
			new_url = 'https://jobs.ebayinc.com/jobs?page='+`start`
			browser.get(new_url)
			sleep(3)
			start+=1
			hrefs = []
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//table[@class="job-listings table table-striped"]')))
			package = browser.find_element_by_xpath('//table[@class="job-listings table table-striped"]').get_attribute('outerHTML')
			
			hrefs = self.myHREF(package)
			hrefs = list(set(hrefs))
			for link in hrefs :
				links.append(link)
		
			
		for joblinkpage in links :
			browser.get(joblinkpage)
			sleep(3)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//h1[@class="job-title ng-binding"]')))
			titles.append(browser.find_element_by_xpath('//h1[@class="job-title ng-binding"]').text)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//p[@class="job-location ng-binding"]')))
			locations.append(browser.find_element_by_xpath('//p[@class="job-location ng-binding"]').text)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//span[@class="job-category ng-scope ng-binding last-child"]')))
			categories.append(browser.find_element_by_xpath('//span[@class="job-category ng-scope ng-binding last-child"]').text)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="descr-container"]')))
			package = browser.find_element_by_xpath('//div[@class="descr-container"]').text
			package = package.encode('ascii','ignore')
			package = package.split('No.: ')[1]
			package = package.split('BR')[0]
			package = package+'BR'
			offerids.append(package)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="descr-container"]')))
			descriptions.append(browser.find_element_by_xpath('//div[@class="descr-container"]').text)
			
		
