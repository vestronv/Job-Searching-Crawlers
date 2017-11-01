# -*- coding: utf-8 -*-

from datetime import datetime
import requests
import inspect
import re

'''
API
===
from bebeeLogger import BebeeLogger

beBeeLogger = BebeeLogger(account_id='100', name = 'josiño')
beBeeLogger = BebeeLogger(account_id='100', name = 'josiño', debug = True)

beBeeLogger.init()

beBeeLogger.success('1')

beBeeLogger.failure('1', 'categoria')

beBeeLogger.progress()

beBeeLogger.end()

'''

class BebeeLogger:
	
	# Constructor
	def __init__(self, account_id=None, botName='', debug = False):
		# Es obligatorio un account_id
		if not account_id:
			raise Exception('BebeeLogger necesita un account_id suministrado por BeBee para cada spider.')
		
		# Name and date for 'filename'
		dt = datetime.now()
		'''
		# Get the caller class name
		stack = inspect.stack()
		s = stack[0][0].f_locals["self"].__class__
		the_class = re.split(r'[.](?![^][]*\])', str(s))[1]
		'''
		
		self.filename = '%s_%s.xml' % (botName, dt.strftime('%Y%m%d'))
		# print self.filename
		
		# Conjunto de offer_id's de items OK
		self.okSet = set()
		
		# Conjunto de offer_id's de items failed
		self.failSet = set()
		
		# Habilita resultados por consola para debug
		self.debug = debug
	
	def init(self):
		print "beBeeLogger.init: Resultado del logeo inicial: " 
		self.printStatus()
	
	def end(self):
		print "beBeeLogger.end: Resultado del logeo final: " 
		self.printStatus()
	
	def failure(self, offer_id, mensaje_error):
		if (offer_id in self.failSet) or (offer_id in self.okSet):
			print "WARNING: beBeeLogger.failure: Elemento ya registrado previamente"
		else:
			self.failSet.add(offer_id)
			print "beBeeLogger.failure: Resultado del logeo 'failure': "  
		
		print "beBeeLogger.failure: Item a registrar: %s" % str(offer_id)
		self.printStatus()
	
	# Este método se llama cuando no ha habido errores para un item
	# No se debe contar más de una vez cada item
	def success(self, offer_id):
		# Si se registró previamente, WARNING
		if (offer_id in self.failSet) or (offer_id in self.okSet):
			print "WARNING: beBeeLogger.success: Elemento ya registrado previamente"
		# caso contrario: se registra
		else:
			self.okSet.add(offer_id)
			
		
		print "beBeeLogger.success: Item a registrar: %s" % str(offer_id)
		self.printStatus()
	
	# Logea el progreso del rascado, no altera el estado de la clase
	def progress(self):
		print "beBeeLogger.init: Resultado de logeo de progreso: "  
		self.printStatus()
	
	def printStatus(self):
		# @TODO Imprimir variables de estado
		print "Items SIN error de mapeo: %s" % str(len(self.okSet))
		print "Items CON error de mapeo: %s" % str(len(self.failSet))
		print "---------"
