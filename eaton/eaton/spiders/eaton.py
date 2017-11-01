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

class EATON_SPIDER(BaseSpider) :
	
	name = 'eatonJobs'
	allowed_domains = ['http://www.eaton-jobs.com']
	start_urls = [
		'http://eaton-jobs.com/ListJobs/All/Page-1'
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
					hrefs.append('http://www.eaton-jobs.com'+url)
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
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//table[@class="JobListTable"]')))
		package = browser.find_element_by_xpath('//table[@class="JobListTable"]').get_attribute('outerHTML')
		
		links = self.myHREF(package)
		links = list(set(links))
		
		totalPage = ((browser.find_elements_by_xpath('//span[@class="pager-info"]')[1].text).encode('ascii','ignore'))
		totalPage = int(re.findall(r"\D(\d{4})\D", " "+totalPage+" ")[0])
		if totalPage % 30 != 0 :
			totalPage = (totalPage)/30
			totalPage += 1
		else  :
			totalPage = (totalPage)/30
		start = 2
		
		while start <= totalPage :
			break
			new_url  = 'http://www.eaton-jobs.com/ListJobs/All/Page-'+`start`
			browser.get(new_url)
			sleep(3)
			start+=1
			hrefs = []
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//table[@class="JobListTable"]')))
			package = browser.find_element_by_xpath('//table[@class="JobListTable"]').get_attribute('outerHTML')
			hrefs = self.myHREF(package)
			hrefs = list(set(links))
			for href in hrefs :
				links.append(href)
			
		
		for joblinkpage in links :
			browser.get(joblinkpage)
			sleep(3)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="pageHeader"]')))
			titles.append(browser.find_element_by_xpath('//div[@class="pageHeader"]').text)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="show-job-top-fields-col1"]')))
			offerids.append((browser.find_elements_by_xpath('//div[@class="show-job-top-field"]')[0].text).split(':')[1])
			categories.append((browser.find_elements_by_xpath('//div[@class="show-job-top-field"]')[1].text).split(':')[1])
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="show-job-top-fields-col2"]')))
			locations.append((browser.find_elements_by_xpath('//div[@class="show-job-top-fields-col2"]//div[@class="show-job-top-field"]')[0].text).split(':')[1])
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="show-job-description"]')))
			descriptions.append(browser.find_element_by_xpath('//div[@class="show-job-description"]').text)
			break
			
		for item in titles :
			print item
		raw_input('titl')
		for item in offerids :
			print item
		raw_input('offer id')
		for item in categories :
			print item
		raw_input('categ')
		for item in locations :
			print item
		raw_input('loca')
			
