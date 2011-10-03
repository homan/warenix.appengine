import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from xml.dom.minidom import Document


class User(db.Model):
	name = db.StringProperty(required=True)

	def toXML(self):
		doc = Document()

		userNode = doc.createElement("user")

		nameNode = doc.createElement("name")
		userNode.appendChild(nameNode)
		nameText = doc.createTextNode(self.name)
		nameNode.appendChild(nameText)

		keyNode = doc.createElement("key")
		userNode.appendChild(keyNode)
		keyText = doc.createTextNode(str(self.key()))
		keyNode.appendChild(keyText)

		return userNode

class Email(db.Model):
	user = db.ReferenceProperty(User, collection_name='emails')
	addr = db.EmailProperty(required=True)
	mail_type = db.StringProperty()


class GlobalIndex(db.Model):
	maxIndex = db.IntegerProperty(required=True, default=1)
	type = db.StringProperty(required=True)

	def GetMaxIndex(type):
		result = db.GqlQuery("SELECT * FROM GlobalIndex where type=:type", type=type)

		if result.count() == 1:
			current = result[0]
			current.maxIndex += 1
			current.put()

			return current.maxIndex
		else:
			current = GlobalIndex(type=type)
			current.put()

			return current.maxIndex

	GetMaxIndex = staticmethod(GetMaxIndex)

class Poll(db.Model):
	index = db.IntegerProperty(required=False)
	background = db.StringProperty(required=True)
	owner = db.ReferenceProperty(User)

	def toXML(self, includeChoice=False):
		doc = Document()

		pollNode = doc.createElement("poll")

		indexNode = doc.createElement("index")
		pollNode.appendChild(indexNode)
		indexText = doc.createTextNode(str(self.index))
		indexNode.appendChild(indexText)

		backgroundNode = doc.createElement("background")
		pollNode.appendChild(backgroundNode)
		backgroundText = doc.createTextNode(self.background)
		backgroundNode.appendChild(backgroundText)

		ownerNode = doc.createElement("owner");
		pollNode.appendChild(ownerNode)
		ownerText = doc.createTextNode(self.owner.name)
		ownerNode.appendChild(ownerText)

		keyNode = doc.createElement("key")
		pollNode.appendChild(keyNode)
		keyText = doc.createTextNode(str(self.key()))
		keyNode.appendChild(keyText)

		if includeChoice:
			choiceNode = doc.createElement("choices")
			pollNode.appendChild(choiceNode)


			for choice in self.choices:
				choiceNode.appendChild(choice.toXML())


		return pollNode

class Choice(db.Model):
	description = db.StringProperty(required=True)
	count = db.IntegerProperty(default=0)
	poll = db.ReferenceProperty(Poll, collection_name='choices')

	def toXML(self):
		doc = Document()

		choiceNode = doc.createElement("choice")

		descriptionNode = doc.createElement("description")
		descriptionText = doc.createTextNode(self.description)
		descriptionNode.appendChild(descriptionText)
		choiceNode.appendChild(descriptionNode)


		countNode = doc.createElement("count")
		choiceNode.appendChild(countNode)
		countText = doc.createTextNode(str(self.count))
		countNode.appendChild(countText)

		keyNode = doc.createElement("key")
		choiceNode.appendChild(keyNode)
		keyText = doc.createTextNode(str(self.key()))
		keyNode.appendChild(keyText)

		return choiceNode

class ResultXML():

	doc = Document()

	def getRoot(self, doc):
		root = doc.createElement("next-step")
		doc.appendChild(root)
		return root


	def setResultStatus(self, root, resultStatus):
		resultStatusNode = self.doc.createElement("resultStatus")
		resultStatusText = self.doc.createTextNode(resultStatus)
		resultStatusNode.appendChild(resultStatusText)
		root.appendChild(resultStatusNode)

	def setResultData(self, root, resultData):
		resultDataNode = self.doc.createElement("resultData")
		resultDataNode.appendChild(resultData)
		root.appendChild(resultDataNode)

	def toXML(self, doc):
		return doc.toprettyxml()

class HTTPRequest():

	def GetRequest(request, name=""):
		value = request.get(name)

		if (value):
			return cgi.escape(value)
		else:
			return None

	GetRequest = staticmethod(GetRequest)

