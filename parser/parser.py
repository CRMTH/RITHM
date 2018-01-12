# -*- coding: utf-8 -*-

import time, os 
#import re, sys
from decode import decoder
from combine import csvcombine

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

kwMode = False 
for line in open(dir_path+'template.txt'):
    # ignore hashed-out lines and blank lines
    if (line[:1] !='#' and line.strip()!=''):
        # split line into cmd & val pairs using a colon, where appropriate
        items = line.split(':')
        if len(items) > 1:
            cmd = items[0].strip().lower()
            val = ':'.join(items[1:]).strip()
            cmdval = True
        else:
            cmd = None
            val = str(line).strip()
            cmdval = False
    
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
            
            # hiMem setting should be based on file size and amount of working memory (i.e., RAM)
            # If hiMem == True, then full JSON files will be moved to working memory for parsing 
            # this is faster but more memory intensive. 
            if cmd.lower() in ['memory', 'mem', 'himem']:
                if val.lower() in ['high', 'fast'] or val in confirm:
                    hiMem = True
                else:
                    hiMem = False
                

            # set "start" and "stop" date strings to select input files to parse
            # format is YYYYMMDD, inclusive 
            if cmd.lower() in ['start','begin', 'first']:
                start = int(val)
            if cmd.lower() in ['stop','end', 'last']:
                end = int(val)
    
            # set combine to dictate how output files are combined
            # NEED TO DOCUMENT THIS!
            if cmd == 'combine':
                combine = val
        
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

# read data files in dirIn
files = sorted(os.listdir(dirIn))
print("\nREADING TWEETS FROM " + str(start) + ' to ' + str(end) +'\n')
t = str(time.time())
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

c = csvcombine(dirOut, dir_path, dirTemp)
c.combinecsv(combine, clear)
