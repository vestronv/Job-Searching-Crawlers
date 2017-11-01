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

class EL_SPIDER(BaseSpider) :
	
	name = 'elJobs'
	allowed_domains = ['http://www.elcompanies.com','http://www.taleo.net']
	start_urls = [
		'http://elcompanies.taleo.net/careersection/external/jobsearch.ftl?lang=en&portal=12240452131#'
	]
	
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
		#sleep(8) # Wait for page to load
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionListInterface.reqTitleLinkAction.row1"]')))
		btn = browser.find_element_by_xpath('//*[@id="requisitionListInterface.reqTitleLinkAction.row1"]')
		btn.click()
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.pagerDivID901"]')))
		div_str = browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.pagerDivID901"]').text
		
		while 'Next' in div_str : #scrape n click
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.reqTitleLinkAction.row1"]')))
			titles.append(browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.reqTitleLinkAction.row1"]').text)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.ID1724.row1"]')))
			locations.append((browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.ID1724.row1"]').text).split(':')[1])
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.reqContestNumberValue.row1"]')))
			offerids.append(browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.reqContestNumberValue.row1"]').text)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="editablesection"]')))
			descriptions.append((browser.find_element_by_xpath('//div[@class="editablesection"]').text).split('Description')[1])
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.pagerDivID901.Next"]')))
			btn = browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.pagerDivID901.Next"]')
			btn.click()
			sleep(3)
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.pagerDivID901"]')))
			div_str = browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.pagerDivID901"]').text
		
		
		
	
	


