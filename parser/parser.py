# -*- coding: utf-8 -*-

import os
import sys
from decode import decoder

dir_path = './' #Default path 
confirm = ['true','yes','y','1'] #Possible responses to indicate "True"
deny = ['false','none','no','n','0',''] #Possible responses to indicate "False"

# Set these to None so command line parsing works when not defined
hiMem = None
loMem = None
start = None 
end = None
logging = None
emoji = None
# These are default values in case 
lcase = False
mode = 1.0

#Dictionaries to keep track of duplicate tweets across all parsed files
yesterday_dict = {}
today_dict = {}

try: 
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/'
except: 
    print('Failed to set dir_path programmatically!\n',
              'Parser works better if run from command line.\n',
              'Setting dir_path to: ', dir_path)
    input('Press Enter to continue...')

template = 'template.par' # Default template file


if len(sys.argv) > 1: # If command line arguments were passed
    i = 0
    try:
        for arg in sys.argv:
            # '-f' indicates template file input (req. 1 file object)
            if arg.lower() in ['-f','-file']:
                template = str(sys.argv[i+1])
                if '/' in template:
                    dir_path = '' # Ignore dir_path if directory is defined

            # '-d' indicates start/end dates (req. 2 MMDDYYYY objects)
            if arg.lower() in ['-d','-date','-dates']:
                start = int(sys.argv[i+1])
                end = int(sys.argv[i+2])

            # DEPRECIATED: indicates hiMem=True
            #if arg.lower() in ['-h','-hi','-himem','-high','-highmem']:
            #    hiMem = True

            # indicates hiMem=False
            if arg.lower() in ['-l','-lo','-lomem','-low','-lowmem']:
                loMem = True
            i = i+1
    except:
        print ('Command line arguments failed to parse.\n',
               'Using default '+template+' settings.')

### PARSING KEYWORDS AND SETTING VALUES
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
            val = str(line).strip()#.lower() #.lower isn't needed here
            cmdval = False
            pass
    
        # begin parsing cmd, val pairs into working variables
        if cmdval:

            # set directories for input, temp, and output
            if cmd == 'dir_self':
                dirSelf = val
            if cmd == 'dir_in':
                dirIn = val
            if cmd == 'dir_out':
                dirOut = val
            #if cmd == 'dir_temp':
            #    dirTemp = val


            # hiMem settings
            #  
            himemset = ['high', 'hi', 'fast'] + confirm
            if cmd.lower() in ['memory', 'mem', 'himem']:
                if val.lower() in himemset and not hiMem:
                    hiMem = True
                else:
                    hiMem = False
            if loMem:
                hiMem = False


            # set "start" and "stop" date strings to select input files to parse
            # format is YYYYMMDD, inclusive 
            if cmd in ['start','begin', 'first'] and not start:
                start = int(val)
            if cmd in ['stop','end', 'last'] and not end:
                end = int(val)
    
            # set "mode" variable
            if cmd in ['mode','parse','parser']:
                try: mode = float(val)
                except: mode = str(val)


            # set "test" variable
            if cmd in ['test','testing','log','logging']:
                if val.lower() in deny:
                    logging = False
                elif val.lower() in confirm:
                    logging = True
                    from datetime import datetime
                    from datetime import timedelta

                else:
                    #May want more parameters later
                    logging = False
                    from datetime import datetime
                    from datetime import timedelta

            # set "lcase" variable
            if cmd in ['lcase', 'lower']:
                if val.lower() in confirm:
                    lcase = True
                else:
                    lcase = False

            # set the CSV file to use for emoji translations
            # NEED TO DOCUMENT THIS!
            if 'emoj' in cmd.lower():
                if val in deny:
                    emoji = None
                elif '.csv' in val:
                    emoji = dir_path+val # MAY NEED TO UPDATE DIRECTORY!
                else:
                    emoji = None


            # DEPRECIATED: set combine to dictate how output files are combined
            #if cmd == 'combine':
            #    combine = val
            #    if val.lower() in confirm:
            #        combine = True
            #    else:
            #        combine = False
    
            # DEPRECIATED: set "clear" to True, to clear temp files before decoding
            #if cmd.lower() == 'clear':
            #    if val.lower() in confirm:
            #        clear = True
            #    else:
            #        clear = False
        
            # DEPRECIATED: set "geo" to True to retrieve only geotagged tweets
            #if cmd == 'geo':
            #    if val.lower() in confirm:
            #        geo = True
            #    else:
            #        geo = False
                    
    

            # look for the "keywords" command (should always be last command!)
            # all lines after this will be treated as keyword parameters
            if cmd in ['keywords','kws']:
                keywords = []
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
                print('KEYWORDS:')
                pass
            else:
                if val not in keywords:
                    keywords.append(val.strip())
                    print(val)
    else:
        continue



