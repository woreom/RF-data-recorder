===============================================================================
Instructions for running SiteSurvey Tools
===============================================================================
1.Open a terminal 'ctrl'+'alt'+'t'

2.Copy following command using 'ctrl+c' and paste to the terminal using 'ctrl+alt+v', add the file name after '-n' option 
  
  sudo python /home/Peripherals-SiteSurveyTools/SiteSurveyTool/Frequency_Heat_Map_Generator.py -a 1 -n <file name>

  Notice:<file name> should contain information of deployment and location for future reference, don't add any special character or space inside file name, you can use '_' or '-' to seperate names

3.Hit 'enter' and run program, type password if needed, a file will be generated at Desktop with the name <file name>_startFreq_stopFreq_TimeStamp.txt

4.After finishing multiple locations at one deployment, zip all files in the same .zip and name it using the deployment name
