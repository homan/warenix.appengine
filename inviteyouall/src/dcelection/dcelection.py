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

import re

import html5lib
from html5lib import treebuilders, treewalkers, serializer
from html5lib.filters import sanitizer

districts = [
		{
			'constituency':'central&western',
			'member_url':'http://e.had.pbase.net/east_d/chinese/member_detail.htm',
			},
		{
			'constituency':'wanchai',
			'member_url':'http://www.districtcouncils.gov.hk/wc_d/chinese/member_detail.htm',
			},
		{
			'constituency':'eastern',
			'member_url':'http://e.had.pbase.net/east_d/chinese/member_detail.htm',
			},
		{
			'constituency':'southern',
			'member_url':'http://www.districtcouncils.gov.hk/south_d/chinese/member_detail.htm',
			},

		{
			'constituency':'yautsimmong',
			'member_url':'http://www.districtcouncils.gov.hk/ytm_d/chinese/member_detail.htm',
			},
		{
			'constituency':'shamshuipo',
			'member_url':'http://www.districtcouncils.gov.hk/ssp_d/chinese/member_detail(08-11).htm',
			},

		{
			'constituency':'kowlooncity',
			'member_url':'http://www.districtcouncils.gov.hk/klc_d/chinese/member_detail.htm',
			},
		{
			'constituency':'kwuntong',
			'member_url':'http://www.districtcouncils.gov.hk/kt_d/chinese/member_detail_2008.htm',
			},

		{
			'constituency':'tsuenwan',
			'member_url':'http://www.districtcouncils.gov.hk/tw_d/chinese/member_detail.htm',
			},
		{
			'constituency':'tuenmun',
			'member_url':'http://www.districtcouncils.gov.hk/tm_d/chinese/member_detail.htm',
			},

		{
			'constituency':'yuenlong',
			'member_url':'http://www.districtcouncils.gov.hk/yl_d/chinese/member_detail.htm',
			},
		{
			'constituency':'north',
			'member_url':'http://www.districtcouncils.gov.hk/north_d/chinese/member_detail.htm',
			},

		{
			'constituency':'taipo',
			'member_url':'http://www.districtcouncils.gov.hk/tp_d/chinese/member_detail.htm',
			},
		{
			'constituency':'saikung',
			'member_url':'http://www.districtcouncils.gov.hk/sk_d/chinese/member_detail.htm',
			},

		{
			'constituency':'shatin',
			'member_url':'http://www.districtcouncils.gov.hk/st_d/chinese/member_detail.htm',
			},
		{
			'constituency':'kwaitsing',
			'member_url':'http://www.districtcouncils.gov.hk/kc_d/chinese/member_detail.htm',
			},

		{
			'constituency':'islands',
			'member_url':'http://www.districtcouncils.gov.hk/island_d/chinese/member_detail3.htm',
			},
		]

class QueueParseNominateHandler(webapp.RequestHandler):
	''' queue parse nominate job '''

	def post(self):
		self.process()

	def get(self):
		self.process()

	def process(self):

		for district in districts:
			constituency = district['constituency']
			url = 'http://www.elections.gov.hk/dc2011/pdf/2809_%s_c.txt' % constituency

			taskqueue.add(url='/dcelection/nominate/parse/',
					params={
						'url':url,
						'constituency':constituency})

		self.response.out.write('queue parse nominate completed')

class ParseNominateHandler(webapp.RequestHandler):
	''' parse nominate from a constituency'''

	def post(self):
		self.process()

	def get(self):
		self.process()

	def process(self):
		#url = 'http://www.elections.gov.hk/dc2011/pdf/2809_%s_c.txt' % district['constituency']
		url = self.request.get('url')
		constituency = self.request.get('constituency')

		logging.info(url)
		html = urlfetch.fetch(url)
		content = html.content.decode("big5", 'ignore')

		state = 0;
		STATE_CONTENT_START = 1
		STATE_CONTENT_END = 2

		lines = content.split('\n')
		for line in lines:
			line = line.strip()
			if len(line) > 0:
				if state == 0:
					if line[0] == '-':
						state = STATE_CONTENT_START
						logging.info('change state to start')
				elif state == STATE_CONTENT_START:
					if line[0] == '-':
						state = STATE_CONTENT_END
						logging.info('change state to end')
					else:
						self.parseLine(line, constituency)
				elif state == STATE_CONTENT_END:
					pass

		self.response.out.write('parse nominate completed')

	last_code = ''
	def parseLine(self, line, constituency):
		fields = line.split(' ')

		nominate = Nominate()
		nominate.constituency_eng = constituency

		i = 0
		for field in fields:
			if len(field) > 0:
				if i == 0:
					nominate.code = field
					i+=1
				elif i == 1:
					nominate.constituency = field
					i+=1
				elif i == 2:
					nominate.name = field
					i+=1
				elif i == 3:
					if field == u'\u7537' or field == u'\u5973':
						nominate.gender = field
						i+=1
					else:
						nominate.alias = field
				elif i == 4:
					nominate.occupation = field
					i+=1
				elif i == 5:
					if field[0] != '2':
						nominate.political = field
					i+=1

		nominate.put()

