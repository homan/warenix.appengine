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
from View import View

class FacebookApp(webapp.RequestHandler):
	def post(self):
		self.safe_process()

	def get(self):
		self.safe_process()

	def safe_process(self):
		try:
			fb_sig_session_key = self.request.get('fb_sig_session_key')
			self.session_object = memcache.get(fb_sig_session_key)
			if self.session_object is None:
				self.session_object = {}
			logging.info('-start-')

			self.process()
		except DownloadError, e:
			logging.error(e)

			self.out("oops! we get an error at this moment. please try refreshing your browser. hopefully it will resume very soon")
		finally:
			memcache.set(fb_sig_session_key, self.session_object, 60)
			logging.info('-end-')

	def process(self):

		fb = self.get_fb()

		redirect_url = """
		<script language="javascript">
			top.location.replace("%s")
		</script>
		"""

		if not fb.check_session(self.request):
			url = fb.get_login_url()
			logging.info("redirect to %s" % (url))
			self.response.out.write((redirect_url % url))
			return


		self.onProcess()

	def onProcess(self):
		self.out('<ul>welcome to MyStatusSearch api</ul>')
		self.list_request(self.request)


	def out(self, string):
		self.response.out.write(string)

	def list_request(self, request):
		logging.info("MyStatusSearch: log request parameters")
		arguments = request.arguments()
		for arg in arguments:
			logging.info("received %s=[%s]" % (arg, request.get(arg)))

	def get_fb(self):

		if not 'fb' in self.session_object:
			logging.info('fb not found')
			conf = Config()
			self.fb = facebook.Facebook(conf.API_KEY, conf.SECRET_KEY)
			self.session_object['fb'] = self.fb
		else:
			logging.info('use cache fb')
			self.fb = self.session_object['fb']
		return self.fb

	def get_pic_dict(self, uid, fb):
		"""
		cache friends profile pic if uid iis logged in user
		"""
		pic_dict = {}
		if uid == fb.uid:
			profile_pic_query = "select id, pic_square from profile where id in (select uid2 FROM friend where uid1 = '%s') or id = '%s'" % (uid, uid)
			logging.info(profile_pic_query)
			my_profile_pic_result = fb.fql.query(profile_pic_query)
			for result in my_profile_pic_result:
				friend_uid = result['id']
			       	pic_url = result['pic_square']
			       	pic_dict[friend_uid] = pic_url
		return pic_dict

class get_dst(FacebookApp):

	def onProcess(self):

		fb = self.fb()
		uid = fb.uid

		"""
		get user timezone
		"""
		my_timezone_query = "select timezone from standard_user_info where uid = '%s'" % uid
		logging.info(my_timezone_query)
		my_timezone_result = fb.fql.query(my_timezone_query)
		my_dst = 0
		for result in my_timezone_result:
			my_dst = result['timezone']

		self.out(my_dst)

class get_friends(FacebookApp):

	def onProcess(self):

		fb = self.fb()
		uid = fb.uid

		"""
		get user timezone
		"""
		my_friends_query = """
		select id, pic_square from profile where id in (
	select uid2 from friend where uid1 = '%s')""" % uid
		logging.info(my_friends_query)
		my_friends_result = fb.fql.query(my_friends_query)


		html = '''
		<form action="/MyStatusSearch/" method="post">
		<select name="friends" multiple="multiple" height="100px">
		'''
		friends = {}
		for result in my_friends_result:
			html += """<option value="%s" style="width:50px;height:50px;margin:5px;background-image:url(%s);"></option><br/>""" % (
					result['id'], result['pic_square'])

		html += """
			<input type="submit" />
		</select>
		</form>"""

		self.out(html)

def main():
	application = webapp.WSGIApplication([ ('/', FacebookApp),
	  ('/MyStatusSearch/api/*', FacebookApp),
	  ('/MyStatusSearch/api/get_dst/*', get_dst),
	  ('/MyStatusSearch/api/get_friends/*', get_friends),
	], debug=True)

	wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()