# clear EVERYTHING from "dirTemp" and "dirOut"
#if clear in ['true','1','yes','clear']:
#    for f in sorted(os.listdir(dirTemp)):
#        os.remove(dirTemp+f)
#    for f in sorted(os.listdir(dirOut)):
#        os.remove(dirOut+f)

#t = str(time.time())

# read data files in dirIn
files = os.listdir(dirIn)
files.sort()
print('\n\nSTART_DATE: '+str(start))
print('END_DATE:   '+str(end))
if logging:
    print('HIMEM_SET:  '+str(hiMem))
    t0=datetime.now()
    print('RUN_START:  '+str(t0))

N_tweets = 0
N_matches = 0
N_warnings = 0
N_errors = 0
#N_duplicates = 0
#N_large_duplicates = 0

for f in files:
    if f[-5:] =='.json':
        #try:
        if int(f[:8]) >= int(start):
            if int(f[:8]) <= int(end):
                d = decoder(keywords, dirIn, dirOut, 
                            hiMem, mode, lcase, emoji, logging, yesterday_dict, today_dict)
                #record = d.fixjson(dirIn, f, hiMem, emojiFile)
                record = d.fixjson(dirIn, f, hiMem)

                if logging:
                    print('\n# FILE STATS #') 
                    print('FILE:       '+ str(f))
                    n_tweets = d.n_tweets
                    N_tweets += n_tweets
                    print('TWEETS:     '+ str(n_tweets))
                    n_matches = d.n_matches
                    N_matches += n_matches
                    print('MATCHES:    '+ str(n_matches))
                    n_warnings = d.n_warnings
                    N_warnings += n_warnings
                    print('WARNINGS:   '+ str(n_warnings))
                    n_errors = d.n_errors
                    N_errors += n_errors
                    print('ERRORS:     '+ str(n_errors))
                    #log duplicate tweet counts
                    #n_duplicates = number of keys in d.yesterday_dict and d.today_dict > 1
                    #N_duplicates += n_duplicates
                    #log large duplicates
                    #n_large_duplicates = number of keys in d.yesterday_dict and d.today_dict > 10
                    #N_large_duplicates += n_large_duplicates
                yesterday_dict = d.today_dict
                today_dict = {}
                #d.jsontocsv(record,f,geo,emojify, count=0)
        #except:
        #    print("Incorrect format: ",f)
        #    continue
if logging:
    t1 = datetime.now()
    seconds=timedelta.total_seconds(t1-t0)
    print('\n\n### RUNTIME TOTALS ###')
    print('SECONDS:    '+str(seconds))
    print('MINUTES:    '+str(seconds/60))
    print('HOURS:      '+str((seconds/60)/60))
    print('DAYS:       '+str(((seconds/60)/60)/24))
    print('\n\n### TOTAL COUNTS ###')
    print('N_TWEETS:    '+str(N_tweets))
    print('N_MATCHES:   '+str(N_matches))
    print('N_WARNINGS:  '+str(N_warnings))
    print('N_ERRORS:    '+str(N_errors))
    #Print duplicate tweet stats
    
#if combine:
#    c = csvcombine(dirOut, dir_path, dirTemp)
#    c.combinecsv(combine, clear)
