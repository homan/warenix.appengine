#!/usr/bin/env python

import cgi
from datetime import timedelta
import time
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.api.urlfetch import DownloadError
from google.appengine.api import memcache

import facebook
import logging

from Config import Config

class Page(webapp.RequestHandler):


	''' entry point '''
	def post(self):
		self.safe_process()

	def get(self):
		self.safe_process()

	''' wrap all exception '''
	def safe_process(self):
		try:
			logging.info('-start-')

			self.process()
		except DownloadError, e:
			logging.error(e)

			self.out("oops! we get an error at this moment. please try refreshing your browser. hopefully it will resume very soon")
		finally:
			logging.info('-end-')


	''' common facebook process logic '''
	def process(self):

		fb = self.get_fb()

		redirect_url = """
		<script language="javascript">
			top.location.replace("%s")
		</script>
		"""

		if not fb.check_session(self.request) or not fb.added:
			url = fb.get_login_url()
			logging.info("redirect to %s" % (url))
			self.response.out.write((redirect_url % url))
			return


		self.onProcess()

	''' real class logic here '''
	def onProcess(self):
		self.list_request(self.request)

	''' override this to return path to conf file'''
	def getConfFile(self):
		return 'app.conf'

	''' helper methods '''
	def out(self, string):
		self.response.out.write(string)

	def list_request(self, request):
		logging.info("MyStatusSearch: log request parameters")
		arguments = request.arguments()
		for arg in arguments:
			logging.info("received %s=[%s]" % (arg, request.get(arg)))

	def get_fb(self):
		conf = Config(self.getConfFile())
		self.fb = facebook.Facebook(conf.API_KEY, conf.SECRET_KEY)
		return self.fb

	def isGroupAKey(self, key):
		'''
		[alphanumeric string]-[uid]
		'''
		return key[25:] == self.fb.uid


	def isGroupCKey(self, key):
		'''
		Group C : 2.[alphanumeric string]___.86400.[some number]-[uid]
		'''
		group_c_pattern = ['2', '86400', self.fb.uid]
		token = []

		alphamask = 'xxxxxxxxxxxxxxxxxxxxxx'
		mask_len = len(alphamask)

		p = 0
		q = 1
		token.append(key[p:q])

		p = mask_len + 5
		q = p + 5
		token.append(key[p:q])

		p = len(key) - len(self.fb.uid)
		q = p + len(self.fb.uid)
		token.append(key[p:q])

		return token == group_c_pattern

