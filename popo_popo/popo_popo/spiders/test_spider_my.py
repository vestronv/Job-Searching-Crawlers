#from __future__import absolute_import
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

class MySpider(BaseSpider) :
	name = 'vimal'
	allowed_domain = ['craiglist.org']
	start_urls = ['http://sfbay.craiglist.org/sfc/npo']
	
	def parse(self, response) :
		print response.url
		raw_input()
		hxs = HtmlXPathSelector(response)
		titles = hxs.select('//p')
		for titles in titles :
			title =titles.select('a/text()').extract()
			link = titles.select('a/href').extract()
			print title, link

