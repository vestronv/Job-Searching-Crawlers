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

class MATHWORKS_SPIDER(BaseSpider) :
	
	name = 'mathworksJobs'
	allowed_domains = ['http://www.mathworks.com']
	start_urls = [
		'http://www.mathworks.com/company/jobs/opportunities/search?utf8=%E2%9C%93&keywords=&location[]=&page=1'
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
					hrefs.append('http://www.mathworks.com'+url)
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
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="results_form"]')))
		package = browser.find_element_by_xpath('//*[@id="results_form"]').get_attribute('outerHTML')
		links = self.myHREF(package)
		div_str = browser.find_element_by_xpath('//div[@class="content_container"]').text
		
		i=2
		#while 'Don\'t see a job that interests you?' not in div_str :
		while len(div_str) >1800 :
			new_url = 'http://www.mathworks.com/company/jobs/opportunities/search?utf8=%E2%9C%93&keywords=&location[]=&page='+`i`
			browser.get(new_url)
			i+=1
			sleep(3)
			hrefs = []
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="results_form"]')))
			package = browser.find_element_by_xpath('//*[@id="results_form"]').get_attribute('outerHTML')
			
			hrefs = self.myHREF(package)
			for link in hrefs :
				links.append(link)
			
			div_str = browser.find_element_by_xpath('//div[@class="content_container"]').text
				
		for joblinkpage in links :
			browser.get(joblinkpage)
			sleep(3)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="col-xs-12"]')))
			titles.append(browser.find_element_by_xpath('//div[@class="col-xs-12"]//h1[1]').text)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//dl[@class="dl-horizontal add_margin_0"]')))
			locations.append(browser.find_element_by_xpath('//dl[@class="dl-horizontal add_margin_0"]//dd[1]').text)
			
			categories.append(browser.find_element_by_xpath('//dl[@class="dl-horizontal add_margin_0"]//dd[2]').text)
			
			offerids.append(browser.find_element_by_xpath('//dl[@class="dl-horizontal add_margin_0"]//dd[3]').text)
			
			descriptions.append(((browser.find_element_by_xpath('//div[@class="content_container"]').text).split('Job Summary')[1]).split('Why MathWorks')[0])
		
		
