import wsgiref.handlers
from google.appengine.ext import webapp

#from offline import TestPage

import stock
import mystatussearch

url_handlers = [
	# stock
	('/stock/*', stock.StockHandler),
	('/stock/quote/*', stock.StockQuoteHandler),
	('/stock/monitor/*', stock.StockMonitor),
	('/stock/monitor/worker/*', stock.StockMonitorWorker),

	# mystatussearch
	('/mystatussearch/*', mystatussearch.MainPage),

	]

def main():
	application = webapp.WSGIApplication(url_handlers, debug=True)

	wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
	main()

