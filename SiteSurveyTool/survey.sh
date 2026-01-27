#!/bin/sh
#x-terminal-emulator
while true; do
	echo 'Please enter the name of the site: \n'
	read sitename
	if [ -z "$sitename" ]
	then
		echo 'Please enter a valid name!\n'
	else
		if [ -d ~/Desktop/$sitename ]
		then
			echo 'file path already exist, please pick another name'
		else
			if [ -f ~/Desktop/$sitename.zip ]
			then
							echo 'file already exist, please pick another name'
			else
				break
			fi
		fi
	fi
done

while true; do
	checkSDR=$(sudo uhd_find_devices | grep serial | tr -d :)
	if [ -z "$checkSDR" ]
	then
		echo 'Missing SDR card, please check!\n'
	else
		break
	fi
	echo 'Press Enter to continue...\n'
	read key
done
mkdir ~/Desktop/$sitename
sudo python3 /home/Peripherals/SiteSurveyTool/Frequency_Heat_Map_Generator.py -t 1 -w 3 -n $sitename -d ~/Desktop/$sitename/
sleep 3
sudo python3 /home/Peripherals/SiteSurveyTool/Frequency_Heat_Map_Generator.py -e 1 -w 3 -n $sitename -d ~/Desktop/$sitename/
sleep 3
sudo python3 /home/Peripherals/SiteSurveyTool/Frequency_Heat_Map_Generator.py -z 1 -w 3 -n $sitename -d ~/Desktop/$sitename/
sleep 3
sudo python3 /home/Peripherals/SiteSurveyTool/Frequency_Heat_Map_Generator.py -k 1 -w 3 -n $sitename -d ~/Desktop/$sitename/
sleep 3
echo '\n'
echo 'Survey Finished, scanned channels: 400Mhz, 900Mhz, 2.4Ghz, 5.8Ghz\n'
#echo 'Press Enter to continue...\n'
#read key
echo 'plotting...\n'
sudo python3 /home/Peripherals/SiteSurveyTool/Frequncy_Heat_File_Plotter.py -a /home/cvuser/Desktop/$sitename
echo 'zipping the files...\n'
cd ~/Desktop
zip -r $sitename $sitename
sudo rm -r $sitename
echo 'Survey finished, press Enter to exit...\n'
read key

