# -*- coding: utf-8 -*-

import time, os 
#import re, sys
from decode import decoder
from combine import csvcombine

dir_path = "//home/jason/repos/RITHM/decoder/"

try: 
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/'
except: 
    print('Failed to set dir_path programmatically!\n',
              'Parser works better if run from command line.\n',
              'Setting dir_path to: ', dir_path)
    input('Press Enter to continue...')


#lineCount = 0
kwMode = False
for line in open(dir_path+'template.txt'):
    # ignore hashed-out lines and blank lines
    if line[:1] =='#' or line.strip()=='':
        pass
    else:
        # try to split line into cmd, val pairs using a colon
        try:
            cmd = line.split(':')[0].strip().lower()
            val = str(line.split(':')[1]).strip()
            cmdval = True
        # otherwise, treat entire line as val
        except:
            cmd = None
            val = line
            cmdval = False
            pass
    
        # begin parsing cmd, val pairs into working variables
        if cmdval:
            # set directories for input, temp, and output
            if cmd in ['dir_in','dirin']:
                dirIn = val
            if cmd in ['dir_temp','dirtemp']:
                dirTemp = val
            if cmd in ['dir_out','dirout']:
                dirOut = val
            
            # set "start" and "stop" date strings to select input files to parse
            # format is YYYYMMDD, inclusive 
            if cmd in ['start','begin']:
                start = val
            if cmd in ['stop','end']:
                end = val
    
            # set combine to dictate how output files are combined
            # NEED TO DOCUMENT THIS!
            if cmd == 'combine':
                combine = val
        
            # set the CSV file to use for emoji translations
            # NEED TO DOCUMENT THIS!
            if 'emoj' in cmd:
                emojify = 1 # FIX THIS DEPENDENCY
                if '.csv' in val:
                    emoji_file = dir_path+val
                else:
                    emoji_file = None
                #emojify == 1
    
            # set "clear" to True, to clear temp files before decoding
            # TO-DO: clear tempDir and/or outDir separately
            if cmd in ['clear']:
                if val.lower() in ['true','yes','1','clear']:
                    clear = True
                else:
                    clear = False
        
            # set "geo" to True, to retrieve only geotagged tweets
            if cmd == 'geo':
                if val.lower() in ['true','yes','1','geo']:
                    geo = True
                else:
                    geo = False
                    
        
            # set "test" variable (not yet implemented)
            if cmd == 'test':
                if val.lower() in ['true','yes','1','test']:
                    test = True
                else:
                    test = False
    
            # look for the "keywords" command (should be the last command)
            # all lines after this will be treated as keyword parameters
            if cmd in ['keywords','kws']:
                keywords = {}
                if val == '':
                    kwMode = True
                else:
                    # different types of modes may come in handy later?
                    kwMode = val.lower()
            
        # append all remaining lines to the keyword parameter list
        # NEED TO DOCUMENT THIS!
        if kwMode:
            if cmd:
                # keywords are not read from the initial "keywords" line
                pass
            else:
                if line not in keywords.keys():
                    keywords.update({line.rstrip():0})


# clear EVERYTHING from "dirTemp" and "dirOut"
if clear in ['true','1','yes','clear']:
    for f in sorted(os.listdir(dirTemp)):
        os.remove(dirTemp+f)
    for f in sorted(os.listdir(dirOut)):
        os.remove(dirOut+f)

# read data files in dirIn
files = sorted(os.listdir(dirIn))
print("\nREADING TWEETS FROM " + str(start) + ' to ' + str(end) +'\n')
t = str(time.time())
for f in files:
    if f[-5:] =='.json':
        #try:
        if int(f[:8]) >= int(start):
            if int(f[:8]) <= int(end):
                d = decoder(keywords, dirOut, dirIn, dirTemp, emojify, emoji_file)
                record = d.fixjson(dirIn, f)
                d.jsontocsv(record,f,geo,emojify)
        #except:
        #    print("Incorrect format: ",f)
        #    continue

c = csvcombine(dirOut, dir_path, dirTemp)
c.combinecsv(combine, clear)
