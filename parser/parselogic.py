# -*- coding: utf-8 -*-
"""
This script defines functions used throughout the RITHM repository. 
Changes here will broadly impact RITHM functionality. Handle with care.

Created on 2018-05-29
@author: colditzjb

"""
import os, datetime, re, sys

### cmdvars function
#
# Set default variables and look for additional command line input. 
# Output a dictionary of variables used in various other RITHM scripts.
#
###
def cmdvars(args=sys.argv):
    make_dir = False
    sub_dir = False
    d = {}

    # Default directory values
    d['dir_in'] = './'
    d['dir_in_kws'] = None
    d['dir_out'] = None

    # Default file extension and delimiter
    d['f_ext'] = '.tsv'
    d['delimiter'] = '\t'
    
    # Default file stem
    d['f_stem'] = ''

    # Default datestamps in filename-type format (int; YYYYMMDD)
    #d['start'] = 20060321 # Default to first tweet in recorded history 
    d['start'] = 20170101 # Default to 1/1/2017 
    d['end'] = 20301231 # Default to 12/31/2030

    # Default retweet handling
    d['rt_include'] = False
    d['rt_ignore'] = True
    d['rt_status'] = '_noRTs'

    #keywords = []

    if len(args) > 1: # If command line arguments were passed
        i = 0
        for arg in args:

            # '-date' indicates start/end dates (req. 2 MMDDYYYY objects)
            if arg.lower() in ['-date','-dates']:
                d['start'] = int(args[i+1])
                d['end'] = int(args[i+2])

            # '-dir' indicates input directory (MUST include trailing slash)
            if arg.lower() in ['-dir','-in','-indir','-dirin']:
                d['dir_in'] = str(args[i+1])

            # '-dirkws' indicates input directory for KWS files (MUST include trailing slash)
            if arg.lower() in ['-dirkws','-dirkw','-kwsdir','-kwdir']:
                d['dir_in_kws'] = str(args[i+1])

            # '-out' indicates output directory (MUST include trailing slash)
            # '-mkout' will create that directory if it does not exist
            # dir_out starting with './' will make subdirectory of dir_in
            if arg.lower() in ['-out','-dirout','-outdir','-mkdir','-mkout']:
                d['dir_out'] = str(args[i+1])
                if arg.lower() in ['-mkdir', '-mkout']:
                    make_dir = True
                if d['dir_out'][0:2] == './':
                    make_dir = True
                    sub_dir = True

            # '-fstem' indicates a stem to append to beginning of output file name
            if arg.lower() in ['-filestem','-fstem','-stem','-fs']:
                d['f_stem'] = str(args[i+1])+'_'

            # '-ext' indicates file extension (MUST include the ".")
            # '-csv' is a shortcut that requires no additional argument
            if arg.lower() in ['-ext','-extension','-fext', '-csv']:
                if arg.lower() == '-csv':
                    d['f_ext'] = '.csv'
                    d['delimiter'] = ','
                else:
                    d['f_ext'] = lower(str(args[i+1]))
                    if d['f_ext'] == '.csv':
                        d['delimiter'] = ','

            # '-rt' indicates that RTs should be included
            if arg.lower() in ['-rt', '-rts']:
                d['rt_include'] = True
                d['rt_ignore'] = False
                d['rt_status'] = '_withRTs'

            i+=1

        if d['dir_in_kws'] is None:
            d['dir_in_kws'] = d['dir_in']
        if d['dir_out'] is None:
            d['dir_out'] = d['dir_in']
            
        if sub_dir:
            dir_out = d['dir_in']+d['dir_out'][2:]
            d['dir_out'] = dir_out
        if make_dir:
            mkdir(d['dir_out'])
            

    return d
"""
Here's example syntax for using cmdvars function in other RITHM scripts.
This is here for easy copy/paste - not all values are used by all scripts.

    cv = parselogic.cmdvars()
    start = cv['start']
    end = cv['end']
    dir_in = cv['dir_in']
    dir_in_kws = cv['dir_in_kws']
    dir_out = cv['dir_out']
    f_stem = cv['f_stem']
    f_ext = cv['f_ext']
    delimiter = cv['delimiter']
    rt_include = cv['rt_include']
    rt_ignore = cv['rt_ignore']
    rt_status = cv['rt_status']

"""


