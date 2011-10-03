import os
import sys
sys.path.append(os.path.abspath('..'))

from Page import Page

import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from google.appengine.ext import db

import logging

class FacebookOfflineAccess(db.Model):
	uid = db.StringProperty()
	infinite_session_key = db.StringProperty()

class AllowOfflineAccessPage(Page):
	'''
		ask user to grant offline access
	'''

	def onProcess(self):
		self.list_request(self.request)

		infinite_session_key = self.request.get('fb_sig_session_key')

		# check type of infinite session key obtained

		if self.isGroupAKey(infinite_session_key):
			# store it for later use

			offline_access = FacebookOfflineAccess(key_name = self.fb.uid)
			offline_access.uid = self.fb.uid
			offline_access.infinite_session_key = infinite_session_key
			offline_access.put()

			self.out('''
				<p>we have updated your infinite session key</p>
				<p>you can always visit this page to update it</p>
					''')
			pass
		elif self.isGroupCKey(infinite_session_key):
			# instruct user to allow offline access

			offline_access_url = self.fb.get_ext_perm_url('offline_access')
			self.out('''
				<p>oops! look like you have a group c session key, which we can't use it for offline access</p>
				<p><a href="%s">please click here to allow offline access</a></p>
				''' % (offline_access_url))

		self.out('<p>your session key: [%s]</p>' % infinite_session_key)

def main():
	application = webapp.WSGIApplication([
	  ('/offline/.*', AllowOfflineAccessPage),
	], debug=True)

	wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
	main()

