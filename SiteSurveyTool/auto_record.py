import numpy as np
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import time, datetime
import threading
import struct
import timeit
from optparse import OptionParser
#from DGH_Logging import *
import sys


class top_block(gr.top_block):

	def __init__(self,options,args):
		gr.top_block.__init__(self, "Top Block")

		self.name = options.device
		self.samp_rate = samp_rate = int(options.sampling_rate)*1e6
		self.gain = gain = options.sdr_gain
		print('-----set up gain:', gain)
		self.freq = freq = options.center_freq*1e6
		print('-----set up freq:', freq)
		
		self.file_name = file_name = options.record_dir.strip() + options.device.strip() + '_' + str(options.drone_c_freq) + '_' + str(int(options.bw)) + '_' + str(options.center_freq) + '_' + options.altitude.strip() + '_' + options.distance.strip() + '_' + options.status.strip() + '_' + str(options.snr) + '.dat'
		
		print('-----write to file:', file_name)
		self.usrp_source = uhd.usrp_source(",".join(("", "")),uhd.stream_args(cpu_format="fc32",channels=range(1),),)
		self.usrp_source.set_samp_rate(samp_rate)
		self.usrp_source.set_center_freq(freq)
		self.usrp_source.set_gain(gain)
		self.file_sink = blocks.file_sink(gr.sizeof_gr_complex*1, file_name, True)
		self.file_sink.set_unbuffered(False)

		self.connect((self.usrp_source, 0), (self.file_sink, 0))

def main(top_block, options, args):
	count_time=options.duration_recording
	tb = top_block(options,args)
	tb.start()
	count = 0
	time1 = time.time()
	while count < count_time:
		print('-----',count)
		count = count + 1
		time.sleep(1)
	time2 = time.time()
	print(time2-time1)
	tb.stop()
	tb.wait()

if __name__ == '__main__':
	usage="usage: %prog: [options]"
	parser = OptionParser(option_class=eng_option, usage=usage)
	parser.add_option("-i", "--record_dir", type="string", default="/home/hongtao/Desktop/sitesurveyrecording/", help="Set directory for saving the recordings [default=%default]")
	parser.add_option("-n", "--device", type="string", default='DEFAULT', help="Set drone or signal name [default=%default]")
	parser.add_option("-t", "--status", type="string", default='DEFAULT', help="Set up drone status, e.g., flying, armed, hovering, on the ground [default=%default]")
	parser.add_option("-q", "--drone_c_freq", type="eng_float", default=2442, help="Set center frequency of drone or other signal [default=%default]")
	parser.add_option("-v", "--env", type="string", default='DEFAULT', help="Set recording environment description [default=%default]")
	parser.add_option("-g", "--sdr_gain", type="eng_float", default=50, help="Set SDR gain in dB [default=%default], max=76")
	parser.add_option("-p", "--splitter", type="string", default="Y", help="Set using splitter or not")
	parser.add_option("-x", "--duration_recording", type="eng_float", default=5, help="Set duration of recording [default=%default]")
	parser.add_option("-d", "--distance", type="string", default=0, help="Setup distance to the signal source [default=%default]")
	parser.add_option("-a", "--altitude", type="string", default=0, help="Setup altitude of the signal source [default=%default]")
	parser.add_option("-c", "--center_freq", type="eng_float", default=2412, help="Set center freqency of scanning [default=%default]")
	parser.add_option("-b", "--bw", type="string", default='20', help="Setup bandwidth [default=%default]")
	parser.add_option("-r", "--snr", type="eng_float", default=15, help="Setup estimated SNR [default=%default]")
	parser.add_option("-s", "--sampling_rate", type="eng_float", default=20e6, help="Set sampling rate [default=%default]")
	
	(options, args) = parser.parse_args()
	main(top_block,options,args)