class SetupHandler(webapp.RequestHandler):
	''' reset datastore and setup task queues for parsing '''

	def post(self):
		self.process()

	def get(self):
		self.process()

	def process(self):
		self.remove_datastore_type('DCMember')
		self.remove_datastore_type('Nominate')

	def remove_datastore_type(self, datastore_type):
		try:
			while True:
				q = db.GqlQuery("SELECT __key__ FROM %s" % datastore_type)
				assert q.count()
				db.delete(q.fetch(200))
		except Exception, e:
			self.response.out.write(repr(e)+'\n')
			pass

		logging.info('%s removed' % datastore_type)

class QueueParseMemberHandler(webapp.RequestHandler):
	''' monitor requested product to see if its price has changed '''

	def post(self):
		self.process()

	def get(self):
		self.process()

	def process(self):
		for district in districts:
			url = district['member_url']
			constituency = district['constituency']
			logging.info('fetching [%s] dc members from url [%s]' % (constituency, url))

			taskqueue.add(url='/dcelection/member/parse/',
					params={
						'url':url,
						'constituency':constituency})

		self.response.out.write('queue parse member cmonitor requested product to see if its price has changed ompleted')

class ParseMemberHandler(webapp.RequestHandler):
	''' parse existing dc member '''

	def post(self):
		self.process()

	def get(self):
		self.process()

	def process(self):

		url = self.request.get('url')
		constituency = self.request.get('constituency')

		logging.info('fetching [%s] dc members from url [%s]' % (constituency, url))

		response = urlfetch.fetch(url)
		html = response.content
		html = html.decode('big5', 'ignore')

		p = MemberParser()
		resutl = p.parse(html, constituency)

		self.response.out.write('parse member completed')

