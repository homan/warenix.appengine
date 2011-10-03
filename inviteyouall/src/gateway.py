import wsgiref.handlers
from google.appengine.ext import webapp

#from inviteyouall import InviteYouAllRobot
from centralbeauty import StoreCentralBeautyHandler
from centralbeauty import GetCentralBeautyHandler
from centralbeauty import ListCentralBeautyHandler

from dcelection import SetupHandler
from dcelection import ParseNominateHandler
from dcelection import QueueParseNominateHandler
from dcelection import ParseMemberHandler
from dcelection import QueueParseMemberHandler


url_handlers = [

	# central beauty
	('/centralbeauty/put/.*', StoreCentralBeautyHandler),
	('/centralbeauty/get/.*', GetCentralBeautyHandler),
	('/centralbeauty/list/.*', ListCentralBeautyHandler),
	#('/_wave/.*', InviteYouAllRobot),

	# dcelection
	('/dcelection/setup/.*', SetupHandler),
	('/dcelection/member/parse/.*', ParseMemberHandler),
	('/dcelection/member/queue/.*', QueueParseMemberHandler),
	('/dcelection/nominate/parse/.*', ParseNominateHandler),
	('/dcelection/nominate/queue/.*', QueueParseNominateHandler),
	]

def main():
	application = webapp.WSGIApplication(url_handlers, debug=True)

	wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
	main()

