import ConfigParser

class Config:

	API_KEY = ""
	SECRET_KEY = ""


	def __init__(self, conf_file='app.conf'):
		config = ConfigParser.RawConfigParser()
		config.read(conf_file)

		self.API_KEY = config.get('facebook', 'API_KEY')
		self.SECRET_KEY = config.get('facebook', 'SECRET_KEY') 