class MemberParser:
	def parse(self, html, constituency):
		p = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
		dom_tree = p.parse(html)
		walker = treewalkers.getTreeWalker("dom")
		stream = walker(dom_tree)

		s = serializer.htmlserializer.HTMLSerializer(omit_optional_tags=True,
				strip_whitespace=True,
				escape_rcdata=True)

		output_generator = s.serialize(stream)

		state= 0
		STATE_BEGIN_MEMBER = 1
		STATE_FOUND_NAME=2
		STATE_BEGIN_SPAN = 3
		STATE_END_SPAN = 4

		member_state = 0
		STATE_CAPACITY = 5
		STATE_OCCUPATION = 6
		STATE_POLITICAL=7
		STATE_SERVICE=8
		STATE_ADDRESS=9
		STATE_TEL=10
		STATE_FAX=11
		STATE_EMAIL=12
		STATE_NAME=13
		STATE_HOMEPAGE=14

		span_buffer = ''
		last_span_buffer = ''
		field_name_list = [
						u'\u5e2d\u4f4d\uff1a',
						u'\u8077\u696d\uff1a',
						u'\u6240\u5c6c\u653f\u6cbb\u5718\u9ad4\uff1a',
						u'\u5340\u8b70\u6703\u670d\u52d9\uff1a',
						u'\u5730\u5740\uff1a',
						u'\u96fb\u8a71\uff1a',
						u'\u50b3\u771f\uff1a',
						u'\u96fb\u90f5\u5730\u5740 :',
						u'\u96fb\u90f5\u5730\u5740\uff1a',
						u'\u7db2\u9801\uff1a',
				]
		name_filter_list = [
				u'\u8b70\u54e1',
				u'\u526f\u4e3b\u5e2d',
				u'\u4e3b\u5e2d',
				u'\u5148\u751f',
				u'\u5973\u58eb',
				',',
				'MH',
				'BBS',
				'JP',
				'GBS',
				u'\u535a\u58eb',
				'SBS',
				u'\u592a\u5e73\u7d33\u58eb',
				]

		dc_member = None

		for item in output_generator:
			data = item.strip()
			if len(data) > 0:
				#logging.info('state[%d] data[%s]' % (state, data))

				if '<table' in data:
					state = STATE_BEGIN_MEMBER
					if dc_member != None and dc_member.name != None:
						dc_member.constituency = constituency
						dc_member.put()
						logging.info('store dc_member')
					dc_member = DCMember()
					member_state = STATE_NAME
				if state == STATE_BEGIN_MEMBER:
					if '<td' in data:
						state = STATE_BEGIN_SPAN
				elif state == STATE_BEGIN_SPAN:
					if '</td' in data:
						state = STATE_BEGIN_MEMBER

						span_buffer = span_buffer.replace('<br>', '\n')
						span_buffer = self.remove_html_tags(span_buffer)


						if last_span_buffer == u'\u5e2d\u4f4d\uff1a':
							member_state = STATE_CAPACITY
							found_field_name = True
						elif last_span_buffer == u'\u8077\u696d\uff1a':
							member_state = STATE_OCCUPATION
							found_field_name = True
						elif last_span_buffer == u'\u6240\u5c6c\u653f\u6cbb\u5718\u9ad4\uff1a':
							member_state = STATE_POLITICAL
							found_field_name = True
						elif last_span_buffer == u'\u5340\u8b70\u6703\u670d\u52d9\uff1a':
							member_state = STATE_SERVICE
							found_field_name = True
						elif last_span_buffer == u'\u5730\u5740\uff1a':
							member_state = STATE_ADDRESS
							found_field_name = True
						elif last_span_buffer == u'\u96fb\u8a71\uff1a':
							member_state = STATE_TEL
							found_field_name = True
						elif last_span_buffer == u'\u50b3\u771f\uff1a':
							member_state = STATE_FAX
							found_field_name = True
						elif last_span_buffer == u'\u96fb\u90f5\u5730\u5740 :' or last_span_buffer == u'\u96fb\u90f5\u5730\u5740\uff1a':
							member_state = STATE_EMAIL
							found_field_name = True
						elif last_span_buffer == u'\u7db2\u9801\uff1a':
							member_state = STATE_HOMEPAGE

						if len(span_buffer) > 0 and  span_buffer not in field_name_list:
							if member_state == STATE_NAME:
								for filter in name_filter_list:
									span_buffer = span_buffer.replace(filter, '')
								logging.info('found name %s' % span_buffer)
								dc_member.name= span_buffer.replace('\n', '')
								member_state = 0
							elif member_state == STATE_CAPACITY:
								logging.info('found capacity %s' % span_buffer)
								dc_member.capacity= span_buffer
							elif member_state == STATE_OCCUPATION:
								logging.info('found occupation %s' % span_buffer)
								dc_member.occupation= span_buffer
							elif member_state == STATE_POLITICAL:
								logging.info('found political %s' % span_buffer)
								dc_member.political= span_buffer
							elif member_state == STATE_SERVICE:
								logging.info('found district coucil service %s' % span_buffer)
								dc_member.service= span_buffer
							elif member_state == STATE_ADDRESS:
								logging.info('found address %s' % span_buffer)
								dc_member.address= span_buffer
							elif member_state == STATE_TEL:
								logging.info('found tel %s' % span_buffer)
								dc_member.tel= span_buffer
							elif member_state == STATE_FAX:
								logging.info('found fax [%s]' % span_buffer)
								dc_member.fax= span_buffer
							elif member_state == STATE_EMAIL:
								logging.info('found email %s' % span_buffer)
							elif member_state == STATE_HOMEPAGE:
								logging.info('found homepage %s' % span_buffer)
								dc_member.homepage = span_buffer


						last_span_buffer = span_buffer.strip()
						span_buffer = ''
						logging.info('xxxxxxxx')
					elif '<table' in data:
						state = 0
					elif 'member_info.htm' in data:
						state = 0
					else:
						span_buffer += data
						#logging.info('>>>[%s]' % data)



		return 'finish'

	def remove_html_tags(self, data):
		p = re.compile(r'<.*?>')
		return p.sub('', data)


class Nominate(db.Model):
	code = db.StringProperty()
	constituency_eng = db.StringProperty()
	constituency = db.StringProperty()
	name = db.StringProperty()
	alias = db.StringProperty()
	gender = db.StringProperty()
	occupation  = db.StringProperty()
	political = db.StringProperty()

	def __str__(self):
		s = '%s %s %s %s %s %s' % (
				self.code,
				self.constituency,
				self.name,
				self.alias,
				self.gender,
				self.political)
		#if self.name == u'\u4faf\u91d1\u6797':
		#	s = '<b>%s</b>' % s
		return s

class DCMember(db.Model):
	constituency = db.StringProperty()
	name = db.StringProperty()
	occupation = db.StringProperty(multiline=True)
	political= db.StringProperty(multiline=True)
	service= db.StringProperty(multiline=True)
	address= db.StringProperty(multiline=True)
	tel= db.StringProperty(multiline=True)
	fax= db.StringProperty(multiline=True)
	email= db.StringProperty(multiline=True)
	homepage = db.StringProperty(multiline=True)