### filelist function
#
# Returns a list of files matching certain criteria within a given directory. 
#    
#    "tsv_type" settings: 
#       "raw" handles tsv files as daily tweet files ("start" and "end" req.)
#
###
def filelist(dir_in, f_ext='.tsv', tsv_type='raw', start=None, end=None, silent=False, quiet=True):
    if silent == True: quiet = True
    files_list = []
    files_all = os.listdir(dir_in)
    files_all.sort()
    if not silent: print('\n----- '+f_ext+' files in '+dir_in)
    for f in files_all:
        if f[-4:] == f_ext:
            if f_ext in ['.tsv','.csv']:
                if tsv_type=='raw':
                    try:
                        if int(f[:8]) >= int(start):
                            if int(f[:8]) <=int(end):
                                files_list.append(f)
                                if not silent: print(f+' included')
                            else: 
                                if not quiet: print(f+' excluded')
                        else: 
                            if not quiet: print(f+' excluded')
                    except: 
                        if not quiet: print(f+' ignored')
                        pass
                else:
                    pass # May need to handle other types of TSV files later?

            else:
                if not silent: print(f+' included')
                files_list.append(f)

    return sorted(files_list)


### kwslist function
#
# Returns de-duplicated list of keywords from ALL .kws type files in a dir. 
#   Each line is treated as a separate keyword string. 
#   Blank lines and hashed-out lines are ignored. 
#
###
def kwslist(dir_in_kws, f_ext='.kws', silent=False):
    kws_list = []
    kws_files = filelist(dir_in_kws, f_ext=f_ext, silent=silent)
    for f in kws_files:
        with open(dir_in_kws+f, 'r') as o:
            for l in o: #for line in open file
                if len(l.strip())>0 and l[0] != '#':
                    kws_list.append(l.strip())
                else:
                    pass
    if not silent:
        print('\nKeyword filters:')
        print(sorted(list(set(kws_list))))
        print('')
    return sorted(list(set(kws_list)))


### mkdir function
#
# A scrappy way to create a new directory if it's not there. Use this function
# on a directory before trying to write out new files to it. 
#
#   "dirs" argument can handle a string or list of strings that correspond 
#       to one or more directories to search for and create if not there.
#       This argument is REQUIRED and strings must end with a "/"
#
#   "base" argument is an optional parent directory to work from.
#       This must be a string ending with "/"
#
###
def mkdir(dirs, base='', silent=False):
    def makeit(base, dira):
        if dirs[-1] != '/':
            if not silent:
                print('')
                print(str(base)+str(dira)+' directory was not created.')
                print('Directory string must end with a forward slash.\n')
        elif not os.path.exists(base+dira):
            os.makedirs(base+dira)
            if not silent:
                print('\nNew directory created:'+str(base)+str(dira)+'\n')

    if base is str and len(base)>0 and base[-1] != '/':
        if not silent:
            print('')
            print(str(base)+' is not a valid base path.')
            print('Directory string must end with a forward slash.\n')
        return None
    else:
        if type(dirs) is str:
            makeit(base, dirs)
        elif type(dirs) is list:
            for d in dirs:
                makeit(base, d)
        else:
            if not silent:
                print('')
                print(str(dirs)+' is not valid input.')
                print('mkdir(dirs) must be string or list format.\n')
            return None


### emojify function
#
# Documentation not provided.
# This is used in reformat function.
#
###
def emojify(text, emojis):
    if '\\u' in text.lower():
        text = text.replace('\\U' , '\\u')
        text = text.replace('\\u' , ' \\u')
        words = text.split(' ')

        for word in words:
            if '\\u' in word:
                if word in emojis.keys():
                    words[words.index(word)] = emojis[word]
                elif word[0:10] in emojis:
                    word_1 = word[10:len(word)]
                    words[words.index(word)] = emojis[word[0:10]] + ' ' + word_1
                elif word[0:6] in emojis:
                    word_1 = word[6:len(word)]
                    words[words.index(word)] = emojis[word[0:6]] + ' ' + word_1
                elif word[0:4] in emojis:
                    word_1 = word[4:len(word)]
                    words[words.index(word)] = emojis[word[0:4]] + ' ' + word_1


        return ' '.join(words)
    return text
                    
                    
"""
                #This is an old approach. May have additional processing overhaed
                else:
                    stem = ''
                    i_char = 0
                    done = False
                    for char in word:
                        stem += char
                        i_char += 1
                        if stem in emojis.keys():
                            words[words.index(word)] = emojis[stem]+' '+word[i_char:]
                            break
"""


# This is a crude, hierarchical way to organize modes for reformat function
modes = {'tsv':'1.0',
         'csv':'1.5',
         'two':'2.0',
         'mac':'2.5',
         'hum':'3.5',
         'kws':'4.5'}

