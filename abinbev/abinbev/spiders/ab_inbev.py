#DAMN IT.... 
#DIFFICULTY - MOD-HIGH
#do one thing make spider for each continent or sub category and call from a single file OK
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

class AB_INBEV_SPIDER(BaseSpider) :
	name = 'AB_INBEV'
	allowed_domains = ['http://www.ab-inbev.com/careers.html',
	'http://eu.abinbevcareers.com',
	'http://gmodelo.bumeran.com.mx',
	'https://abinbev.taleo.net',
	'http://eu.abinbevcareers.com'
	]
	start_urls = [
	'http://www.ab-inbev.com/careers.html'
	]
	
	
	# Override settings	
	# http://stackoverflow.com/questions/25353650/scrapy-how-to-import-the-settings-to-override-it
	def set_crawler(self, crawler):
		super(AB_INBEV_SPIDER, self).set_crawler(crawler)

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
		fset = open('crawling/spiders/samsungCategoriesMissing.json', 'w')
		json.dump(list(self.uniqueCategoriesSet), fset)
		fset.close()
		# Load the dict for category mapper
		# Change this filename in each spider class
		with open('crawling/spiders/samsungCategoriesMap.json') as data_file:    
			self.categories = json.load(data_file)
		
		# for counting elapsed time
		self.start_time = time()
		
	def spider_closed(self):
		
		# Close selenium driver to avoid too much phantomJS running
		self.driver.close()
		
		# Saving the unique set of categories
		# Change this filename in each spider class
		fset = open('crawling/spiders/samsungCategoriesMissing.json', 'w')
		json.dump(list(self.uniqueCategoriesSet), fset)
		fset.close()

		# Log end
		self.beBeeLogger.end()
	
	def myHREF(self, htmlcode) :
		hrefs = []
		htmlcode = htmlcode.encode('ascii','ignore') #converted to string
		item = htmlcode
		htmllen = len(htmlcode)
		i=0
		while i < htmllen :
			if item[i]=='h' and item[i+1]=='r' and item[i+2]=='e' and item[i+3]=='f' and item[i+4]=='=':
				i=i+6
				url = ''
				while item[i] != '"' :
					url += item[i]
					i=i+1
				if 'javascript' not in url :
					hrefs.append(url)
			i=i+1
		#~ print 'printing URLSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS'
		#~ for href in hrefs :
			#~ print '-> ' + href
		return hrefs
	
	def parse(self, response) :
		
		# storages for data
		links = []
		titles = []
		locations = []
		categories = []
		dates = []
		offerids = []
		descriptions = []
		langs = []
		
		reload(sys)
		sys.setdefaultencoding("utf-8")
		#dcap = dict(DesiredCapabilities.PHANTOMJS)
		#dcap["phantomjs.page.settings.userAgent"] = (
		#"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 (KHTML, like Gecko) Chrome/15.0.87")

		browser = webdriver.Firefox()
		#browser = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])
		
		browser.set_window_size(1024,768)
		raw_input('Release the SPIDER')
	
		
		# USA
		new_url = 'https://abinbev.taleo.net/careersection/27/jobsearch.ftl?lang=en'
		browser.get(new_url)
		new_response = browser.page_source
		#WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionListInterface.ID3161.row1"]')))
		#//*[@id="requisitionListInterface.reqTitleLinkAction.row1"]
		##WebDriverWait(browser, 10)
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionListInterface.reqTitleLinkAction.row1"]')))
		button = browser.find_element_by_xpath('//*[@id="requisitionListInterface.reqTitleLinkAction.row1"]')
		button.click()
		sleep(5)
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.pagerDivID862.Next"]')))
		div_str = (browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.pagerDivID862.Next"]').text)
		while "Next" in div_str :
			sleep(3)
			#wat abt URL in such cases?
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.reqTitleLinkAction.row1"]')))
			title = browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.reqTitleLinkAction.row1"]').text
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.ID1676.row1"]')))
			location = browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.ID1676.row1"]').text
			#NO UPAR DEK #category = browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.ID1626.row1"]').text
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.reqPostingDate.row1"]')))
			date = browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.reqPostingDate.row1"]').text
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.reqContestNumberValue.row1"]')))
			offerid = browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.reqContestNumberValue.row1"]').text
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.ID3560.row.row1"]')))
			description = (browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.ID3560.row.row1"]').text).split('Job Description')[1]
		
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.pagerDivID862.Next"]')))
			new_button = browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.pagerDivID862.Next"]')
			new_button.click()
			sleep(5)
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.pagerDivID862.Next"]')))
			div_str = browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.pagerDivID862.Next"]').text
		
		sleep(5)	
		#USA
		#~ new_url = 'https://abinbev.taleo.net/careersection/27/jobsearch.ftl?lang=en'
		#~ browser.get(new_url)
		#~ WebDriverWait(browser, 10)
		#~ new_response = browser.page_source
		#~ print 'RESPONSE>>>>>>>>>>>>>>>>>>>\n',new_response
		#~ print 'URL -------->> ',browser.current_url
		
		sleep(5)
		
		#mexico
		new_url = 'http://gmodelo.bumeran.com.mx/listadoofertas.bum'
		browser.get(new_url)
		new_response = browser.page_source
		#WebDriverWait(browser, 10)
		sleep(5)
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="listado"]')))
		hrefss = self.myHREF(browser.find_element_by_xpath('//div[@class="listado"]').get_attribute('outerHTML'))
		#remember first we are getting all urls for all coutries.. than only we categories them
		#joblinks
		for item in hrefss :
			if 'detal' in item :
				links.append( (new_url.split('/lis')[0])+'/'+item )
		
		div_str = browser.find_elements_by_xpath('//div[@class="paginador"]')[0].text
		i=2
		while "Siguiente" in div_str :
			browser.get(new_url+'?page='+`i`)
			i=i+1
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="paginador"]')))
			div_str = browser.find_elements_by_xpath('//div[@class="paginador"]')[0].text
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="listado"]')))
			hrefss = self.myHREF(browser.find_element_by_xpath('//div[@class="listado"]').get_attribute('outerHTML'))
			for item in hrefss :
				#print item
				if 'detal' in item :
					links.append( (new_url.split('/lis')[0])+'/'+item )
		
		for joblinkpage in links :
			browser.get(joblinkpage)
			sleep(5)
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//span[@class="ciudad"]')))
			location = browser.find_elements_by_xpath('//span[@class="ciudad"]')[0].text
			print location
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="titulo"]')))
			title = browser.find_elements_by_xpath('//div[@class="titulo"]')[0].text
			print title.split(location)[0]
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="detalle"]//dev[@class="value"]')))
			category = browser.find_elements_by_xpath('//div[@class="detalle"]//dev[@class="value"]')[0].text
			print category
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="detalle"]//dev[@class="value"]')))
			date = browser.find_elements_by_xpath('//div[@class="detalle"]//dev[@class="value"]')[5].text
			print date
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="detalle"]//dev[@class="value"]')))
			description = browser.find_elements_by_xpath('//div[@class="detalle"]//dev[@class="value"]')[6].text
			print description
			#WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, )))
			offerid = joblinkpage.split('=')[1]
			print offerid
		
		sleep(5)
		
		#south america
		url = 'https://abinbev.taleo.net/careersection/2/jobsearch.ftl?lang=pt-BR'
		browser.get(url)
		WebDriverWait(browser, 10)
		# extract from this DIV --->>> resultListPanel
		#joblinks
		sleep(5)
		#joblinks
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="jobs"]//tbody/tr[1]/th')))
		hrefss = self.myHREF(browser.find_element_by_xpath('//*[@id="jobs"]//tbody/tr[1]/th').get_attribute('outerHTML'))
		for href in hrefss :
			links.append(href)
		#yahi se location pe append kara le
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="jobs"]//tbody//tr[1]/td[2]')))
		location = browser.find_element_by_xpath('//*[@id="jobs"]//tbody//tr[1]/td[2]').text
		
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="next"]')))
		div_str = (browser.find_element_by_xpath('//*[@id="next"]').get_attribute('outerHTML')).encode('ascii','ignore')
		var = 25
		while "-disabled" not in div_str :
			#print 'done>>>>>>>>>>>>>>>>>>> ',var
			#var+=25
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="next"]')))
			browser.find_element_by_xpath('//*[@id="next"]').click()
			sleep(5)
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="jobs"]//tbody/tr[1]/th')))
			hrefss = self.myHREF(browser.find_element_by_xpath('//*[@id="jobs"]//tbody/tr[1]/th').get_attribute('outerHTML'))
			for href in hrefss :
				links.append(href)
			#yahi se location pe appens kara le
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="jobs"]//tbody//tr[1]/td[2]')))
			location = browser.find_element_by_xpath('//*[@id="jobs"]//tbody//tr[1]/td[2]').text
		
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="next"]')))
			div_str = (browser.find_element_by_xpath('//*[@id="next"]').get_attribute('outerHTML')).encode('ascii','ignore')
		
		for joblinkpage in links :
			
			browser.get(joblinkpage)
			sleep(5)
			
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.reqTitleLinkAction.row1"]')))
			title = browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.reqTitleLinkAction.row1"]')
			print title
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.reqContestNumberValue.row1"]')))
			offerid = browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.reqContestNumberValue.row1"]')
			print offerid
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.ID1493.row1"] ')))
			description = ''
			description = browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.ID1493.row1"]').text
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.ID1553.row1"]')))
			description += browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.ID1553.row1"]').text
			print description
			
			
		sleep(5)
		#EUROPE
		url = 'http://eu.abinbevcareers.com/en/job-search.aspx?country=Any&keyword='
		browser.get(url)
		#WebDriverWait(browser, 10)
		sleep(5)
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="lumesse-search-results"]')))
		div_str = browser.find_elements_by_xpath('//div[@class="lumesse-search-results"]')[0].text
		num_pages = int(div_str.split(' ')[3])
		if num_pages % 10 != 0 :
			num_pages = num_pages/10+1
		else :
			num_pages = num_pages/10
		sleep(5)
		#joblink
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="lumesse-search-results"]')))
		hrefss = self.myHREF(browser.find_element_by_xpath('//div[@class="lumesse-search-results"]').get_attribute('outerHTML'))
		for item in hrefss :
			links.append( 'http://eu.abinbevcareers.com'+item)
		#date
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="job-listing-container-right"]')))
		for item in browser.find_elements_by_xpath('//div[@class="job-listing-container-right"]') :
			print item.text.split(':')[1]
		#title
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="job-listing-container-left"]//div[@class="job-listing-title"]')))
		for item in browser.find_elements_by_xpath('//div[@class="job-listing-container-left"]//div[@class="job-listing-title"]') :
			print item.text
		#locaation
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="job-listing-container-left"]//div[@class="job-listing-key-details"]')))
		for item in (browser.find_elements_by_xpath('//div[@class="job-listing-container-left"]//div[@class="job-listing-key-details"]')) :
			print item.text
		#description
		#WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="lumesse-advert-row"]')))
		#in joblink page -> (('//div[@class="lumesse-advert-row"]').text).split('About Us')[0]
		raw_input('hi...........######.......###########........#########')
		start = 2
		while start <= num_pages :
			myxpath = '//*[@id="btnPage'+`start`+'"]'
			start+=1
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, myxpath)))
			browser.find_element_by_xpath(myxpath).click()
			#joblink
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="lumesse-search-results"]')))
			hrefss = self.myHREF(browser.find_element_by_xpath('//div[@class="lumesse-search-results"]').get_attribute('outerHTML'))
			for item in hrefss :
				links.append('http://eu.abinbevcareers.com'+item)
			#date
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="job-listing-container-right"]')))
			for item in browser.find_elements_by_xpath('//div[@class="job-listing-container-right"]') :
				print item.text.split(':')[1]
			#title
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="job-listing-container-left"]//div[@class="job-listing-title"]')))
			for item in browser.find_elements_by_xpath('//div[@class="job-listing-container-left"]//div[@class="job-listing-title"]') :
				print item.text
			#locaation
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="job-listing-container-left"]//div[@class="job-listing-key-details"]')))
			for item in (browser.find_elements_by_xpath('//div[@class="job-listing-container-left"]//div[@class="job-listing-key-details"]')) :
				print item.text
			#description
			#WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="lumesse-advert-row"]')))
			#in joblink page -> (('//div[@class="lumesse-advert-row"]').text).split('About Us')[0]
		for joblinkpage in links :
			
			browser.get(joblinkpage)
			sleep(5)
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="lumesse-advert-row"]')))
			description = (browser.find_elements_by_xpath('//div[@class="lumesse-advert-row"]').text).split('About Us')[0]
		
		sleep(5)
		#ASIA
		url = 'https://abinbev.taleo.net/careersection/15/jobsearch.ftl?lang=zh_CN'
		browser.get(url)
		#WebDriverWait(browser, 10)
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionListInterface.reqTitleLinkAction.row1"]')))
		button = browser.find_element_by_xpath('//*[@id="requisitionListInterface.reqTitleLinkAction.row1"]')
		button.click()
		sleep(5)
		#div_str = (browser.find_element_by_xpath('//*[@id="requisitionListInterface.pagerDivID3595.panel.Next"]').get_attribute('outerHTML')).encode('ascii','ignore')
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.pagerDivID835.Next"]')))
		div_str = (browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.pagerDivID835.Next"]').get_attribute('outerHTML')).encode('ascii','ignore')
		while "pagerlinkoff" not in div_str :
			sleep(5)
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.reqPostingDate.row1"]')))
			date = browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.reqPostingDate.row1"]').text
			#print 'date  ---->> ',date
			##locations = browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.ID1815.row1"]').text
			locations = 'China'
			#print 'locatoin  ---->> ',locations
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.reqContestNumberValue.row1"]')))
			offerid = browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.reqContestNumberValue.row1"]').text
			#print 'offerid  ---->> ',offerid
			res = ''
			try :
				WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.ID1629.row1"]/div[1]')))
				res = (browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.ID1629.row1"]/div[1]').text)
			except Exception :
				try :
					WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.ID1629.row1"]/p[1]')))
					res = (browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.ID1629.row1"]/p[1]').text)
				except Exception :
					pass
				pass
			try :
				title = ''
				if res == '':
					title = 'NAN' 
				if 'seeking ' in res:
					try :
						WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.ID1629.row1"]/div[1]')))
						title = ((browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.ID1629.row1"]/div[1]').text).split('seeking ')[1]).split('to ')[0]
					except Exception: 
						pass
				elif 'seeking ' in (browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.ID1629.row1"]/p[1]').text) :
					WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.ID1629.row1"]/p[1]')))
					title = ((browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.ID1629.row1"]/p[1]').text).split('seeking ')[1]).split('to ')[0]
				else :
					title = 'NAN'
			except Exception :
				pass
			#print 'title  ---->> ',title
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.ID1629.row1"]')))
			description = browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.ID1629.row1"]').text
			#print 'description ---->> ',description
			#raw_input('??????????? *******#################### O O O O O O O O O  O')
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.pagerDivID835.Next"]')))
			browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.pagerDivID835.Next"]').click()
			#browser.implicitly_wait(5)
			sleep(5)
			WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requisitionDescriptionInterface.pagerDivID835.Next"]')))
			div_str = (browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.pagerDivID835.Next"]').get_attribute('outerHTML')).encode('ascii','ignore')
		
		for i in range(len(titles)):
			error_location = False
			error_category = False
			
			# Object to create XML
			item = BebeeItem()
			item['title'] = titles[i]
			item['offer_id'] = offerids[i]
			item['url'] = links[i]
			#item['date'] = dates[i]
			item['account_id'] = str(self.account_id)
			item['company_id'] = str(self.company_id)
			item['location_name'] = locations[i]
			item['category_name'] = categories[i]
			item['description'] = descriptions[i]
			language = langid.classify(item['description'])[0]
			if (language == 'en'):
				item['lang_code']= 'en-US'
			elif (language == 'es'):
				item['lang_code']= 'es-ES'
			elif (language == 'pt'):
				item['lang_code'] = 'pt-BR'
			else:
				item['lang_code'] = language
			
			#GEONAME MANAGEMENT
			try:
				item['geoname_id'] = self.geoCache.getGeonameId(locations[i])
				item['country_code'] = self.geoCache.getCountryCode(locations[i])
			except:
				error_message = "%s location not found in GeoName" % str(locations[i])
				print error_message
				error_location = True
				self.beBeeLogger.failure(item['offer_id'], error_message)
			
			category_id = self.categoryMapper(item['category_name'])
			if category_id:
				item['category_id'] = category_id
			else:
				error_message = "category not found: %s" % str(item['category_name'])
				print error_message
				error_category = True
				self.beBeeLogger.failure(item['offer_id'], error_message)
			
			#Count success jobs
			if not (error_location or error_category):
				self.beBeeLogger.success(item['offer_id'])
			
			#Print progress
			if ((i % 100)==0):
				print "-------------------"
				print "Jobs crawled: " + str(i)
				self.beBeeLogger.progress()
			
			yield item

