# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy import signals
from scrapy.contrib.exporter import XmlItemExporter
from datetime import datetime

# This class is to add a newline betweed each item

class XmlItemExporterWithNewLine(XmlItemExporter):
	def __init__(self, file, **kwargs):
		super(XmlItemExporterWithNewLine, self).__init__(file, **kwargs)
		self.file = file     # added framontb

	def export_item(self, item):
		super(XmlItemExporterWithNewLine, self).export_item(item)
		self.file.write('\n')   # added framontb
		
class XmlExportPipeline(object):

	def __init__(self):
		self.files = {}

	@classmethod
	def from_crawler(cls, crawler):
		pipeline = cls()
		crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
		crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
		return pipeline

	def spider_opened(self, spider):
		dt = datetime.now()
		file = open('output/%s_%s.xml' % (spider.name, dt.strftime('%Y%m%d')), 'w+b')
		self.files[spider] = file
		self.exporter = XmlItemExporterWithNewLine(file, item_element='job', root_element='bebee')
		self.exporter.start_exporting()

	def spider_closed(self, spider):
		self.exporter.finish_exporting()
		file = self.files.pop(spider)
		file.close()

	def process_item(self, item, spider):
		self.exporter.export_item(item)
		return item
