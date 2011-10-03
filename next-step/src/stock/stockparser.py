from google.appengine.api import urlfetch

from HTMLParser import HTMLParser
from BeautifulSoup import BeautifulSoup

import logging

class AAStockParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)

		self.result = []

	def getQuote(self, stock_code):

		url = "http://freequote.aastocks.com/TC/LTP/RTQuote.aspx?&symbol=%05d" % (int(stock_code))
		feed = urlfetch.fetch(url, deadline=10)

		soup = BeautifulSoup(feed.content)
		html = soup.prettify()

		self.feed(html)


		template_values = {}

		self.result.append(self.stock_price_change)
		self.result.append(self.stock_name)
		self.result.append(self.refresh_time)

		template_values = {}

		i = 0
		for r in self.result:
			key = "f%d" % i
			template_values[key] = r
			i += 1

		return template_values


	result = []
	found_div = False
	found_span = False
	found_stock_name = False
	found_refresh_time = False
	stock_price_change = 'static'
	stock_name = ''
	refresh_time = ''

	def handle_starttag(self, tag, attrs):

		for pairs in attrs:
			if 'class' in pairs:
				# value contains whole value string
				value = pairs[1]

				if value == "tb-h1":
					self.found_div = True
				elif value == 'floatL f15':
					self.found_stock_name = True

				if value == 'pos':
					self.stock_price_change = 'pos'
				elif value == 'neg':
					self.stock_price_change = 'neg'

		if self.found_div == True and tag=='td':
			self.found_span = True

	def handle_data(self, data):
		data = data.strip()
		if len(data) == 0:
			return

		if self.found_refresh_time == False and len(data) == 16 and data[4] == '-':
			self.refresh_time = data
			self.found_refresh_time = False

		if self.found_div and self.found_span == True:
			if len(data) > 0:
				self.result.append(data);
				self.row_count -= 1
				if self.row_count == 0:
					self.found_div = False

		if self.found_stock_name:
			self.stock_name = data
			self.found_stock_name = False

	# only print 25 rows from the found_div
	row_count = 25
