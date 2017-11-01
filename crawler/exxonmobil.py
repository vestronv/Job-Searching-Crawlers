import selenium, phantomjs, re
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

class EXXON_MOBIL_SPIDER(BaseSpider) :
	
	name = 'EXXON_MOBIL'
	allowed_domain = ['http://corporate.exxonmobil.com']
	start_urls = ['http://corporate.exxonmobil.com/en/company/careers/career-opportunities']
	
	# NOT MINE :D
	def __init__(self) :
		self.driver = webdriver.PhantomJS()
		self.driver.set_window_size(1024,768)
		#elapsed time
		self.start_time = time()
	
	def extractJobLinks :
		
