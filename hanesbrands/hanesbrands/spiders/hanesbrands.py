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

class HANESBRANDS_SPIDER(BaseSpider) :
	
	name = 'hanesJobs'
	allowed_domains = ['https://jobs-hanesbrands.icims.com']
	start_urls = [
		'https://jobs-hanesbrands.icims.com/jobs/search?pr=1'
	]
	
	def myHREF(self, htmlcode) :
		hrefs = []
		htmlcode = htmlcode.encode('ascii','ignore') #converted to string
		item = htmlcode
		htmllen = len(htmlcode)
		i=0
		while i < htmllen :
			if item[i]=='h' and item[i+1]=='r' and item[i+2]=='e' and item[i+3]=='f' and item[i+4]=='=' and item[i+6]=='h':
				i=i+6
				url = ''
				while item[i] != '"' :
					url += item[i]
					i=i+1
				if 'javascript' not in url :
					hrefs.append(url)
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
		sleep(15) # Wait for page to load
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="icims_iframe_span"]//*[@id="icims_content_iframe"]//div[@class="iCIMS_Body iCIMS_ff iCIMS_ff37-0"]//div[@class="iCIMS_MainWrapper iCIMS_ListingsPage  "]//table[@class="iCIMS_JobsTable iCIMS_Table"]')))
		package = browser.find_element_by_xpath('//*[@id="icims_iframe_span"]//*[@id="icims_content_iframe"]//div[@class="iCIMS_Body iCIMS_ff iCIMS_ff37-0"]//div[@class="iCIMS_MainWrapper iCIMS_ListingsPage  "]//table[@class="iCIMS_JobsTable iCIMS_Table"]').get_attribute('outerHTML')
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="icims_iframe_span"]')))
		div_str = browser.find_element_by_xpath('//*[@id="icims_iframe_span"]').text
		links = self.myHREF(package)
		
		i=1
		while 'Here are our current job openings.' in div_str :
			new_url = 'https://jobs-hanesbrands.icims.com/jobs/search?pr='+`i`
			browser.get(new_url)
			sleep(15)
			
			#~ WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, ingsPage '//*[@id="icims_iframe_span"]//*[@id="icims_content_iframe"]//div[@class="iCIMS_Body iCIMS_ff iCIMS_ff37-0"]//div[@class="iCIMS_MainWrapper iCIMS_ListingsPage  "]//table[@class="iCIMS_JobsTable iCIMS_Table"]')))
			#~ package = browser.find_element_by_xpath('//*[@id="icims_iframe_span"]//*[@id="icims_content_iframe"]//div[@class="iCIMS_Body iCIMS_ff iCIMS_ff37-0"]//div[@class="iCIMS_MainWrapper iCIMS_ListingsPage  "]//table[@class="iCIMS_JobsTable iCIMS_Table"]').get_attribute('outerHTML')
			#~ hrefs = []
			#~ hrefs = self.myHREF(package)
			#~ for href in hrefs :
				#~ links.append(href)
			#~ 
			#~ WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="icims_iframe_span"]')))
			#~ div_str = browser.find_element_by_xpath('//*[@id="icims_iframe_span"]').text
		
		for item in links :
			print item
		raw_input('?')
