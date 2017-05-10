# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 15:49:37 2017

@author: GMTemp
"""

import os, csv, re

#directory_in = 'C:/Users/Coldjb/Desktop/CSVs/'
#directory_out = 'C:/Users/Coldjb/Desktop/'
#directory_in = '/pylon2/db4s82p/jcolditz/twitter/emojified/'
directory_out = directory_in
files = sorted(os.listdir(directory_in))

fileCount = 0
for f in files:
    if f[-4:] == '.csv':
        ####### IF THERE IS NO HEADER, REMOVE THE LINE fileCount += 1 ######
        ####### THAT WILL KEEP IT ON THE if PORTION THAT GETS EVERY LINE #####
        if fileCount == 0:
            with open(directory_out + 'MasterCSV.csv', 'ab') as csvfile:
                #saveFile = csv.writer(csvfile, delimiter=',', dialect='excel')
                saveFile = csv.writer(csvfile, delimiter=',')
                with open(directory_in + f, 'rb') as read:
                    for line in read:
                        line = re.sub('\r', '', line)
                        line = re.sub('\n', '', line)
                        cells = line.split(',')
                        saveFile.writerow([cell for cell in cells])
            fileCount += 1 ### THIS ONE ### 
        else:
            with open(directory_out + 'MasterCSV.csv', 'ab') as csvfile:
                saveFile = csv.writer(csvfile, delimiter=',')
                with open(directory_in + f, 'rb') as read:            
                    count = 0
                    for line in read:
                        if count == 0:
                            doNothing = 0 #this will skip over the header                        
                        else:
                            line = re.sub('\r', '', line)
                            line = re.sub('\n', '', line)
                            cells = line.split(',')
                            saveFile.writerow([cell for cell in cells])
                        count += 1