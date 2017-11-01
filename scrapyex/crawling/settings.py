# -*- coding: utf-8 -*-

# Scrapy settings for Crawl project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

#---------- BEBEE CONFIGURATION PARAMETERS BEGINS ----------------------

BEBEE_SPIDER_FIRST_PAGE = 1		# Primera página a visitar
BEBEE_SPIDER_LAST_PAGE = 1		# Ultima página a visitar
BEBEE_SPIDER_MAX_ITEMS = 2		# Número máximo de ofertas a rastrear
BEBEE_SPIDER_CRAWL_DELAY_PAGE = 5	# Delay entre cada oferta en segundos
BEBEE_SPIDER_CRAWL_DELAY_ITEM = 1	# Delay entre cada oferta en segundos
BEBEE_SPIDER_MAX_EXECUTION_TIME = 1800	# Tiempo máximo a emplear en el rastreo en segundos
BEBEE_SPIDER_ACCOUNT_ID = 0
BEBEE_SPIDER_COMPANY_ID = 1801385
CRAWLERA_ENABLED = False		# Activar/desactivar crawlera
#---------- BEBEE CONFIGURATION PARAMETERS ENDS ----------------------

BOT_NAME = 'beebot'

SPIDER_MODULES = ['crawling.spiders']
NEWSPIDER_MODULE = 'crawling.spiders'

TELNETCONSOLE_ENABLED = False
WEBSERVICE_ENABLED = False
LOG_LEVEL = 'INFO'
LOG_ENABLED = True

#RETRY_ENABLED = False
#AJAXCRAWL_ENABLED = True

# Crawlera settings
CRAWLERA_PRESERVE_DELAY = True
DOWNLOADER_MIDDLEWARES = {'scrapylib.crawlera.CrawleraMiddleware': 600}
CRAWLERA_USER = '6a7186af2bd14883b95e0cae712ac092'
CRAWLERA_PASS = ''


'''
# Enable CLOSESPIDER_TIMEOUT, CLOSESPIDER_ITEMCOUNT
EXTENSIONS = {
    'scrapy.contrib.closespider.CloseSpider': 500
}
CLOSESPIDER_ITEMCOUNT = 7
'''

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'

DOWNLOAD_HANDLERS = {
    'http': 'scrapy_webdriver.download.WebdriverDownloadHandler',
    'https': 'scrapy_webdriver.download.WebdriverDownloadHandler',
}

SPIDER_MIDDLEWARES = {
    'scrapy_webdriver.middlewares.WebdriverSpiderMiddleware': 543,
}

#WEBDRIVER_BROWSER = 'Firefox'
WEBDRIVER_BROWSER = 'PhantomJS'  # Or any other from selenium.webdriver
                                 # or 'your_package.CustomWebdriverClass'
                                 # or an actual class instead of a string.
                                 
# Optional passing of parameters to the webdriver
WEBDRIVER_OPTIONS = {
    'service_args': ['--debug=false', '--load-images=false', '--webdriver-loglevel=debug']
}

# pipelines for the Item Exporter

FEED_EXPORTERS_BASE = {
    'xml': 'scrapy.contrib.exporter.XmlItemExporter',
}

ITEM_PIPELINES = {
    'crawling.pipelines.XmlExportPipeline': 800,
}
