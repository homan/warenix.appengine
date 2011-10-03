from waveapi import events
from waveapi import robot
from waveapi import element
from waveapi import appengine_robot_runner
import logging

# Events

def OnWaveletSelfAdded(event, wavelet):
	"""Invoked when the robot has been added."""
	logging.info("OnWaveletSelfAdded called")

	wavelet.title = "Invite You All - Robot"
	wavelet.root_blip.append("\nUsage: just separate your contacts, the id only,  with a comma, then click the invite button.")
	wavelet.root_blip.append("\n\nThe following blip is an example group of you and the inviteyouall robot creator.")

	# sample group
	creator_string = wavelet.creator.__str__()
	creator_id, creator_domain = creator_string.split("@")
	wavelet.reply("warenix, %s" % creator_id)

def OnWaveletBlipCreated(event, wavelet):

	logging.info("OnWaveletBlipCreated")

	logging.info("wavelet creator: %s" % wavelet.creator)
	if wavelet.creator == "rusty@a.gwave.com" or wavelet.creator == "inviteyouall@appspot.com":
		logging.info("this is not a group blip, do nothing")
		return

	logging.info("create invite button")

	new_blip = event.new_blip
	new_blip.append('\n')
	new_blip.append(element.Button("inviteButton", "Invite You All!"))

def OnFormButtonClicked(event, wavelet):
	logging.info("OnBlipSubmitted")
	blip = event.blip

	# if participant_list is based on wavelet.participants,
	# they will also be added to the wavelet,
	# which is not wanted.
	participant_id_list = blip.text.split(",")
	participant_list = blip.contributors

	for participant_id in participant_id_list:
		participant = "%s@%s" % (trim(participant_id), wavelet.domain)
		participant_list.add(participant)
		logging.info("with participants: %s" % participant)

	creaetANewWave(wavelet, participant_list)

def creaetANewWave(wavelet, participant_list):
	logging.info("creaetANewWave")

	myRobot = robot.Robot('inviteyouall',
		image_url='http://inviteyouall.appspot.com/assets/icon.png',
		profile_url='http://code.google.com/p/warenix/wiki/inviteyouall')

	newWave = myRobot.new_wave(wavelet.domain,
			participant_list,
			message=wavelet.serialize())
	newWave.submit_with(wavelet)

	logging.info("end create a new wave")

def trim(string):
	return string.strip().lstrip()


if __name__ == '__main__':
	myRobot = robot.Robot('inviteyouall',
		image_url='http://inviteyouall.appspot.com/assets/icon.png',
		profile_url='http://code.google.com/p/warenix/wiki/inviteyouall')

	myRobot.register_handler(events.WaveletSelfAdded, OnWaveletSelfAdded)
	myRobot.register_handler(events.FormButtonClicked, OnFormButtonClicked)
	myRobot.register_handler(events.WaveletBlipCreated, OnWaveletBlipCreated)
	appengine_robot_runner.run(myRobot)