### reformat function
# 
# This reformats text so that it is keyword searchable or machine/human readable
# Format selection relies on bandwidths of float numbers (as above, so below)
#   "mode" argument options currently include: 
#     1.0 'tsv' = Only replace tabs, and hard returns (TSV compatability) 
#                 This is currently the default for output. 
#     1.5 'csv' = Replace commas, tabs, and hard returns (CSV compatability) 
#     2.0 'two' = Use O'Connor "Twokenize.py" for formatting
#     2.5 'mac' = Standard machine processing (buffer spacing for tokenizing)
#     2.x [TBD] = More machine processing (include modes for stemming, etc.)
#     3.5 'hum' = Format for maximum human readability (useful for annotation)
#     4.5 'kws' = Format for keyword matching (default for search procedures)
#
#   "lcase" argument is optional. All text will be reduced to lowercase. 
#   "ht_include" argument is optional. Includes hashtags w/ basic keywords. 
#   "emoji" argument contains the emoji dict. Will be empty if filepath invalid. 
###
def reformat(text, emojis, mode=1.0, modes=modes, 
             lcase=False, ht_include=True):
    
    # It's faster to use numbers instead of dictionary matching of text!
    try:
        mode = float(mode)
    except:
        if mode in modes: # Match strings to values and convert to floats
            for k, v in modes.items(): 
                if mode == k:
                    mode = modes[k]
                    try:
                        mode = float(mode)
                    except:
                        print('reformat(mode) value failed to convert from str to float')
                        pass
        else:
            print('reformat(mode) value not recognized')
            pass
        
    # Always buffer whitespace for matching text
    text = ' '+text+' '

    # This reformats the unicode objects so we can work with them 
    text = str(text.encode('unicode-escape'))[2:-1]

    text = text.replace('\\\\', '\\') #Fixing backslach escapes

    # https://stats.seandolinar.com/collecting-twitter-data-converting-twitter-json-to-csv-ascii/
    # This was good, in theory, but completely borked file input
    #text = text.encode('unicode_escape') # THIS BELONGS WITH INPUT PROCEDURES, IF USEFUL 

    # Lower case happens when requested or at "mode" 4+ by default
    if lcase:
        text = text.lower()
    elif mode >= 4:
        text = text.lower()

    # Commas/returns/tabs get recoded because CSV output
    # WE MAY WANT TO OUTPUT AS TAB-SEPARATED TO PRESERVE COMMAS (FOR TWOKENIZE)
    text = text.replace('\\n', ' _newline_ ') #Newline
    text = text.replace('\\r', ' _newline_ ') #Newline
    text = text.replace('\\t', ' ') #Tab

    if mode == 1.5:
        text = text.replace(',0', '0') #Comma in common number
        text = text.replace(',', ' - ') #Comma to hyphen


    # Reformat common punctuation oddities
    text = text.replace('\\u2026' , '...')
    text = text.replace('\\u2122' , '...')
    text = text.replace('\\u2018' , "'") #Slanted left single quote
    text = text.replace('\\u2019' , "'") #Slanted right single quote
    text = text.replace('\\\'', "'") #Escaped single quote
    text = text.replace('`', "'")
    text = text.replace('\\u201c' , '"') #Slanted left double quotes
    text = text.replace('\\u201d' , '"') #Slanted right double quotes
    text = text.replace('\\u200d' , '') #Zero-width character
    text = text.replace('\\u2014' , '-') #Em-dash
    #text = text.replace('\\u' , ' \\u') # CHECK THIS
    text = text.replace('\\xa0', ' ') #Non-breaking space
    text = text.replace('&nbsp;', ' ') #Non-breaking space
    text = text.replace('&amp;', '&')
    text = text.replace('&gt;', '>')
    text = text.replace('&lt;', '<')

    if mode >= 4:
        ht_include = True
        
        # Buffer common punctuation with spaces for word matching
        text = text.replace('(', ' ( ')
        text = text.replace(')', ' ) ')
        text = text.replace('[', ' [ ')
        text = text.replace(']', ' ] ')
        text = text.replace('"', ' " ')
        text = text.replace("'", " ' ")
        text = text.replace('*', ' * ')
        text = text.replace('-', ' - ')
        text = text.replace('.', ' . ')
        text = text.replace(',', ' , ')
        text = text.replace('!', ' ! ')
        text = text.replace('?', ' ? ')
        text = text.replace(':', ' : ')
        text = text.replace(';', ' ; ')
        text = text.replace('&', ' & ')
        text = text.replace('>', ' > ')
        text = text.replace('<', ' < ')
        text = text.replace('\\', ' \\')
    
    if ht_include:
        # This is important so that keywords can match hashtagged keywords
        text = text.replace('#', '# ')
        

    # Repair hyperlinks
    text = re.sub(r' \: \/\/', '://', text)
    text = re.sub(r't . co', 't.co', text)

    # Repair quote on rt
    #text = re.sub(r'\"rt', 'rt', text)
    
    # These are for human-readable text formatting only
    if 3 <= mode < 4:
    # Format more punctuation oddities
        while '  ' in text:
            text = text.replace('  ' , ' ')
        while '. .' in text:
            text = text.replace('. .' , '..')
        while '....' in text:
            text = text.replace('....' , '...')
        while '- -' in text:
            text = text.replace('- -' , '--')
        while '----' in text:
            text = text.replace('----' , '---')

    # If emojis is non-empty, convert unicode emoji and symbols 
    # to human readable text using emoji dictionary
    if emojis:
        text = emojify(text, emojis)
    text = text.replace('\n', '_newline_')
    #text = text.replace('\\\\', '\\') #Fixing backslach escapes
    return text


