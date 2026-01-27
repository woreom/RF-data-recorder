from __future__ import division #To force the division to produce float result
import numpy as np
import pickle
import csv
from optparse import OptionParser
import matplotlib.pyplot as plt
from os import listdir
import os
import re

def plot_spectrum(fig,ax,Output_File_Name,debug,mode):
		if mode=='single':
			fig, ax = plt.subplots(2,2)
		with open(Output_File_Name, 'rb') as txt_file:
			array = pickle.load(txt_file,encoding="latin1")
			for row_index,row in enumerate(array):
				if row_index==0:
					freq_list=row
				else:
					if row_index==1:#Hold_Max==0 and Smooth==0:
						ax[0,0].plot(freq_list,row)
						ax[0,0].set_title('(a) Averaged FFTs without smoothing')
						ax[0,0].set(xlabel='Frequency in Hz',ylabel='Power in dB')
					elif row_index==2:#Hold_Max==0 and Smooth==1:
						ax[0,1].plot(freq_list,row)
						ax[0,1].set_title('(b) Averaged FFTs with smoothing')
						ax[0,1].set(xlabel='Frequency in Hz',ylabel='Power in dB')
					elif row_index==3:#Hold_Max==1 and Smooth==0:
						ax[1,0].plot(freq_list,row)
						ax[1,0].set_title('(c) Holding the max of FFTs without smoothing')
						ax[1,0].set(xlabel='Frequency in Hz',ylabel='Power in dB')
					elif row_index==4:#Hold_Max==1 and Smooth==1:
						ax[1,1].plot(freq_list,row)
						ax[1,1].set_title('(d) Holding the max of FFTs with smoothing')
						ax[1,1].set(xlabel='Frequency in Hz',ylabel='Power in dB')
			fig.suptitle(Output_File_Name.split('/')[-2]+'_spectrum',size=20)
			fig.set_size_inches(18.5, 10.5)
			if debug:
				plt.show()
			if mode=='single':
				fig.savefig(str(Output_File_Name.replace('.txt','.png')))

class find_files_in_repositories():
	def __init__(self,root_folder):
		self.root_list = []
		self.root_folder=root_folder

	# Function to recursively explore directories
	def explore_directory(self,folder):
		for root, dirs, files in os.walk(folder):
			print(root)
			self.root_list.append(root)
			plot_list=[]
			for file in files:
				if bool(re.match(r'^Spectrum_Heat_Map.*\.txt$', file)):
					plot_list.append(os.path.join(root, file))
			if len(plot_list)>0:
				fig, ax = plt.subplots(2,2)
				for item in plot_list:
					print('Files tagged with time: '+item)
					plot_spectrum(fig,ax,item,options.debug,options.mode)
				ax[0,0].grid()
				ax[0,1].grid()
				ax[1,0].grid()
				ax[1,1].grid()
				plt.legend()
				#plt.show()
				fig.savefig(str(root+'_spectrum.png'))

	def work(self):
		# Start exploring the root folder
		self.explore_directory(self.root_folder)

		# Continue exploring until no more directories are found
		while True:
			new_dirs_found = False
			for root, dirs, _ in os.walk(self.root_folder):
				for dir_name in dirs:
					dir_path = os.path.join(root, dir_name)
					if dir_path not in self.root_list:
						self.explore_directory(dir_path)
						new_dirs_found = True
			# If no new directories were found, break out of the loop
			if not new_dirs_found:
				break

if __name__ == '__main__':
	
	parser = OptionParser(usage="%prog: [options] coordiante")#------------------>for options
	parser.add_option("-f", "--output_file_folder_directory_and_name", type="string", default='',help="Output File Directory and name default=%default")
	parser.add_option("-a", "--all_files_folder_directory", type="string", default='',help="All Files Directory default=%default")
	parser.add_option("--debug", action="store_true", dest="debug", default=False,help="True if use kalman filter[default=%default]")
	parser.add_option("--mode", type="string", default="single",help="Select modes: single, compare[default=%default]")
	(options, args) = parser.parse_args()#------------------>for options

	if options.output_file_folder_directory_and_name=='' and options.all_files_folder_directory=='':
		print ("Insert file(s) directory and name (see options).")
		exit()
	elif options.output_file_folder_directory_and_name!='' and options.all_files_folder_directory!='':
		print ("You should choose either a specific file of all files directory (see options).")
		exit()
	elif options.output_file_folder_directory_and_name!='' and options.all_files_folder_directory=='':
		plot_spectrum(options.output_file_folder_directory_and_name,options.debug)

	elif  options.output_file_folder_directory_and_name=='' and options.all_files_folder_directory!='':
		if options.mode=='compare':
			find_files_in_repositories(options.all_files_folder_directory).work()
		else:
			Files_Names= [f for f in listdir(options.all_files_folder_directory) if 'Spectrum_Heat_Map' and '.txt' in f]
			for item in Files_Names:
				print('Files tagged with time: '+item)
				fig, ax = plt.subplots(2,2)
				plot_spectrum(fig,ax,options.all_files_folder_directory+'/'+item,options.debug,options.mode)

		
