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

class THREEM_SPIDER(BaseSpider):
	
	name = 'threemJobs'
	allowed_domains = ['https://jobs.3m.com']
	start_urls = [
		'https://jobs.3m.com/search/?q=&sortColumn=referencedate&sortDirection=desc&startrow=0'
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
					hrefs.append('https://jobs.3m.com'+url)
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
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="searchResultsShell"]')))
		package = browser.find_element_by_xpath('//div[@class="searchResultsShell"]/table/tbody').get_attribute('outerHTML')
		
		links = self.myHREF(package)
		
		totalJob = int(browser.find_element_by_xpath('//span[@class="paginationLabel"]/b[2]').text)
		start=25
		
		while start<totalJob :
			if start>=25 :
				break
			new_url = 'https://jobs.3m.com/search/?q=&sortColumn=referencedate&sortDirection=desc&startrow='+`start`
			browser.get(new_url)
			sleep(3)
			start+=25
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="searchResultsShell"]')))
			package = browser.find_element_by_xpath('//div[@class="searchResultsShell"]/table/tbody').get_attribute('outerHTML')
			
			hrefs = []
			hrefs = self.myHREF(package)
			
			for link in hrefs :
				links.append(link)
		
		i=0
		for joblinkpage in links :
			i+=1
			if i<21 :
				continue
			browser.get(joblinkpage)
			sleep(3)
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="jobTitle"]')))
			titles.append(browser.find_element_by_xpath('//h1[@id="job-title"]').text)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="job-date"]')))
			dates.append((browser.find_element_by_xpath('//*[@id="job-date"]').text).split(':')[1])
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="job-location"]')))
			locations.append((browser.find_element_by_xpath('//*[@id="job-location"]').text).split(':')[1])
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="job"]')))
			offerid = (browser.find_element_by_xpath('//div[@class="job"]//span[1]').text).split(':')[1]
			offerid = offerid.encode('ascii','ignore')
			#realid = ['']
			realid = re.findall(r"\D(\d{5})\D", " "+offerid+" ")
			if len(realid) < 1 :
				realid = re.findall(r"\D(\d{6})\D", " "+offerid+" ")
			offerids.append(realid[0])
			
			#WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, )))
			descriptions.append((browser.find_element_by_xpath('//div[@class="job"]//span[1]').text).split(realid[0])[1])
		
		
		
		
