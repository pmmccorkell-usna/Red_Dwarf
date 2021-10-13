import mbed
from time import sleep
from json import dumps,loads
# from multiprocessing import Process, Pipe


class BNO:
	def __init__(self,communicator):
		self.comms=communicator
		self.run=1
	
	def stream(self):
		while(self.run):
			self.data=mbed.get_angles()
			# print('mbed.py: '+dumps(self.data))
			self.comms.send(self.data)
			sleep(0.01)

	def close(self):
		self.run = 0

if __name__ == "__main__":
	print("running as main")
	from multiprocessing import Process, Pipe
	daemon_mode = True

	mbed_pipe_in,mbed_pipe_out = Pipe()
	imu = mbed_wrapper.BNO(mbed_pipe_in)
	mbed_process = Process(target=imu.stream,daemon=daemon_mode)
	mbed_process.start()
	
	bno = {
		'heading':999,
		'roll':999,
		'pitch':999,
		'calibration':999,
		'status':999
	}

	buffer={}
	while (mbed_pipe_out.recv()):
		buffer = mbed_pipe_out.recv()
	if buffer:
		bno = buffer
		buffer = {}
