# -*- coding: utf-8 -*-

#@TODO : Cargar en local la base SQLite

'''
	===
	API
	===

#import module class
from mapperGeoCache import MapperGeoCache

# string to search
location_name = 'location to search'

#instantiate object
geoCache = MapperGeoCache()

# search
geoCache.getLocation(location_name)
geoCache.getGeonameId()
geoCache.getCountryCode()
geoCache.getGeonameId(location_name)
geoCache.getCountryCode(location_name)
id = geoCache.geonameId
code = geoCache.countryCode

NOTE: MapperGeoCache can be used the same way as GeoNames

'''
from geopy.geocoders import GeoNames
import sqlite3

class MapperGeoCache(GeoNames):
	
	# GeoNames Info
	username='bebeedev'	# The account name for accesing Geonames API
	
	# SQLite handlers
	connection 	= None 		# connexion
	cursor 		= None		# cursor

	# The fields we are interested in
	locationName 	= None 		# The search string
	geonameId 	= None
	countryCode 	= None
	rawData 	= {'geonameId','countryCode'}		# The dict with the results of the Search returned by GeoNames and SQLite

	# Constructor
	def __init__(self):
		# Construct the parent GeoNames object
		super(MapperGeoCache, self).__init__(username=self.username)
		
		# Connection to SQLite
		self.connection = sqlite3.connect('./crawling/mapperGeoCache.db')
		self.connection.row_factory = self.dict_factory
		self.cursor = self.connection.cursor()
	
	# Destructor
	def __del__(self):
		super(MapperGeoCache, self).__del__()
		self.connection.close()

	#  Search the locationName:
	# 1- If it is in local variables, do nothing
	# 2- Search in Cache SQLite
	# 3- Search in Geonames
	def getLocation(self, locationName=None):
		# if there is a 'locationName' and is not searched yet, search it
		if  (locationName is not None) and (locationName <> self.locationName):
			# Fist we Search the cache. If it fails, we search GeoNames
			if self.getLocationFromCache(locationName) is None:
				self.getLocationFromGeonames(locationName)
				
		# if not, and there isn't a self.locationName either: raise exception
		else:
			if self.locationName is None:
				raise Exception('%s.getLocation() necesita un locationName' % type(self).__name__)

	# Gets the GeoNames location variable
	# Returns the Geonames's Location object or raise exception
	def getLocationFromGeonames(self, locationName):
		print "*** Consultando Geonames... para: %s" % locationName
		location = self.geocode(locationName)
		if location:
			# store data in class Attributes
			self.locationName 	= locationName
			self.rawData 		= location.raw
			self.geonameId 		= self.rawData['geonameId']
			self.countryCode 	= self.rawData['countryCode']
			
			# store data in SQLite
			self.cursor.execute("INSERT INTO location_geonames_map VALUES ('%s','%d','%s')" % (locationName, self.geonameId, self.countryCode))
			self.connection.commit()
			
			# The location object returned by GeoNames. Attributes: 'address', 'raw'
			return location
		else:
			raise Exception('%s.getLocationFromGeonames() Geonames devolvió None para %s' % (type(self).__name__, locationName))
	
	# Get Location from the Cache SQLite
	# Returns the dict on success, None on failure
	def getLocationFromCache(self, locationName):
		print "*** Consultando Cache SQLite... para: %s" % locationName
		self.cursor.execute("select * from location_geonames_map WHERE locationName='%s'" % locationName)
		location_exists_in_cache = self.cursor.fetchone()
		if location_exists_in_cache:
			# store data in class Attributes
			self.locationName 	= locationName
			self.rawData		= location_exists_in_cache
			self.geonameId 		= self.rawData['geonameId']
			self.countryCode 	= self.rawData['countryCode']
			#print location_exists_in_cache
		else:
			# The locationName you search is not in SQLite
			print "****** Fallido"
		return location_exists_in_cache
	
	# Get Location from the class storage attribute
	# This could be implemented in future for limiting SQLite access
	def getLocationFromMemory(self, locationName):
		return False
	
	# Gets the GeoNames's attribute 'geonameId'
	def getGeonameId(self, locationName=None):
		return self.getField('geonameId', locationName)

	# Gets the GeoNames's attribute 'countryCode'
	def getCountryCode(self, locationName=None):
		return self.getField('countryCode', locationName)
	
	# Gets the GeoNames's attribute 'field'
	# var field: is a key field in self.rawData
	def getField(self, field, locationName=None):
		if field in self.rawData:
			self.getLocation(locationName)
			return str(self.rawData[field])
		else:
			raise Exception('%s.getField() no existe la clave %s' % (type(self).__name__, field))
	
	# Creating a dict from an SQLite's row
	# https://docs.python.org/2/library/sqlite3.html#sqlite3.Connection.row_factory
	def dict_factory(self, cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d
