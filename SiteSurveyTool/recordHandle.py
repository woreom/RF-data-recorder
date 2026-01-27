from subprocess import Popen, PIPE
import time, datetime
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import os
from pathlib import Path
import sys
import numpy as np

import matplotlib.pyplot as plt
import scipy.fftpack
import math
import itertools
from scipy.signal import get_window
from scipy.signal import savgol_filter
import pickle
import glob

import csv

RECORD_FILE_PATH=''
	
def crop(path_of_file,correlation_length):
    with open(path_of_file) as data_file:
        croped_data_file=np.fromfile(data_file,dtype=np.complex64)
    number_of_vectors=int(croped_data_file.size/correlation_length)
    croped_data_file=croped_data_file[0:number_of_vectors*correlation_length]
    return number_of_vectors, croped_data_file	

def selectChannels2(center_freq, bw, sampling_rate):
    bw_val = int(bw)
    center_freq_val = float(center_freq)
    sampling_rate_val = int(sampling_rate)
    scan_range = sampling_rate_val/2 + bw_val/2 - 0.1*bw_val
    if bw_val <= 20:
        channels = initiateVideoChannels(center_freq_val-scan_range, center_freq_val+scan_range, 2)
    elif bw_val == 5:
        channels = initiateVideoChannels(center_freq_val-scan_range, center_freq_val+scan_range, 1)
    elif bw_val > 20:
        channels = initiateVideoChannels(center_freq_val-scan_range, center_freq_val+scan_range, 4)
    print(channels)
    return channels


def initiateVideoChannels(start,stop,interval):
	channels = []
	step = int(abs(stop-start)/interval+1)
	for i in range(step):
		channels.append((start+interval*i))
	return channels
	
def switchFreq2(options):
    channels = selectChannels2(options['center_freq'], options['bw'], options['sampling_rate'])
    print('-----scanning channels: ', channels)
    for freq in channels:
        record = Popen(['python3', GLOBAL_FILE_PATH+'/auto_record.py','-i {0}'.format(options['record_dir']), '-n {0}'.format(options['device']), '-q {0}'.format(options['drone_c_freq']), '-t {0}'.format(options['status']), '-v {0}'.format(options['env']), '-g {0}'.format(options['sdr_gain']),'-p {0}'.format(options['splitter']),'-x {0}'.format(options['duration_recording']),'-d {0}'.format(options['distance']),'-a {0}'.format(options['altitude']),'-c {0}'.format(freq),'-b {0}'.format(options['bw']),'-r {0}'.format(options['snr']), '-s {0}'.format(options['sampling_rate'])])
        
        time.sleep(int(options['duration_recording'])+5)
        process = record.poll()
        while process==None:
            print("process haven't stop yet")
            record.kill()
            record.wait()
            time.sleep(1)
            process = record.poll()
        print('switch freq')
    print('FINISHED!')	
	