### reformat function
# 
# This performs matching on text, using boolean test phrases
#
###
def match(test, text):
    ### Term syntax includes '*' as wildcard and '!' as NOT operator
    # wildcards do not respect space delimitations (full-text inclusive)
    # "!" operator may have undesirable Boolean behavior: use with caution!

    test = test.replace('! ' , '!') # Remove space after "!" for processing
    
    test = test.replace('#' , '# ') # Reformat to catch hashtags as keywords...
    while '  ' in test:
        text = test.replace('  ' , ' ') # Make multuple spaces into single spaces 


    
    def TermMatch(kw, text, matched=False):
    
        # this pads spacing to adjust kw for wildcards
        def spaced(kw):
            if kw[-1] == '*':
                if kw[0] == '*':
                    kw = kw[1:-1]
                else: 
                    kw = ' '+kw[:-1]
            elif kw[0] == '*':
                kw = kw[1:]+' '
            else:
                kw = ' '+kw+' '
            return kw

        # test for kw in text
        if spaced(kw) in text:
            matched = True

        # test for !kw not in text    
        if kw.strip()[0] == '!':
            if spaced(kw.strip()[1:]) not in text:
                matched = True
    
        return matched
    
    ### Logic syntax: '&' = AND, '|' = OR
    # AND statements always take precedence over OR statements
    # multiple OR statements can be processed within multiple AND statements
    # AND statements are never processed within OR statements
    def LogicMatch(test, text, matched=False):
        match = 0
        
        if '&' in test:
            kws = test.split('&')
            for k in kws:
                if '|' in k:
                    if LogicMatch(k, text):
                        match += 1
                elif TermMatch(k.strip(), text):
                    match += 1
            if match >= len(kws):
                matched = True
            
        elif '|' in test:
            kws = test.split('|')
            for k in kws:
                if TermMatch(k.strip(), text):
                    match += 1
            if match >= 1:
                matched = True
    
        else:
            if TermMatch(test.strip(), text):
                matched = True
            
        return matched

    ### A placeholder for implementing parentheses in logic syntax later on
    # Boolean parentheses are not currently implemented - don't use them!
    # this currently defaults to basic LogicMatch() functionality
    def ParentMatch(test, text):
        # This implements 'return all tweets' behavior at the top-most level
        if test.strip() == '***':
            return True

        # This runs LogicMatch and returns the result of that
        return LogicMatch(test, text)
        
    # Returns True/False for a logical keyword test within a given text
    return ParentMatch(test, text)


###############################################################################


### OTHER FUNCTIONS
# 
# THESE ARE EITHER EXPERIMENTAL OR DEPRECATED
#
###


### ts function 
#
# TO BE DEPRECATED AND REPLACED (there is a better version underway)
#
# Output a timestamp string in "YYYYMMDDhhmmss" format. 
#
#    ts() = current date/time.
#    
#    "stamp" argument takes a Twitter-formatted timestamp and converts it.
#
###
def ts(stamp=None, reform=None):
    fail = False
    if stamp is None:
        timestamp = str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
        r = timestamp
    else:
        months={'Jan':'01','Feb':'02','Mar':'03','Apr':'04',
                'May':'05','Jun':'06','Jul':'07','Aug':'08',
                'Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
        try: # This will convert Twitter timestamp to standard format
            d = stamp.split(' ')
            m = months[d[1]]
            t = d[3].split(':')
            r = d[5]+m+d[2]+t[0]+t[1]+t[2]
        except:
            if len(stamp)==14:
                r = stamp
            else:
                r='Failed to parse timestamp!'
                fail=True
    if reform and not fail: # This will output a readable timestamp for analysis
        d = '/'.join([r[4:6],r[6:8],r[:4]])
        t = ':'.join([r[8:10],r[10:12],r[12:14]])
        r = d+' '+t
    return r



### locmatch function
#
# This is only a placeholder. There is a potential use case in freq_out.py 
# Not expected to be a high priority for future development.
#
###
def locmatch(location):
    if 'pennsylvania' in location.lower():
        return 1
    elif ', PA' in location:
        return 1
    else:
        return 0

