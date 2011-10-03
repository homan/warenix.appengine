#!/usr/bin/env python

import os
import wsgiref.handlers

from google.appengine.api.labs import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import memcache

import logging

from stockparser import AAStockParser

from google.appengine.api import urlfetch
from xml.dom import minidom

class StockHandler(webapp.RequestHandler):
	def get(self):
		template_values = {}
		path = os.path.join(os.path.dirname(__file__), 'stock.template')
		self.response.out.write(template.render(path, template_values))

		status = memcache.get('StockMonitor')
		if status != '':
			self.response.out.write(status)
			# clear status
			memcache.delete(key='StockMonitor')


class StockQuoteHandler(webapp.RequestHandler):
	def get(self):
		stock_code = self.request.get('stock_code')
		stock_code = stock_code.strip()

		template_values = {}
		l = 0

		if stock_code == "":
			self.response.out.write(getHSI())
			#self.response.out.write('invalid stock_code')
			return

		myParser = stockparser.AAStockParser()
		template_values = myParser.getQuote(stock_code)

		l = len(template_values)
		if l < 28:
			self.response.out.write('invalid stock_code')
			return


		output_list = [1, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 25, 26, 27 ]
		k = 'f%d' % output_list[0]
		self.response.out.write(template_values[k])

		i = 1
		l = len(output_list)
		separator = '@@@'

		while i < l:
			k = 'f%d' % output_list[i]
			self.response.out.write('%s%s' % (separator, template_values[k]))
			i += 1

def getHSI():
	logging.info("get hsi")
	url = "http://www.hsi.com.hk/HSI-Net/ql//HSI-Net/HSI-Net?cmd=simpleindex"
	feed = urlfetch.fetch(url, deadline=10)
	dom = minidom.parseString(feed.content)

	all_index_node = dom.childNodes[0].getElementsByTagName("index")
	for node in all_index_node:             
		index_code = node.getAttribute('code').strip()
		if index_code == "HSI":
			hsi_current = node.getAttribute('current')
			hsi_change = node.getAttribute('change')

			return "%s@@@%s" % (hsi_current, hsi_change)

class StockMonitor(webapp.RequestHandler):
	def get(self):
		stock_code = self.request.get('stock_code').strip()
		target_price = self.request.get('target_price').strip()

		if stock_code == '':
			return

		worker = StockMonitorWorker()
		worker.enque(stock_code, target_price)

class StockMonitorWorker(webapp.RequestHandler):
	def post(self):
		self.process()

	def get(self):
		self.process()

	def process(self):
		stock_code = self.request.get('stock_code')
		target_price = float(self.request.get('target_price'))


		if stock_code == '' or target_price == '':
			return

		myParser = AAStockParser()
		result = myParser.getQuote(stock_code)
		current_price = float(result['f4'])

		if current_price >= target_price:
			status = '%s reached target %f' % (stock_code, target_price)
			memcache.set(key='StockMonitor', value=status)
		else:
			# enque
			pass


	def enque(self, stock_code, target_price):
		url = '/stock/monitor/worker/'
		params = {
			'stock_code': stock_code,
			'target_price': target_price,
		}
		taskqueue.add(url=url, params=params)
