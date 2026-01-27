from __future__ import division #To force the division to produce float result
import numpy as np
import scipy.fftpack
import math
import itertools
from scipy.signal import get_window
from scipy.signal import savgol_filter
import pickle
import time
import datetime
import csv
#import signal_recognition

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from optparse import OptionParser
import time


class Freaquency_Heat_Map(gr.top_block):

	def __init__(self,options):#------------------>for options
		gr.top_block.__init__(self, "Freaquency Heat Map")

		##################################################
		# Variables
		##################################################
		self.vlen = vlen = options.fft_size
		self.samp_rate = samp_rate = options.samp_rate
		self.gain = gain = options.gain #options.gain #------------------>for options
		self.freq = freq = options.freq_start*1e6 #------------------>for options

		##################################################
		# Blocks
		##################################################
		self.uhd_usrp_source_0_0 = uhd.usrp_source(
			",".join(("", "")),
			uhd.stream_args(
				cpu_format="fc32",
				channels=range(1),
			),
		)
		self.uhd_usrp_source_0_0.set_samp_rate(samp_rate)
		self.uhd_usrp_source_0_0.set_center_freq(freq, 0)
		self.uhd_usrp_source_0_0.set_gain(gain, 0)
		self.fft_vxx_0 = fft.fft_vcc(vlen, True, (window.rectangular(vlen)), True, 1)
		self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, vlen)
		self.blocks_probe_signal_vx_0 = blocks.probe_signal_vf(vlen)
		self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_gr_complex*vlen, 3)
		#################################################################
		self.blocks_nlog10_ff_0 = blocks.nlog10_ff(10, vlen, -20)# 10 represints the log() muliplier (i.e. 10*log). Needed to get correct dB power values.
		self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(vlen)
		##################################################
		# Connections
		##################################################
		self.connect((self.uhd_usrp_source_0_0, 0), (self.blocks_stream_to_vector_0, 0))
		self.connect((self.blocks_stream_to_vector_0, 0), (self.blocks_keep_one_in_n_0, 0))
		self.connect((self.blocks_keep_one_in_n_0, 0), (self.fft_vxx_0, 0))
		self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
		self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_nlog10_ff_0, 0))
		self.connect((self.blocks_nlog10_ff_0, 0), (self.blocks_probe_signal_vx_0, 0))	

	def get_vlen(self):
		return self.vlen

	def set_vlen(self, vlen):
		self.vlen = vlen

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.uhd_usrp_source_0_0.set_samp_rate(self.samp_rate)

	def get_gain(self):
		return self.gain

	def set_gain(self, gain):
		self.gain = gain
		self.uhd_usrp_source_0_0.set_gain(self.gain, 0)


	def get_freq(self):
		return self.freq

	def set_freq(self, freq):
		self.freq = freq
		self.uhd_usrp_source_0_0.set_center_freq(self.freq, 0)


