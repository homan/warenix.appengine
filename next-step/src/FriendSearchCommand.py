
from StatusResultView import StatusResultView

from Page import Page
from util import TimeUtil
from util import StringUtil

from datetime import timedelta
import logging

class FriendSearchCommand():
	def execute(self, fb, request):
		# global variables
		keyword = ''
		keyword_highlight = ''
		my_dst = 8
		pic_dict = {}

		'''
		logic of with friend search
		'''
		uid_commenter = request.get('friend_uid')
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

		return search_result


class FriendSearchResultView:
	def render(self, search_result, uid_commenter):
		avatar_url = "http://static.ak.fbcdn.net/pics/q_silhouette.gif"
		avatar_uid = uid_commenter

		view = StatusResultView()
		html = view.render_search_result('With-Friend', search_result, avatar_url)

		return html

def compareByPostDateDesc(x, y):
	if x['post_date'] > y['post_date']:
		return -1
	return 1

