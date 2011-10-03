from datetime import timedelta
import time

class TimeUtil:
	def timeBeforeNow(self, check_period):
		period = int(check_period)

		if period > 0:
			period = time.time() - int(check_period)

		return period

        def timezonetime(self, timestamp, delta=timedelta()):
		''' get a timestamp in particular timezone
		'''
                delta_seconds = delta.days * 86400 + delta.seconds
                timezone_timestamp = timestamp + delta_seconds
                return timezone_timestamp

class StringUtil:
	def hightlight_message(self, message="", color='yellow'):
		return '<font style="background-color: %s">%s</font>' % (color, message)

	def replace_insensitive(self, string, target, replacement):
		no_case = string.lower()
		index = no_case.find(target.lower())
		if index >= 0:
			result = string[:index] + replacement + string[index + len(target):]
			return result
		else: # no results so return the original string
			return string
