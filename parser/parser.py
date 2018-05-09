# -*- coding: utf-8 -*-

import os
import sys
from decode import decoder
#from combine import csvcombine

dir_path = './' #Default path 
confirm = ['true','yes','1'] #Possible responses to indicate "True"
deny = ['false','no','0'] #Possible responses to indicate "False"

try: 
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/'
except: 
    print('Failed to set dir_path programmatically!\n',
              'Parser works better if run from command line.\n',
              'Setting dir_path to: ', dir_path)
    input('Press Enter to continue...')

template = 'template.ini'

if len(sys.argv) > 1: #If command line arguments were passed
    i = 0
    for arg in sys.argv:
        if arg.lower() == '-f': # '-f' indicates template file input
            template = str(sys.argv[i+1])
        if arg.lower() == '-d': # '-d' indicates start/end dates
            start = int(sys.argv[i+1])
            end = int(sys.argv[i+2])
        i = i+1


kwMode = False 
for line in open(dir_path+template):
    # ignore hashed-out lines and blank lines
    if (line.strip()[:1] !='#' and line.strip()!=''):
        # try to split line into cmd, val pairs using a colon
        try:
            cmd = line.split(':')[0].strip().lower()
            val = str(line.split(':')[1]).strip()
            cmdval = True
        # otherwise, treat entire line as val
        except:
            cmd = None
            val = str(line).strip()
            cmdval = False
            pass
    
        # begin parsing cmd, val pairs into working variables
        if cmdval:
            # set directories for input, temp, and output
            if cmd == 'dir_self':
                dirSelf = val
            if cmd == 'dir_in':
                dirIn = val
            if cmd == 'dir_temp':
                dirTemp = val
            if cmd == 'dir_out':
                dirOut = val
            
            # set "start" and "stop" date strings to select input files to parse
            # format is YYYYMMDD, inclusive 
            if cmd.lower() in ['memory', 'mem', 'himem']:
                if val.lower() in ['high', 'fast'] or val in confirm:
                    hiMem = True
                else:
                    hiMem = False
                

            # set "start" and "stop" date strings to select input files to parse
            # format is YYYYMMDD, inclusive 
            if cmd in ['start','begin', 'first'] and not start:
                start = int(val)
            if cmd in ['stop','end', 'last'] and not end:
                end = int(val)
    
            # set combine to dictate how output files are combined
            # NEED TO DOCUMENT THIS!
            if cmd == 'combine':
                combine = val
                if val.lower() in confirm:
                    combine = True
                else:
                    combine = False
        
            # set the CSV file to use for emoji translations
            # NEED TO DOCUMENT THIS!
            if 'emoj' in cmd.lower():
                emojify = 1 # FIX THIS DEPENDENCY
                if '.csv' in val:
                    emojiFile = dir_path+val
                else:
                    emojiFile = None
    
            # set "clear" to True, to clear temp files before decoding
            # TO-DO: clear tempDir and/or outDir separately
            if cmd.lower() == 'clear':
                if val.lower() in confirm:
                    clear = True
                else:
                    clear = False
        
            # set "geo" to True, to retrieve only geotagged tweets
            if cmd == 'geo':
                if val.lower() in confirm:
                    geo = True
                else:
                    geo = False
                    
            # set "test" variable (not yet implemented)
            if cmd == 'test':
                if val.lower() in confirm:
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
                if val not in keywords.keys():
                    keywords.update({val.strip() : 0})
                    print(val)            
    else:
        continue



# clear EVERYTHING from "dirTemp" and "dirOut"
if clear in ['true','1','yes','clear']:
    for f in sorted(os.listdir(dirTemp)):
        os.remove(dirTemp+f)
    for f in sorted(os.listdir(dirOut)):
        os.remove(dirOut+f)

#t = str(time.time())

# read data files in dirIn
files = os.listdir(dirIn)
files.sort()
print("\nREADING TWEETS FROM " + str(start) + ' to ' + str(end) +'\n')
for f in files:
    if f[-5:] =='.json':
        #try:
        if int(f[:8]) >= int(start):
            if int(f[:8]) <= int(end):
                d = decoder(keywords, dirIn, dirTemp, dirOut, 
                            hiMem, emojiFile)
                record = d.fixjson(dirIn, f, hiMem, emojiFile)
                #d.jsontocsv(record,f,geo,emojify, count=0)
        #except:
        #    print("Incorrect format: ",f)
        #    continue
"""
if combine:
    c = csvcombine(dirOut, dir_path, dirTemp)
    c.combinecsv(combine, clear)
"""