class GetChoiceHandler(webapp.RequestHandler):

	def post(self):
		self.process();

	def get(self):
		self.process();

	def process(self):
		choiceKey = HTTPRequest.GetRequest(self.request, "choiceKey")

		doc = Document()
		resultXML = ResultXML()
		root = resultXML.getRoot(doc)

		if (choiceKey):

			choiceKey = db.Key(choiceKey)
			result = db.GqlQuery("SELECT * FROM Choice WHERE __key__ = :choiceKey", choiceKey=choiceKey)

			if (result.count() == 1):
				choice = result[0]
				resultXML.setResultStatus("ok")
				resultXML.setResultData(choice.toXML())
			else:
				resultXML.setResultStatus(root, "choice does not exist")

		else:
			resultXML.setResultStatus(root, "?choiceKey=<>")

		self.response.out.write(resultXML.toXML(doc))

		del resultXML


class VoteChoiceHandler(webapp.RequestHandler):

	def post(self):
		self.process();

	def get(self):
		self.process();

	def process(self):
		username = HTTPRequest.GetRequest(self.request, "username")
		choiceKey = HTTPRequest.GetRequest(self.request, "choiceKey")

		doc = Document()
		resultXML = ResultXML()
		root = resultXML.getRoot(doc)

		if (choiceKey and username):

			result = db.GqlQuery("SELECT * FROM User where name=:name", name=username)

			if result.count() == 1:
				user = result[0]

				choiceKey = db.Key(choiceKey)
				result = db.GqlQuery("SELECT * FROM Choice WHERE __key__ = :choiceKey", choiceKey=choiceKey)

				if result.count() == 1:
					choice = result[0]
					choice.count = choice.count + 1
					choice.put()

					resultXML.setResultStatus(root, "ok")
					resultXML.setResultData(root, choice.toXML())
				else:
					resultXML.setResultStatus(root, "choice does not exist")

			else:
				resultXML.setResultStatus(root, "user does not exist")
		else:
			resultXML.setResultStatus(root, "?username=<>&choiceKey=<>")

		self.out(resultXML.toXML(doc))

	def out(self, message):
		self.response.out.write(message)


class PutChoiceHandler(webapp.RequestHandler):

	def post(self):
		self.process();

	def get(self):
		self.process();

	def process(self):
		pollKey = HTTPRequest.GetRequest(self.request, "pollKey")
		description = HTTPRequest.GetRequest(self.request, "description")

		doc = Document()
		resultXML = ResultXML()
		root = resultXML.getRoot(doc)

		if (pollKey and description):
			pollKey = db.Key(pollKey)
			result = db.GqlQuery("SELECT * FROM Poll WHERE __key__ = :pollKey", pollKey=pollKey)

			if(result):
				poll = result[0]

				if (poll):
					choice = Choice(
							description=description,
							count=0,
							poll=poll)

					choice.put()

					resultXML.setResultStatus(root, "ok")
					resultXML.setResultData(root, choice.toXML())
				else:
					resultXML.setResultStatus(root, "poll not found")
		else:
			resultXML.setResultStatus(root, "?pollKey=<>&description=<>")

		self.out(resultXML.toXML(doc))

	def out(self, message):
		self.response.out.write(message)



class GetPollHandler(webapp.RequestHandler):

	def post(self):
		self.process();

	def get(self):
		self.process();

	def process(self):
		pollKey = HTTPRequest.GetRequest(self.request, 'pollKey')
		pollIndex = HTTPRequest.GetRequest(self.request, 'pollIndex')

		resultXML = ResultXML()
		doc = Document()
		root = resultXML.getRoot(doc)

		if (pollKey):
			pollKey = db.Key(pollKey)
			result = db.GqlQuery("SELECT * FROM Poll WHERE __key__ = :pollKey", pollKey=pollKey)

			if result:
				poll = result[0]

				resultXML.setResultStatus(root, "ok")
				resultXML.setResultData(root, poll.toXML(includeChoice=False))

			else:
				resultXML.setResultStatus(root, "poll does not exist")
		else:
			if (pollIndex):
				pollIndex = int(pollIndex)
				result = db.GqlQuery("SELECT * FROM Poll WHERE index = :pollIndex", pollIndex=pollIndex)

				poll = result[0]
				resultXML.setResultStatus(root, "ok")
				resultXML.setResultData(root, poll.toXML(includeChoice=True))

			else:
				resultXML.setResultStatus(root, "?pollIndex=<> or ?pollKey=<>")

		self.out(resultXML.toXML(doc))


	def out(self, message):
		self.response.out.write(message)


