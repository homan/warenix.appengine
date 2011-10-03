import facebook
from Config import Config

session_key = ''

conf = Config('app.conf')
fb = facebook.Facebook(conf.API_KEY, conf.SECRET_KEY)
fb.session_key = session_key
fb.uid=''

result = fb.users.getInfo([fb.uid], ['name'])

result = fb.notifications.send('', 'sent from console')
print result