if __name__ == '__main__':

	print("Please input the directory of your recordHandle.py file: ")
	GLOBAL_FILE_PATH = input()
	
	print("Start to gather recording related parameters, input info separated by - if needed:")
	
	while True:
		filename = ""
		options = {}
		
		print("Please input the drone model and make or device name, separated by -, e.g., DJI-Mini4: ")
		device = input()
		options['device'] = device
		
		print("Please input the drone status when recording, e.g., hovering, on the ground, or flying: ")
		status = input()
		options['status'] = status
		
		print("Please describe the recording environment, e.g., cage or office: ")
		env = input()
		options['env'] = env
		
		print("Please input the SDR gain in dB:")
		sdr_gain = input()
		options['sdr_gain'] = sdr_gain
		
		print("Please input if a splitter is used or not, Y for yes, N for no: ")
		splitter = input()
		options['splitter'] = splitter
		
		print("Please input the time duration for each recording in seconds: ")
		duration_recording = input()
		options['duration_recording'] = duration_recording
		
		print("Please input the distance to the drone in meters: ")
		distance = input()
		options['distance'] = distance
		
		print("Please input the altitude of the drone in meters: ")
		altitude = input()
		options['altitude'] = altitude
		
		print("Please input the center frequency of the drone signal in MHz: ")
		center_freq = input()
		options['center_freq'] = center_freq
		options['drone_c_freq'] = center_freq
		
		print("Please input the bandwidth of the drone signal in MHz: ")
		bw = input()
		options['bw'] = bw
		
		print("Please input a rough estimate of SNR in the channel in dB: ")
		snr = input()
		options['snr'] = snr
		
		print("Please input the sampling rate of the SDR card in MHz: ")
		sr = input()
		options['sampling_rate'] = int(sr)
		
		print("Please input the directory to save the recording: ")
		dir_name = input()
		ct = datetime.datetime.now()
		ct = str(ct).split(' ')
		ymd = ct[0]
		timestamp = ct[1]
		print('Current time is: ', ymd, timestamp)
		
		sub_dir = options['env'] + '_' + str(options['sdr_gain']) + '_' + str(options['sampling_rate']) + '_' + options['duration_recording'] + '_' + options['splitter'] + '_' + timestamp
		whole_dir = RECORD_FILE_PATH + dir_name + '/' + ymd + '/' + sub_dir + '/'
		print("This patch of recording will be saved in: ", whole_dir)
		options['record_dir'] = whole_dir
		nested_path = Path(whole_dir)
		nested_path.mkdir(parents=True, exist_ok=True)
		
		print("Please input a detailed description of the recording environment: ")
		des = input()
		des_f = whole_dir + "readme.txt"
		with open(des_f, 'w') as file:
			file.write(des)
			file.write('\n')
		print(f"Environment info saved to {des_f}")
		
		csv_f = whole_dir + "parameter_summary.csv"
		with open(csv_f, 'w', newline='') as c_f:
			fieldnames = options.keys()
			writer = csv.DictWriter(c_f, fieldnames=fieldnames)
			writer.writeheader()
			writer.writerows([options])
			
		print("A parameter summary file is saved into: ", csv_f)
	
		filename = filename + device + '_' + center_freq + '_' + bw + '_' + center_freq + '_' + altitude + '_' + distance + '_' + status + '_' + snr + '.dat'
		print("Recording will be saved as: ", filename, "Press ENTER to confirm, else input N to re-enter: ")
		ans = input()
		if ans == "":
			break
	    
	print("Recording parameters confirmed. Recording initiated.")
	switchFreq2(options)
	
	flag_plot = input("Please input Y for ploting the spectrograms for review, else press enter to finish: ")
	if flag_plot == 'Y':

		data_dir = whole_dir
		file_names = os.listdir(data_dir)
		img_dir_head = input("Please input the directory where you want to save the spectrogram files: ")
		img_dir_temp = data_dir.split('/')
		img_dir = img_dir_head + '/spectrogram/' + '/'.join(img_dir_temp[-3:])
		print("The spectrogram will be saved into: ", img_dir)
		img_path = Path(img_dir)
		img_path.mkdir(parents=True, exist_ok=True)

		for f in file_names:
			if f.endswith(".dat"):
				print(f)
				FFT_Size=1024
				Sampling_Rate=options['sampling_rate']*1e6
				fn = f.split('_')
				Center_Freq = float(fn[3])*1e6
				print('Plotting at center frequency: ', Center_Freq)
				Total_Number_Of_FFT_Vectors_In_Spectrogram_Image=1000

				File = data_dir + f
				Spectrogram_Output_Image_Name= img_dir + f[:-4] + '.jpg'

				number_of_Data_vectors,Recorded_Signal_In_Time_Domain=crop(File,FFT_Size)
				Recorded_Signal_In_Time_Domain=Recorded_Signal_In_Time_Domain[0:Total_Number_Of_FFT_Vectors_In_Spectrogram_Image*FFT_Size]

				img,ax = plt.subplots(1)
				ax.specgram(x=Recorded_Signal_In_Time_Domain, Fs=Sampling_Rate, NFFT=FFT_Size, Fc=Center_Freq)
				img.savefig(Spectrogram_Output_Image_Name)
				plt.close()
	
	
	
	
