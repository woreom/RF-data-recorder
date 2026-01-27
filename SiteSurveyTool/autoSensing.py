#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Autosensing
# Generated: Wed Mar  6 11:22:43 2019
##################################################
import time, threading, struct, os
from dotenv import load_dotenv
load_dotenv('/home/aerodefense/prefix/setup_env.sh',verbose=True,override=True)
_environ = dict(os.environ)
os.environ.clear()
os.environ.update(_environ)

from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.fft import logpwrfft
from gnuradio.fft import window
from gnuradio.filter import firdes
from optparse import OptionParser
import numpy as np


class ThreadClass(threading.Thread):
	def run(self):
		return

class parse_msg(object):
	def __init__(self, msg):

		self.l = msg.length()
		t = msg.to_string()
		self.raw_data = t
		self.data = struct.unpack('%df' % (self.l/4,), t)

class autoSensing(gr.top_block):

	def __init__(self,freq):
		gr.top_block.__init__(self, "Autosensing")

		##################################################
		# Variables
		##################################################
		self.freq = freq 
		self.gain = gain = 50
		self.samp_rate = samp_rate = 20e6
		self.fft_size_1 = fft_size_1 = 2048
		self.fft_size = fft_size = 4
		self.ave = ave = 20000
		self.record = False
		##################################################
		# Blocks
		##################################################
		self.uhd_usrp_source_0 = uhd.usrp_source(
			",".join(("", "")),
			uhd.stream_args(
				cpu_format="fc32",
				channels=range(1),
			),
		)
		self.uhd_usrp_source_0.set_samp_rate(samp_rate)
		self.uhd_usrp_source_0.set_center_freq(freq, 0)
		self.uhd_usrp_source_0.set_gain(gain, 0)
		self.logpwrfft_x_0 = logpwrfft.logpwrfft_f(
			sample_rate=samp_rate,
			fft_size=fft_size_1,
			ref_scale=2,
			frame_rate=int(samp_rate/fft_size_1),
			avg_alpha=0.5,
			average=False,
		)
		self.fft_vxx_0 = fft.fft_vfc(fft_size, True, (window.rectangular(fft_size)), 1)
		self.blocks_vector_to_streams_0 = blocks.vector_to_streams(gr.sizeof_gr_complex*1, 4)
		self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_float*1, fft_size_1)
		self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_float*1, fft_size)
		self.blocks_peak_detector_xb_0 = blocks.peak_detector_fb(0.4, 0.4, 30, 0.001)
		self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_float*1)
		self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((500, ))
		self.blocks_moving_average_xx_0 = blocks.moving_average_ff(ave, 1, 4000)
		self.blocks_file_sink_1 = blocks.file_sink(gr.sizeof_gr_complex*1, 'test.dat', True)
		self.blocks_file_sink_1.set_unbuffered(False)
		self.blocks_divide_xx_0 = blocks.divide_ff(1)
		self.blocks_complex_to_mag_squared_0_2 = blocks.complex_to_mag_squared(1)
		self.blocks_complex_to_mag_squared_0_1 = blocks.complex_to_mag_squared(1)
		self.blocks_complex_to_mag_squared_0_0 = blocks.complex_to_mag_squared(1)
		self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)
		self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
		self.blocks_char_to_float_0 = blocks.char_to_float(1, 1)
		self.blocks_add_xx_0 = blocks.add_vff(1)
		self.analog_const_source_x_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 4000)
		self.msgq = message_sink_msgq_out = gr.msg_queue(1)
		self.message_sink = blocks.message_sink(gr.sizeof_float*1, message_sink_msgq_out, False)
		##################################################
		# Connections
		##################################################
		self.connect((self.analog_const_source_x_0, 0), (self.blocks_divide_xx_0, 1))
		self.connect((self.blocks_add_xx_0, 0), (self.blocks_divide_xx_0, 0))
		self.connect((self.blocks_char_to_float_0, 0), (self.blocks_moving_average_xx_0, 0))
		self.connect((self.blocks_complex_to_mag_0, 0), (self.blocks_stream_to_vector_0, 0))
		self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_add_xx_0, 0))
		self.connect((self.blocks_complex_to_mag_squared_0_0, 0), (self.blocks_add_xx_0, 3))
		self.connect((self.blocks_complex_to_mag_squared_0_1, 0), (self.blocks_add_xx_0, 2))
		self.connect((self.blocks_complex_to_mag_squared_0_2, 0), (self.blocks_add_xx_0, 1))
		self.connect((self.blocks_divide_xx_0, 0), (self.logpwrfft_x_0, 0))
		self.connect((self.blocks_moving_average_xx_0, 0), (self.message_sink, 0))
		self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_complex_to_mag_0, 0))
		self.connect((self.blocks_peak_detector_xb_0, 0), (self.blocks_char_to_float_0, 0))
		self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
		self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_peak_detector_xb_0, 0))
		self.connect((self.blocks_vector_to_streams_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
		self.connect((self.blocks_vector_to_streams_0, 3), (self.blocks_complex_to_mag_squared_0_0, 0))
		self.connect((self.blocks_vector_to_streams_0, 2), (self.blocks_complex_to_mag_squared_0_1, 0))
		self.connect((self.blocks_vector_to_streams_0, 1), (self.blocks_complex_to_mag_squared_0_2, 0))
		self.connect((self.fft_vxx_0, 0), (self.blocks_vector_to_streams_0, 0))
		self.connect((self.logpwrfft_x_0, 0), (self.blocks_vector_to_stream_0, 0))		
		self.connect((self.uhd_usrp_source_0, 0), (self.blocks_multiply_const_vxx_0, 0))

			

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
		self.logpwrfft_x_0.set_sample_rate(self.samp_rate)

	def get_fft_size_1(self):
		return self.fft_size_1

	def set_fft_size_1(self, fft_size_1):
		self.fft_size_1 = fft_size_1

	def get_fft_size(self):
		return self.fft_size

	def set_fft_size(self, fft_size):
		self.fft_size = fft_size

	def set_freq(self, freq):
		self.freq = freq
		self.uhd_usrp_source_0.set_center_freq(uhd.tune_request(freq, rf_freq=(freq),rf_freq_policy=uhd.tune_request.POLICY_MANUAL))
		

class Recorder():
	def __init__(self,SWEEP_FREQ_list):
		self.SWEEP_FREQ_list = np.array(SWEEP_FREQ_list)
		self.sweep_time = 5
		self.current_freq = self.SWEEP_FREQ_list[0]
		self.max_iteration = 1
		self.current_iteration = 0

	def tune_freq(self,fg):
			time_now = time.time()
			if time_now-self.LAST_TUNE_TIME>self.sweep_time:
				location = np.where(self.SWEEP_FREQ_list==self.current_freq)[0][0]
				if location<len(SWEEP_FREQ_list)-1: 
					target_freq = SWEEP_FREQ_list[int(location+1)]					
				else:
					target_freq = SWEEP_FREQ_list[0]
					self.current_iteration = self.current_iteration + 1
					if self.current_iteration > self.max_iteration -1:
						print '-----Sweeping Finished-----'                                                                                 
						return True
					else:
						print 'Scanning cycle ',self.current_iteration
						print '-----Sweeping start at ', target_freq,'-----'
				fg.stop()
				fg.wait()
				if fg.record:
					fg.record = False
					print 'stop recording'
					fg.disconnect((fg.uhd_usrp_source_0, 0), (fg.blocks_file_sink_1, 0))
				print 'Switch freq to ', target_freq
				fg.set_freq(target_freq*1e6)								
				self.current_freq = target_freq			
				fg.start()
				self.LAST_TUNE_TIME = time.time()


	def main(self):
		fg = autoSensing(self.current_freq*1e6)
		print '-----Sweeping start at ',self.current_freq,'-----'
		fg.start()
		self.LAST_TUNE_TIME=time.time()
		while True:
			m=parse_msg(fg.msgq.delete_head())
			if fg.record ==False and m.data[0]>0:				
				print 'Activity detected, start recordng'
				fg.record =True
				fg.stop()
				fg.wait()
				fg.blocks_file_sink_1 = blocks.file_sink(gr.sizeof_gr_complex*1, 'test_'+str(self.current_freq)+'.dat', True)
				fg.connect((fg.uhd_usrp_source_0, 0), (fg.blocks_file_sink_1, 0))
				fg.start()

			if self.tune_freq(fg):
				break
		fg.stop()
		fg.wait()

if __name__ == '__main__':
	
	SWEEP_FREQ_list = [434,905,915,2382,2392,2412,2422,2432,2442,2452,2462,2472,2482,2492,5730,5740,5750,5760,5770,5780,5790,5800,5810,5820,5830,5840,5850,5860,5870,5880]
	tb = Recorder(SWEEP_FREQ_list)
	tb.main()
	if os.path.isfile('test.dat'):
		os.remove('test.dat')
	print 'Survey Ended'
	
