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
from Page import Page

class MainPage(Page):
	def onProcess(self):
		fb = self.fb

		"""
		get request paramenters
		"""
		keyword = self.request.get('keyword')
		keyword_upper = keyword.upper()
		keyword_upper = keyword_upper.replace("\\", "\\\\")
		keyword_upper = keyword_upper.replace("'", "\\'")

		"""
		defaut is current logged in user unless specified
		"""

		uid = fb.uid
		if self.request.get('uid'):
			'''
			allow to search base on given uid
			'''
			uid = self.request.get('uid')

		"""
		construct view
		"""
		v = View()
		self.out (v.html_head())
		self.out (v.html_begin_body())

		self.out (v.html_head_div())


		"""
		get request paramenters
		"""
		keyword = self.request.get('keyword')
		keyword_upper = keyword.upper()
		keyword_upper = keyword_upper.replace("\\", "\\\\")
		keyword_upper = keyword_upper.replace("'", "\\'")

		check_period = self.request.get('check_period')
		if check_period:
			period = int(check_period)

			if period > 0:
				period = time.time() - int(check_period)

		"""
		do nothing when there is no keyword given
		"""
		if keyword == "":
			return


		logging.info('get pic_dict')
		pic_dict = self.get_pic_dict(uid, fb)

		keyword_highlight = self.hightlight_message(keyword)


		logging.info('get my_dst')
		my_dst = self.get_my_dst(uid, fb)

		logging.info("my_dst = %s" % my_dst)

		if self.request.get('check_status'):
			"""
			query facebook for status message
			"""
			my_search_query = "select uid, status_id, message, time from status where uid='%s' and strpos(upper(message), '%s') >= 0 and time > %d" % (uid, keyword_upper, period)
			logging.info(my_search_query)
			my_search_result_set = fb.fql.query(my_search_query)
			logging.info('result set size = %s' % len(my_search_result_set))

			self.out (v.html_begin_content_div(heading="Searching %s in status message found %d result") % (keyword_highlight, len(my_search_result_set)))

			for result in my_search_result_set:
				feed_url = 'http://www.facebook.com/profile.php?id=%s&v=feed&story_fbid=%s' % (uid, result['status_id'])
				message = self.replace_insensitive(result['message'], keyword, keyword_highlight)
				post_time = self.timezonetime(result['time'], timedelta(hours=my_dst))

				avatar_url = "http://static.ak.fbcdn.net/pics/q_silhouette.gif"
				if result['uid'] in pic_dict:
					avatar_url = pic_dict[result['uid']]

				self.out (
				v.html_search_result(
				avatar_url=avatar_url,
				post_date=time.ctime(post_time),
				message_url=feed_url,
				message_text=message,
				))

			self.out (v.html_end_content_div())

		if self.request.get('check_comment'):
			"""
			query facebook for all comments related to all my status
			"""

			my_post_id_query = "select concat(%s, '_', status_id) from status where uid='%s' and time > %d" % (uid, uid, period)
			my_comment_query = "select fromid, post_id, text, time from comment where post_id in (%s) and strpos(upper(text), '%s') >= 0 and time > %d" % (my_post_id_query, keyword_upper, period)
			logging.info(my_comment_query)
			my_comment_result_set = fb.fql.query(my_comment_query)
			logging.info('result set size = %s' % len(my_comment_result_set))

			self.out (v.html_begin_content_div(heading="Searching %s in comment found %d result") % (keyword_highlight, len(my_comment_result_set)))


			"""
			display comment search result
			"""

			for result in my_comment_result_set:
				status_id = result['post_id'].split('_')[1];
				feed_url = 'http://www.facebook.com/profile.php?id=%s&v=feed&story_fbid=%s' % (uid, status_id)
				message = self.replace_insensitive(result['text'], keyword, keyword_highlight)

				avatar_url = "http://static.ak.fbcdn.net/pics/q_silhouette.gif"
				if result['fromid'] in pic_dict:
					avatar_url = pic_dict[result['fromid']]

				post_time = self.timezonetime(result['time'], timedelta(hours=my_dst))


				self.out (
				v.html_search_result(
				avatar_url=avatar_url,
				post_date=time.ctime(post_time),
				message_url=feed_url,
				message_text=message,
				))

			self.out (v.html_end_content_div())

		"""
		end division
		"""

		self.out (v.html_end_content_div())
		self.out (v.html_end_body())

	def getConfFile(self):
		return 'app.conf'

	def hightlight_message(self, message="", color='yellow'):
		return '<font style="background-color: %s">%s</font>' % (color, message)

	def replace_insensitive(self, string, target, replacement):
		no_case = string.lower()
		index = no_case.find(target.lower())
		if index >= 0:
			result = string[:index] + replacement + string[index + len(target):]
			return result
		else: # no results so return the original string
			return string

	def timezonetime(self, timestamp, delta=timedelta()):
		delta_seconds = delta.days * 86400 + delta.seconds
		timezone_timestamp = timestamp + delta_seconds
		return timezone_timestamp

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

	def get_my_dst(self, uid, fb):
		"""
		get user timezone
		"""
		my_timezone_query = "select timezone from standard_user_info where uid = '%s'" % uid
		logging.info(my_timezone_query)
		my_timezone_result = fb.fql.query(my_timezone_query)
		my_dst = 0
		for result in my_timezone_result:
			my_dst = result['timezone']
		return my_dst