def main(options):
	tb = Freaquency_Heat_Map(options)
	tb.start()
	
	samp_rate=options.samp_rate# Sample/sec
	if options.band_vhf:
		freq_list=1e6*np.array((range(150,194,20)))
		freq_start=min(freq_list)*1e-6
		freq_last=max(freq_list)*1e-6
		#freq_start=150*1e6
		#freq_last=174*1e6 
	elif options.band_uhf:
		freq_list=1e6*np.array((range(450,540,20)))
		freq_start=min(freq_list)*1e-6
		freq_last=max(freq_list)*1e-6
		#freq_start=450*1e6
		#freq_last=520*1e6 
	elif options.band_public_safty:
		freq_list=1e6*np.array((range(769,880,20)))
		freq_start=min(freq_list)*1e-6
		freq_last=max(freq_list)*1e-6
		#freq_start=769*1e6
		#freq_last=860*1e6
	elif options.band_gps:
		freq_list=1e6*np.array((range(4880,4940,20)))
		freq_start=min(freq_list)*1e-6
		freq_last=max(freq_list)*1e-6
		#freq_start=4880*1e6
		#freq_last=4920*1e6
	elif options.band_24:
		freq_list=1e6*np.array((range(2402,2522,20)))
		freq_start=min(freq_list)*1e-6
		freq_last=max(freq_list)*1e-6
	elif options.band_58:
		freq_list=1e6*np.array((range(5730,5900,20)))
		freq_start=min(freq_list)*1e-6
		freq_last=max(freq_list)*1e-6
	elif options.band_900:
		freq_list=1e6*np.array((range(850,950,20)))
		freq_start=min(freq_list)*1e-6
		freq_last=max(freq_list)*1e-6
	elif options.band_400:
		freq_list=1e6*np.array((range(434,454,20)))
		freq_start=min(freq_list)*1e-6
		freq_last=max(freq_list)*1e-6
	elif options.all_bands:
		#freq_list=1e6*np.array((range(150,194,20)+range(450,540,20)+range(769,880,20)+range(4880,4940,20)+range(2402,2522,20)+range(5730,5900,20)))
		freq_list=1e6*np.array((range(434,454,20)+range(850,950,20)+range(1100,1300,20)+range(2402,2522,20)+range(5730,5900,20)))
		freq_start=min(freq_list)*1e-6
		freq_last=max(freq_list)*1e-6
	else:
		freq_start=options.freq_start#2.412e9# Hz
		freq_last=options.freq_last#2.462e9#2.472e9#2.7e9# Hz
		freq_list=1e6*np.array(range(options.freq_start,options.freq_last+20,20))
	#freq_list_all=1e6*np.array(range(150,174,20))#+range(450,520,20)+range(769,860,20)+range(4880,4920,20)+range(2402,2502,20)+range(5730,5880,20))	
	wait_time=options.wait_time#1e-1#0.9e-1# Seconds
	FFT_Size=options.fft_size# Bins
	freq_step=20e6# Hz
	
	Output_File_Name=options.output_file_folder_directory+'/'+options.name+'_'+'Spectrum_Heat_Map_'+'Freq_'+str(freq_start)+'_to_Freq_'+str(freq_last)+'_gain_'+str(options.gain)+'_Time_'+str(datetime.datetime.now())+'.txt'
	
	print(Output_File_Name)
	for Hold_Max in [0,1]:
		for Smooth in [0,1]:
			last_time=time.time()
			
			tb.set_samp_rate(samp_rate)
			tb.set_vlen(FFT_Size)
			n=0
			freq=freq_list[n]#freq_start
			Nyquest_Freq=samp_rate/2.0# Hz
			Current_Frequency_Vector=np.linspace(freq-Nyquest_Freq, freq+Nyquest_Freq, FFT_Size)
			if Hold_Max==0:
				Heat_In_Current_Bandwidth=[]
			else:
				Heat_In_Current_Bandwidth=float('-inf')*np.array([np.ones(FFT_Size)]) #This is just an initialization in case of using the max
			if Hold_Max==0:
				FFT_Vec_Num=0
			Spectrum_Heat_Map=[]
			Spectrum_Frequency_Values=[]
			Spectrum_Frequency_Values=[]
			
			while True:
				time_now=time.time()
				if Hold_Max==0:
					FFT_Vec_Num+=1
				#----read from msg----
				m=list(tb.blocks_probe_signal_vx_0.level())
				In=m[0:FFT_Size]
				In=20*np.log10(2.0/FFT_Size)+np.array(In)
				No_DC=(In[int(FFT_Size/2)+2]+In[int(FFT_Size/2)-2])/2
				In[int(FFT_Size/2)-1]=No_DC
				In[int(FFT_Size/2)]=No_DC
				In[int(FFT_Size/2)+1]=No_DC
				if Smooth:
					In=savgol_filter(In, 151, 2)
				if Hold_Max==0:
					if FFT_Vec_Num==1:
						Heat_In_Current_Bandwidth=In
					else:
						Heat_In_Current_Bandwidth=(Heat_In_Current_Bandwidth*(FFT_Vec_Num-1)+In)/FFT_Vec_Num#Take the average
				else:
					Heat_In_Current_Bandwidth=np.maximum(Heat_In_Current_Bandwidth,In)
				if time_now-last_time>wait_time:
					tb.stop()
					tb.wait()
					
					Current_Frequency_Vector=np.linspace(freq-Nyquest_Freq, freq+Nyquest_Freq, FFT_Size)
					Spectrum_Frequency_Values=np.append(Spectrum_Frequency_Values,Current_Frequency_Vector)
					Spectrum_Heat_Map=np.append(Spectrum_Heat_Map,Heat_In_Current_Bandwidth)
					print(freq)
					
					if Hold_Max==0:
						Heat_In_Current_Bandwidth=[]
					else:
						Heat_In_Current_Bandwidth=float('-inf')*np.array([np.ones(FFT_Size)]) #This is just an initialization in case of using the max
					if Hold_Max==0:
						FFT_Vec_Num=0
					last_time=time_now
					n+=1
					if n<len(freq_list):
						freq=freq_list[n]#freq+freq_step
						tb.set_freq(freq)
						tb.start()
					else:
						tb.start()
						break
				#if freq>=freq_last:
						#break
			print("Finish >>>>>>>>>>>>>>>>>>>>>>>>>>>")
			if Hold_Max==0 and Smooth==0:
				file_data=np.array([np.zeros(len(Spectrum_Frequency_Values))]) #This is just an initialization #--------------------->
				file_data=np.vstack((file_data,np.array([Spectrum_Frequency_Values])))
				file_data=np.vstack((file_data,np.array([Spectrum_Heat_Map])))
			else:
				file_data=np.vstack((file_data,np.array([Spectrum_Heat_Map])))
	file_data=file_data[1:]
	with open(Output_File_Name, 'wb') as txt_file:
		pickle.dump(file_data,txt_file)

	tb.stop()
	tb.wait()
		

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options] coordiante")#------------------>for options
	parser.add_option("-r", "--samp_rate", type="int", default=20e6,help="USRP sampling rate default=%default")#------------------>for options
	parser.add_option("-s", "--freq_start", type="int", default=2312,help="First center frequncy in the band default=%default")#------------------>for options
	parser.add_option("-l", "--freq_last", type="int", default=2562,help="Last center frequncy in the band default=%default")#------------------>for options
	parser.add_option("-w", "--wait_time", type="int", default=0.5,help="Wait time in each channel in seconds default=%default")#------------------>for options
	parser.add_option("-x", "--gain", type="int", default=76,help="USRP Gain in dB default=%default")#------------------>for options
	parser.add_option("-f", "--fft_size", type="int", default=1024,help="FFT vector size default=%default")#------------------>for options
	parser.add_option("-d", "--output_file_folder_directory", type="string", default='~/Desktop',help="Output_File_Directory default=%default")#------------------>for options
	parser.add_option("-v", "--band_vhf", type="int", default=0,help="Insert 1 to scan VHF band default=%default")#------------------>for options
	parser.add_option("-u", "--band_uhf", type="int", default=0,help="Insert 1 to scan UHF band default=%default")#------------------>for options
	parser.add_option("-p", "--band_public_safty", type="int", default=0,help="Insert 1 to scan Public Ssafty band default=%default")#------------------>for options
	parser.add_option("-g", "--band_gps", type="int", default=0,help="Insert 1 to scan GPS band default=%default")#------------------>for options
	parser.add_option("-t", "--band_24", type="int", default=0,help="Insert 1 to scan WiFi 2.4GHz band default=%default")#------------------>for options
	parser.add_option("-e", "--band_58", type="int", default=0,help="Insert 1 to scan WiFi 5.8GHz band default=%default")#------------------>for options
	parser.add_option("-z", "--band_900", type="int", default=0,help="Insert 1 to scan WiFi 900Mhz band default=%default")#------------------>for options
	parser.add_option("-k", "--band_400", type="int", default=0,help="Insert 1 to scan WiFi 400Mhz band default=%default")#------------------>for options
	parser.add_option("-a", "--all_bands", type="int", default=0,help="Insert 1 to scan all bands default=%default")#------------------>for options
	parser.add_option("-n", "--name", type="string", default='DEFAULT',help="write to name default=%default")#------------------>for options

	(options, args) = parser.parse_args()#------------------>for options
	main(options=options)#------------------>for options
	#main()
	#############################################