class PutPollHandler(webapp.RequestHandler):

	def post(self):
		self.process();

	def get(self):
		self.process();

	def process(self):
		username = HTTPRequest.GetRequest(self.request, 'username')
		background = HTTPRequest.GetRequest(self.request, 'background')

		doc = Document()
		resultXML = ResultXML()
		root = resultXML.getRoot(doc)

		if (username and background):

			result = db.GqlQuery("SELECT * FROM User where name=:name", name=username)

			if result.count() == 1:
				user = result[0]

				poll = Poll(
						index = GlobalIndex.GetMaxIndex(type="poll"),
						owner=user,
						background=background
						)

				poll.put()

				resultXML.setResultStatus(root, "ok")
				resultXML.setResultData(root, poll.toXML())
			else:
				resultXML.setResultStatus(root, "user does not exist")
		else:
			resultXML.setResultStatus(root, "?username=<>&background=<>")

		self.out(resultXML.toXML(doc))


	def out(self, message):
		self.response.out.write(message)


class BrowsePollHandler(webapp.RequestHandler):

	def post(self):
		self.process();

	def get(self):
		self.process();

	def process(self):
		startIndex = HTTPRequest.GetRequest(self.request, 'startIndex')
		limit = HTTPRequest.GetRequest(self.request, 'limit')
		resultXML = ResultXML()

		doc = Document()
		resultXML = ResultXML()

		root = resultXML.getRoot(doc)

		if (startIndex and limit):

			startIndex = int(startIndex)
			endIndex = startIndex + int(limit)

			result = db.GqlQuery("SELECT * FROM Poll WHERE index >= :startIndex and index < :endIndex",
								startIndex = startIndex, endIndex = endIndex)

			resultXML.setResultStatus(root, "ok")
			for poll in result:
				resultXML.setResultData(root, poll.toXML(includeChoice=True))
				#self.out("%s, %s, %d<br>" % (poll.key(), poll.background, poll.index))

			self.out(resultXML.toXML(doc))

		else:
			resultXML.setResultStatus("?name=<>&background=<>")
			self.out(resultXML.toXML())


	def out(self, message):
		self.response.out.write(message)


class PutUserHandler(webapp.RequestHandler):

	def post(self):
		self.process();

	def get(self):
		self.process();

	def process(self):
		username = HTTPRequest.GetRequest(self.request, 'username')

		doc = Document()
		resultXML = ResultXML()
		root = resultXML.getRoot(doc)

		if (username):
			result = db.GqlQuery("SELECT * FROM User WHERE name=:username", username=username)

			if result.count() == 0:
				user = User(name=username)
				user.put()

				resultXML.setResultStatus(root, "ok")
				resultXML.setResultData(root, user.toXML())
			else:
				resultXML.setResultStatus(root, "user already exists")
		else:
			resultXML.setResultStatus(root, "?username=<>")

		self.out(resultXML.toXML(doc))


	def out(self, message):
		self.response.out.write(message)


class GetUserHandler(webapp.RequestHandler):

	def post(self):
		self.process();

	def get(self):
		self.process();

	def process(self):
		username = HTTPRequest.GetRequest(self.request, 'username')

		doc = Document()
		resultXML = ResultXML()
		root = resultXML.getRoot(doc)

		if (username):
			result = db.GqlQuery("SELECT * FROM User WHERE name=:username", username=username)

			if result.count() == 1:
				user = result[0]
				resultXML.setResultStatus(root, "ok")
				resultXML.setResultData(root, user.toXML())
			else:
				resultXML.setResultStatus(root, "user does not exist")
		else:
			resultXML.setResultStatus(root, "?username=<>")

		self.out(resultXML.toXML(doc))


	def out(self, message):
		self.response.out.write(message)

application = webapp.WSGIApplication(
		[
#			('/choice/*', ChoiceHandler),
			('/choice/vote/*', VoteChoiceHandler),
			('/choice/put/*', PutChoiceHandler),
			('/choice/get/*', GetChoiceHandler),
			('/poll/put/*', PutPollHandler),
			('/poll/get/*', GetPollHandler),
			('/poll/browse/*', BrowsePollHandler),
			('/user/put/*', PutUserHandler),
			('/user/get/*', GetUserHandler)

		],
		debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
