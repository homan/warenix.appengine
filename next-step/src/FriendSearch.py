from Page import Page
from util import TimeUtil
from util import StringUtil

import time
from datetime import timedelta

import wsgiref.handlers
from google.appengine.ext import webapp
from StatusResultView import StatusResultView
from FriendSearchCommand import FriendSearchCommand
from FriendSearchCommand import FriendSearchResultView

import logging

class TestPage(Page):
	def onProcess(self):
		self.list_request(self.request)

		#self.showFriendSelector()

		# global variables
		fb = self.fb
		keyword = ''
		keyword_highlight = ''
		my_dst = 8
		pic_dict = {}

		'''
		logic of with friend search
		'''
		uid_commenter = self.request.get('friend_uid')
		if uid_commenter:
			pass
		else:
			return
		uid_owner = fb.uid
		timeUtil = TimeUtil()
		begin_time = timeUtil.timeBeforeNow(604800)

		fql = '''
		select post_id, fromid, time, text
		from comment
	       	where fromid = '%(uid_commenter)s'
		and post_id in (
			select concat('%(uid_owner)s', '_', status_id)
		       	from status
		       	where uid = '%(uid_owner)s'
			and time > %(begin_time)d
		)
		''' %{
			'uid_commenter': uid_commenter,
			'uid_owner': uid_owner,
			'begin_time': begin_time,
		}
		logging.info(fql)

		stringUtil = StringUtil()

		search_result = []
		result_set = fb.fql.query(fql)

		self.out('result found %d' % len(result_set))
		for result in result_set:
			feed_url = 'http://www.facebook.com/profile.php?id=%s&v=feed&story_fbid=%s' % (fb.uid, result['post_id'])
			message = stringUtil.replace_insensitive(result['text'], keyword, keyword_highlight)
			post_time = timeUtil.timezonetime(result['time'], timedelta(hours=my_dst))

			r = {}
			r['post_date'] = post_time
			r['avatar_url'] = ''
			r['message_url'] = feed_url
			r['message_text'] = message

			search_result.append(r)

		search_result.sort(cmp=compareByPostDateDesc)

		avatar_url = "http://static.ak.fbcdn.net/pics/q_silhouette.gif"
		avatar_uid = uid_commenter
		if pic_dict.has_key(avatar_uid):
			avatar_url = pic_dict[avatar_uid]
		else:
			avatar_url = "http://static.ak.fbcdn.net/pics/q_silhouette.gif"

		withFriendView = StatusResultView()
		self.out(
			withFriendView.render_search_result('With-Friend', search_result, avatar_url)
			)




class FriendSearchHandler(Page):
	def onProcess(self):
		self.list_request(self.request)

		command = FriendSearchCommand()
		result = command.execute(self.fb, self.request)

		view = FriendSearchResultView()
		logging.info(result)
		html = view.render(result, self.fb.uid)

		self.out(html)

def compareByPostDateDesc(x, y):
	if x['post_date'] > y['post_date']:
		return -1
	return 1

def main():
	application = webapp.WSGIApplication([
# ('/', MainPage),
	  ('/MyStatusSearch/friend_search/*', FriendSearchHandler),
	], debug=True)

	wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
	main()

