# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BebeeItem(scrapy.Item):
	account_id	= scrapy.Field()
	offer_id 	= scrapy.Field()
	url		= scrapy.Field()
	date 		= scrapy.Field()
	title 		= scrapy.Field()
	category_id 	= scrapy.Field()
	category_name 	= scrapy.Field()
	description 	= scrapy.Field()
	company_id 	= scrapy.Field()
	company_name 	= scrapy.Field()
	lang_code 	= scrapy.Field()
	country_id 	= scrapy.Field()
	country_code	= scrapy.Field()
	region_id 	= scrapy.Field()
	location_name	= scrapy.Field()
	geoname_id	= scrapy.Field()
