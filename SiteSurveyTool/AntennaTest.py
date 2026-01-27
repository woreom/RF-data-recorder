from subprocess import Popen, PIPE
import time, datetime
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import numpy as np

GLOBAL_FILE_PATH='/home/DGH_v0-03/'

def evaluate():
	results = {}
	with open('/home/RecordTest/antenna.txt','r') as f:
		for line in f:
			data = line.split('|')
			antenna = data[0].split('_')
			print data

def record(options):
	ACF_detector = Popen(['python', GLOBAL_FILE_PATH+'ACF_detector.py','-G {0}'.format(options.gain),'-g {0}'.format(options.channel_24),'-i {0}'.format(options.channel_24),'-j {0}'.format(options.channel_58),'-k {0}'.format(options.channel_58),'-l {0}'.format(options.channel_900),'-m {0}'.format(options.channel_900)])
	time.sleep(5+options.wait_time)
	process = ACF_detector.poll()
	if process==None:
		print "process haven't stop yet"
		ACF_detector.kill()
		ACF_detector.wait()
		time.sleep(1)
	readings = checkReading()
	print options.name, readings
	with open('/home/RecordTest/antenna.txt','a') as f:
		write_in = options.name+'|'
		for item in readings:
			write_in = write_in + item+'|'+str(readings[item])+'|'
		f.write(write_in+'\n')

def checkReading():
	readings = {}
	with open (GLOBAL_FILE_PATH+'Logs/widebandReports.txt','r') as f:
		for line in f:
			data = line.split('|')
			print data
			try:
				readings[data[0]].append(float(data[1]))
			except:
				readings[data[0]] = []
	with open (GLOBAL_FILE_PATH+'Logs/widebandReports.txt','w') as ff:
		pass
	for item in readings:
		readings[item] = np.mean(readings[item])
	return readings

if __name__ == '__main__':
	usage="usage: %prog: [options]"
	parser = OptionParser(option_class=eng_option, usage=usage)
	parser.add_option("-N", "--name", type="string", default='antenna',
						help="antenna name [default=%default]")
	parser.add_option("-G", "--gain", type="eng_float", default=76,
						help="Set gain [default=%default]")
	parser.add_option("-a", "--channel-24", type="eng_float", default=2407,
						help="Set channel 2400 [default=%default]")
	parser.add_option("-b", "--channel-58", type="eng_float", default=5730,
						help="Set channel 5800 [default=%default]")
	parser.add_option("-c", "--channel-900", type="eng_float", default=918,
						help="Set channel 900 [default=%default]")
	parser.add_option("-T", "--wait-time", type="eng_float", default=30,
						help="Set wait time [default=%default]")
	parser.add_option("-M", "--mode", type="int", default=0,
						help="Set mode [default=%default]")
	(options, args) = parser.parse_args()
	if options.mode == 0:
		record(options)
	else:
		evaluate()
