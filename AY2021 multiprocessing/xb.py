# Patrick McCorkell
# April 2021
# US Naval Academy
# Robotics and Control TSD
#
#
#
# Install xbox drivers:
# sudo apt-get install xboxdrv
#
# run with sudo privileges
# add user to the root group:
#	sudo usermod -a -G root pi
#
# create permissions file using nano
#	sudo nano /etc/udev/rules.d/55-permissions-uinput.rules
#	enter rules:
#

from xbox import Joystick
from math import sqrt, pi, atan
from math import tau as twopi
from time import sleep, monotonic
from json import dumps
# from surface import *
# import atexit

class XBoxController:
	def __init__(self,communicator):
		self.DEBUG = 0
		self.joystick = Joystick()
		self.comms = communicator
		self.max_speed = 500
		self.debounce = 0.2

		self.values = {
			'scalar1':0,
			'vector1':0,
			'scalar2':0,
			'vector2':0,
			'vector2_x2':0,
			'graph' : 0,
			'maintain' : 1,
			'mode' : 1,
			'quit' : 0
		}

	def scalar(self,a,b):
		# rescale_factor = 1.414213562373095
		returnval = sqrt(a**2+b**2)
		return returnval

	def angle(self,a,b):
		degree_conversion = 360 / twopi
		if (a==0):
			a=0.000001
		returnval = atan(b/a)
		if (a < 0):
			returnval += pi
		elif (b < 0):
			returnval += twopi
		return returnval * degree_conversion

	def relative(self,x):
		returnval = (round(x*3))+834
		return returnval

	def check_quit(self):
		return (self.joystick.leftBumper() and self.joystick.rightBumper())

	def sample(self):
		# self.values
		#tuple scaled and normalized [-1.0,1.0]
		(x1,y1) = self.joystick.leftStick()
		#print(x1,y1)
		(x2,y2) = self.joystick.rightStick()

		new_values = {
			'scalar1':self.scalar(x1,y1),
			'vector1':self.angle(y1,x1),
			'scalar2':self.scalar(x2,y2),
			'vector2':self.angle(y2,x2),
			'vector2_x2':self.relative(x2),
			'graph' : int(self.joystick.leftTrigger()),
			'maintain' : self.joystick.rightBumper(),
			'mode' : self.joystick.leftBumper(),
			'quit' : self.check_quit()
		}
		self.values = new_values
		# if (self.DEBUG):
		# 	print(self.values)
		return new_values

	def process(self):
		samples = self.sample()

		self.return_dict = {
			'facing' : round(samples['vector2_x2']),
			'offset' : round(samples['vector1']),
			'speed' : round(self.max_speed*samples['scalar1']),		# if speed is < 10, set to 0
			'graph' : samples['graph'],
			'maintain' : samples['maintain'],
			'mode' : samples['mode'],
			'quit' : samples['quit']
		}
		if (self.DEBUG):
			print()
			# for k,v in self.return_dict:
			# 	print(str(k)+": "+str(v))
			print('xb.py : '+dumps(self.return_dict))
			print()
		self.comms.send(self.return_dict)
		# return return_dict

	def stream(self):
		while(1):
			self.process()
			sleep(0.005)

	def close(self):
		sleep(0.1)
		# print("Turning off xbox controller.")
		self.joystick.close()



###############################################################
###################### Debugging Section ######################
###############################################################
###############################################################

def xbox_debounce(val1,val2):
	global debounce_timer, debounce_time_check
	current = monotonic()

	# if (bool_val):
	# 	returnval = val1 ^ val2
		# if returnval != val1:
			# debounce_timer = monotonic()
	# else:
	# 	returnval = val1
	bool_val = bool(max(current-debounce_timer-debounce_time_check,0))
	returnval = (bool_val * (val1 ^ val2)) + ((not bool_val) * val1)
	not_timer_bool = (returnval ^ val1)
	debounce_timer = (monotonic() * (not_timer_bool)) + (debounce_timer * (not not_timer_bool))
	return returnval

def vessel_thread():
	global vessel
	while(1):
		vessel.azThrusterLogic()
		sleep(0.02)

if __name__ == '__main__':
	print("running as main")
	print("Importing libraries for independent mode.")
	from multiprocessing import Pipe
	from threading import Thread
	import surface

	print("Initiating surface vessel class.")
	global vessel
	vessel = surface.Controller()
	vessel.stopAll()
	vessel.thrusters.servoboard.set_max(500/1.2)
	vessel_thread_object = Thread(target=vessel_thread)
	vessel_thread_object.start()


	print("Initiating xbox controller class.")
	global debounce_timer, debounce_time_check
	debounce_timer = monotonic()
	debounce_time_check = 1.0

	xb_pipe_in, xb_pipe_out = Pipe()
	try:
		xbox_controller = XBoxController(xb_pipe_in)
	except IOError as e:
		# print("xbox controller failed.")
		print(e)
		quit()
	poll_xbox = Thread(target=xbox_controller.stream)
	sleep(0.1)
	poll_xbox.start()


	print("Starting loop.")
	xbox = {
		'facing':999,
		'offset':999,
		'speed':999,
		'graph':0,		# graph 1 starts graphing functionality
		'maintain':1,
		'mode':1,		# mode 1 qtm, mode 0 bno
		'quit':0
	}
	while(1):
		buffer = {}
		while (xb_pipe_out.poll()):
			buffer = xb_pipe_out.recv()
		if buffer:
			vessel.persistent_offset = buffer['offset']
			vessel.persistent_speed = bool(max(buffer['speed']-10,0)) * buffer['speed']

			buffer['maintain'] = xbox_debounce(xbox['maintain'],buffer['maintain'])
			buffer['mode'] = xbox_debounce(xbox['mode'],buffer['mode'])

			xbox = buffer
			vessel.commands['hea'](bool(buffer['maintain']) and buffer['facing'])
		print(xbox)
		sleep(0.02)
