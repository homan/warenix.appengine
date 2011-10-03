# package Wellcome.py
# logic to deal with wellcome website

# gae lib
from django.utils import simplejson
from google.appengine.api import memcache
from google.appengine.api.labs import taskqueue
from google.appengine.api.urlfetch import DownloadError
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.runtime import DeadlineExceededError
import logging
import wsgiref.handlers

from google.appengine.ext import db
from django.utils import simplejson

import datetime



class StoreCentralBeautyHandler(webapp.RequestHandler):
	''' monitor requested product to see if its price has changed '''

	def post(self):
		self.process()

	def get(self):
		self.process()

	def process(self):
		params = ['description', 'previewImage', 'previewImageLarge', 'num']
		values = {}

		for param in params:
			value = self.request.get(param)
			values[param] = value
			self.response.out.write(value)

		centralBeauty = CentralBeauty()
		centralBeauty.num= int(values['num'])
		centralBeauty.description = values['description']
		centralBeauty.previewImage= values['previewImage']
		centralBeauty.previewImageLarge= values['previewImageLarge']

		now = datetime.datetime.now()

		#centralBeauty.num = now.year * 10000 + now.month * 100  + now.day

		centralBeauty.put()


class GetCentralBeautyHandler(webapp.RequestHandler):
	''' monitor requested product to see if its price has changed '''

	def post(self):
		self.process()

	def get(self):
		self.process()

	def process(self):
		params = ['num']
		values = {}

		for param in params:
			value = self.request.get(param)
			values[param] = value

		centralBeautys = CentralBeauty.all()
		centralBeautys.filter("num =", int(values['num']))

		for centralBeauty in centralBeautys:
			self.response.out.write(centralBeauty)

class ListCentralBeautyHandler(webapp.RequestHandler):
	''' monitor requested product to see if its price has changed '''

	def post(self):
		self.process()

	def get(self):
		self.process()

	def process(self):
		params = ['fromNum', 'toNum']
		values = {}

		for param in params:
			value = self.request.get(param)
			values[param] = value

		centralBeautys = CentralBeauty.all()
		#centralBeautys.filter("num >= ", int(values['fromNum']))
		centralBeautys.filter("num <=", int(values['toNum']))
		centralBeautys.order('-num')

		centralBeautyList = []
		for centralBeauty in centralBeautys:
			centralBeautyList.append(centralBeauty.__str__())
			#self.response.out.write(centralBeauty)

		out = {'centralBeautyList': centralBeautyList}
		self.response.out.write(simplejson.dumps(out))

#datastore
class CentralBeauty(db.Model):
	num = db.IntegerProperty()
	description = db.StringProperty()
	previewImageLarge = db.StringProperty()
	previewImage = db.StringProperty()

	def __str__(self):
		map = {'num':self.num,
				'description':self.description,
				'previewImage':self.previewImage,
				'previewImageLarge':self.previewImageLarge,
				}
		return simplejson.dumps(map)
