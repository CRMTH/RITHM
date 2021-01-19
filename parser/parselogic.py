# -*- coding: utf-8 -*-
"""
This script defines functions used throughout the RITHM repository. 
Changes here will broadly impact RITHM functionality. Handle with care.

Created on 2018-05-29
@author: colditzjb

"""
import os, datetime, re, sys


### t_col function
#
# Returns column number (i.e., list position) if valid variable name is passed. 
# Returns variable name if integer is passed. This is useful for quickly 
# locating and converting between variable names and list positions.
# If no tc_in value is passed, it will return col_dict itself.
#
###
def t_col(tc_in=None, head=None, delimit='\t'):

    if head is None:
        col_dict = {
            'u_id': 0,
            'u_handle': 1,
            'u_name': 2,
            'u_desc': 3,
            'u_url': 4,
            'u_create': 5,
            'u_tweets': 6,
            'u_fo_out': 7,
            'u_fo_in': 8,
            'u_likes': 9,
            'u_utcoff': 10,
            'u_locate': 11,
            'u_geotag': 12,
            'u_lang': 13,
            'u_imgurl': 14,
            'u_bgurl': 15,
            'u_privat': 16,
            'u_verify': 17,
            'u_n_capt': 18,
            't_id': 19,
            't_text': 20,
            't_quote': 21,
            't_url': 22,
            't_date': 23,
            't_geopoint': 24,
            't_geopoly': 25,
            't_place': 26,
            't_lang': 27,
            're_t_id': 28,
            're_u_id': 29,
            'qu_t_id': 30,
            'qu_u_id': 31,
            'qu_n_qu': 32,
            'qu_n_re': 33,
            'qu_n_rt': 34,
            'qu_n_fav': 35,
            'rt_t_id': 36,
            'rt_t_id': 36,
            'rt_u_id': 37,
            'rt_n_qu': 38,
            'rt_n_re': 39,
            'rt_n_rt': 40,
            'rt_n_fav': 41,
            'u_profile': 42,
            'u_profile_img': 43,
            'u_list': 44,
            't_hashtags': 45,
            't_urls': 46,
            't_mentions': 47,
            't_media': 48
            }

    i = 0
    if isinstance(head,str):
        head = head.strip().split(delimit)
    if isinstance(head,list):
        col_dict = {}
        for l in head:
            col_dict[l.strip()] = i
            i += 1
            
    if isinstance(tc_in,int):
        for k, v in col_dict.items():
            if v == tc_in:
                return k
    elif isinstance(tc_in,str):
        return col_dict[tc_in]
    else:
        return col_dict


### cmdvars function
#
# Set default variables and look for additional command line input. 
# Output a dictionary of variables used in various other RITHM scripts.
#
###
def cmdvars(args=sys.argv):
    make_dir = False
    sub_dir = 0
    d = {}

    # Default input directory
    d['dir_in'] = './data/'

    # Default datestamps in filename-type format (int; YYYYMMDD)
    d['start'] = 20170101 # Default to 1/1/2017 
    d['end'] = 20301231 # Default to 12/31/2030

    # Default file extension and delimiter
    d['f_ext'] = '.tsv'
    d['delimiter'] = '\t'

    # Default output file stem
    d['f_stem'] = ''

    # Deafult to None for other values    
    for v in ['do_this', 'id', 'val', 'dir_out', 
              'dir_in_kws', 'dir_in_uid', 'dir_in_tid', 'dir_in_gid', 'dir_in_val',
              'f1', 'f2', 'f_kws', 'f_uid', 'f_tid', 'f_gid', 'f_val']:
        d[v] = None

    # Deafult to False for other values    
    for v in ['get_kws', 'get_uid', 'get_gid', 'get_tid', 'get_val']:
        d[v] = False

    # Default retweet handling
    d['rt_include'] = False
    d['rt_ignore'] = True
    d['rt_status'] = '_noRTs'

    #keywords = []

    if len(args) > 1: # If command line arguments were passed
        i = 0
        print(' '.join(args),'\n')
        for arg in args:

            # '-do' passes a generic string command to use later
            if arg.lower() in ['-dothis','-do']:
                d['do_this'] = str(args[i+1])

            # '-id' passes a generic string command to use later
            if arg.lower() in ['-id']:
                d['id'] = str(args[i+1])

            # '-val' passes a generic string command to use later
            if arg.lower() in ['-val']:
                d['val'] = str(args[i+1])

            # '-date' indicates start/end dates (req. 2 MMDDYYYY objects)
            if arg.lower() in ['-date','-dates']:
                d['start'] = int(args[i+1])
                d['end'] = int(args[i+2])

            # '-dir' indicates input directory (MUST include trailing slash)
            if arg.lower() in ['-dir','-in','-indir','-dirin']:
                d['dir_in'] = str(args[i+1])

            # '-out' indicates output directory (MUST include trailing slash)
            # '-mkout' will create that directory if it does not exist
            # dir_out starting with './' or '../' will make subdirectory relative to dir_in
            if arg.lower() in ['-out','-dirout','-outdir','-mkdir','-mkout']:
                d['dir_out'] = str(args[i+1])
                if arg.lower() in ['-mkdir', '-mkout']:
                    make_dir = True
                if d['dir_out'][0:2] == './' or d['dir_out'][0:3] == '../':
                    make_dir = True

            # '-file' or '-filein' indicates a primary file to read
            if arg.lower() in ['-file','-file1','-f','-f1','-filein','-infile']:
                d['f1'] = str(args[i+1])

            # '-file2' or '-fileout' indicates a secondary file to read or an output file
            if arg.lower() in ['-file2','-f2','-fileout','-outfile']:
                d['f2'] = str(args[i+1])

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

            # '-kwdir' indicates input directory for KWS files (MUST include trailing slash)
            if arg.lower() in ['-dirkws','-dirkw','-kwsdir','-kwdir','-kwd']:
                d['dir_in_kws'] = str(args[i+1])
                d['get_kws'] = True

            # '-kwfile' indicates specific KWS file
            # directory paths here override '-kwdir', and are relative to '-dir'
            if arg.lower() in ['-filekws','-filekw','-kwsfile','-kwfile','-kwf']:
                d['f_kws'] = str(args[i+1])
                d['get_kws'] = True

            # '-uidir' indicates input directory for UID files (MUST include trailing slash)
            if arg.lower() in ['-diruid','-dirui','-uiddir','-uidir','-uidd','-uid','-duid','-dui']:
                d['dir_in_uid'] = str(args[i+1])
                d['get_uid'] = True

            # '-uifile' indicates specific UID file
            # directory paths here override '-kwdir', and are relative to '-dir'
            if arg.lower() in ['-fileuid','-fileui','-uidfile','-uifile','-uidf','-uif','-fuid','-fui']:
                d['f_uid'] = str(args[i+1])
                d['get_uid'] = True

            # '-tidir' indicates input directory for TID files (MUST include trailing slash)
            if arg.lower() in ['-dirtid','-dirti','-tiddir','-tidir','-tidd','-tid','-dtid','-dti']:
                d['dir_in_tid'] = str(args[i+1])
                d['get_tid'] = True

            # '-tifile' indicates specific TID file
            # directory paths here override '-kwdir', and are relative to '-dir'
            if arg.lower() in ['-filetid','-fileti','-tidfile','-tifile','-tidf','-tif','-ftid','-fti']:
                d['f_tid'] = str(args[i+1])
                d['get_tid'] = True

            # '-gidir' indicates input directory for GID files (MUST include trailing slash)
            if arg.lower() in ['-dirgid','-dirgi','-giddir','-gidir','-gidd','-gid','-dgid','-dgi']:
                d['dir_in_gid'] = str(args[i+1])
                d['get_gid'] = True

            # '-gifile' indicates specific GID file
            # directory paths here override '-kwdir', and are relative to '-dir'
            if arg.lower() in ['-filegid','-filegi','-gidfile','-gifile','-gidf','-gif','-fgid','-fgi']:
                d['f_gid'] = str(args[i+1])
                d['get_gid'] = True

            # '-valdir' indicates input directory for VAL files (MUST include trailing slash)
            if arg.lower() in ['-dirval','-valdir','-dv','-vd']:
                d['dir_in_val'] = str(args[i+1])
                d['get_val'] = True

            # '-valfile' indicates specific VAL file
            # directory paths here override '-kwdir', and are relative to '-dir'
            if arg.lower() in ['-fileval','-valfile','-fv','-vf']:
                d['f_val'] = str(args[i+1])
                d['get_val'] = True

            # '-rt' indicates that RTs should be included
            if arg.lower() in ['-rt', '-rts']:
                d['rt_include'] = True
                d['rt_ignore'] = False
                d['rt_status'] = '_withRTs'

            i+=1


        # Resolve relative directory and file paths 
        d['dir_out'], null = dirfile_spec(d['dir_in'], d['dir_out'], make_dir=make_dir)
        if d['dir_out'] is None:
            d['dir_out'] = d['dir_in']
        null, d['f1'] = dirfile_spec(d['dir_in'], None, d['f1'])
        null, d['f2'] = dirfile_spec(d['dir_in'], None, d['f2'])
        d['dir_in_kws'], d['f_kws'] = dirfile_spec(d['dir_in'], d['dir_in_kws'], d['f_kws'])
        d['dir_in_uid'], d['f_uid'] = dirfile_spec(d['dir_in'], d['dir_in_uid'], d['f_uid'])
        d['dir_in_tid'], d['f_tid'] = dirfile_spec(d['dir_in'], d['dir_in_tid'], d['f_tid'])
        d['dir_in_gid'], d['f_gid'] = dirfile_spec(d['dir_in'], d['dir_in_gid'], d['f_gid'])
        d['dir_in_val'], d['f_val'] = dirfile_spec(d['dir_in'], d['dir_in_val'], d['f_val'])


    return d
"""
Here's example syntax for using cmdvars function in other RITHM scripts.

    cv = parselogic.cmdvars()

See __main__ for examples of importing specific variables into a script.

"""


### filelist function
#
# Returns a list of files matching certain criteria within a given directory. 
#    
#    "f_ext" parameter: 
#       What is the file extension to search for? If not TSV or CSV, all 
#       matching files will be included by default.
#    
#    "tsv_type" parameter: 
#       "raw" handles daily tweet files (must begin as YYYYMMDD format)
#
###
def filelist(dir_in, f_ext='.tsv', tsv_type='raw', start=0, end=99999999, silent=False, quiet=True):
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
                    # For handling other TSV file types (e.g., subsamples)
                    if not silent: print(f+' included')
                    files_list.append(f)

            else:
                if not silent: print(f+' included')
                files_list.append(f)

    return sorted(files_list)



### othlist function
#
# Returns de-duplicated list of values from other file types in a dir. 
#   Each line is treated as a separate keyword string. 
#   Blank lines and hashed-out lines are ignored. 
#
###
def othlist(dir_in_oth, f_oth=None, f_ext='.nul', prefix=None, silent=False):
    oth_list = []
    if f_oth:
        if not silent: print('\n----- using '+f_oth)
        with open(dir_in_oth+f_oth, 'r') as uf:
            for l in uf: #for line in file
                l = l.strip()
                if len(l)>0 and l[0] != '#':
                    if prefix:
                        if l[0] != prefix:
                            l = prefix+l
                    oth_list.append(l)
                else:
                    pass
    else:
        oth_files = filelist(dir_in_oth, f_ext=f_ext, silent=silent)
        for f in oth_files:
            with open(dir_in_oth+f, 'r') as uf:
                for l in uf: #for line in file
                    l = l.strip()
                    if len(l)>0 and l[0] != '#':
                        if prefix:
                            if l[0] != prefix:
                                l = prefix+l
                        oth_list.append(l)
                    else:
                        pass
    if not silent:
        if f_ext == '.uid':
            print('\nUser ID filters:')
            print(len(list(set(oth_list))), 'users to identify')
            return sorted(list(set(oth_list)))
        if f_ext == '.tid':
            print('\nTweet ID filters:')
            print(len(list(set(oth_list))), 'tweets to identify')
            return sorted(list(set(oth_list)))
        if f_ext == '.gid':
            print('\nGroup ID filters:')
            print(len(list(set(oth_list))), 'groups to identify')
            return sorted(list(set(oth_list)))
        if f_ext == '.val':
            print('\nValue filters:')
            print(sorted(list(set(oth_list))))
            print(len(list(set(oth_list))), 'values to identify')
            return oth_list
        if f_ext == '.kws':
            print('\nKeyword filters:')
            print(sorted(list(set(oth_list))))
            return sorted(list(set(oth_list)))



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


### dirfile_spec function
#
# Resolves relative directory and file inputs and 
# returns expected output format for other functions
#
###
def dirfile_spec(dir_in, dir_spec=None, f_spec=None, make_dir=False):
    if dir_spec is None and f_spec is None:
        return None,None
        
    if dir_spec is None:
        dir_spec = dir_in
    elif dir_spec[0:2] == './':
        dir_spec = dir_in+dir_spec[2:]
    elif dir_spec[0:3] == '../':
        dir_back = ('/').join(dir_in.split('/')[:-2]+[''])
        dir_spec = dir_back+dir_spec[3:]

    if make_dir:
        mkdir(dir_spec)

    if f_spec is not None:
        if f_spec[0:2] == './':
            f_spec = dir_in+f_spec[2:]
            dir_spec = ''
        elif f_spec[0:3] == '../':
            dir_back = ('/').join(dir_in.split('/')[:-2]+[''])
            f_spec = dir_back+f_spec[3:]
            dir_spec = ''
        elif '/' in f_spec:
            dir_spec = ''
            
    return dir_spec, f_spec

### emojify function
#
# Documentation not provided.
# This is used in reformat function.
#
###
def emojify(text, emojis):
    if '\\u' in text.lower():
        text = text.replace('\\U' , '\\u')
        text = text.replace('\\' , ' \\')
        words = text.split(' ')

        for word in words:
            if '\\u' in word:
                word = word.strip()
                if word in emojis.keys():
                    words[words.index(word)] = emojis[word].strip()
                elif word[0:10] in emojis:
                    word_1 = word[10:len(word)]
                    words[words.index(word)] = emojis[word[0:10]].strip() + ' ' + word_1
                elif word[0:6] in emojis:
                    word_1 = word[6:len(word)]
                    words[words.index(word)] = emojis[word[0:6]].strip() + ' ' + word_1
                elif word[0:4] in emojis:
                    word_1 = word[4:len(word)]
                    words[words.index(word)] = emojis[word[0:4]].strip() + ' ' + word_1
        text = ' '.join(words)
        while '  ' in text:
            text = text.replace('  ',' ')
        return text
    return text
                    
"""
# This older version was replaced on 2020-09-21
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


# This is a crude, hierarchical way to organize modes for reformat function
modes = {'tsv':'1.0',
         'csv':'1.5',
         'hum':'3.5',
         'kws':'4.5'}

### reformat function
# 
# This reformats text so that it is keyword searchable or machine/human readable
#   "mode" argument options currently include: 
#     1.0 'tsv' = Only replace tabs, and hard returns (TSV compatability) 
#                 This is currently the default for output. 
#     1.5 'csv' = Replace commas, tabs, and hard returns (CSV compatability) 
#     3.5 'hum' = Format for maximum human readability (useful for annotation)
#     4.5 'kws' = Format for keyword matching (default for search procedures)
#
#   "lcase" argument is optional. All text will be reduced to lowercase. 
#   "ht_include" argument is optional. Includes hashtags w/ basic keywords. 
#   "emoji" argument contains the emoji dict. Will be empty if filepath invalid. 
###
def reformat(text, emojis=None, emojifile=None,
             mode=1.0, modes=modes, 
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

    # To-do: Read dictionary from emojifile if present
    if emojifile:
        pass

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
        test = test.replace('  ' , ' ') # Make multuple spaces into single spaces 


    
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


### dt_format function
# 
# This converts between several datetime formats
#
###
def dt_format(date_in=None, date_type='detect',output='standard',incl_time=True):
    date_out = None
    if date_in is None:
        date_in = str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
        date_type = 'yyyymmddhhmmss'
    
    if date_type == 'detect':
        if type(date_in) is int:
            date_in = str(date_in)

        if type(date_in) is datetime.datetime:
            date_type = 'datetime'
            #output = 'human'
        elif '-' in date_in: 
            date_type = 'human'
        elif len(date_in) == 8: 
            date_type = 'yyyymmdd'
            incl_time = False
        elif len(date_in) == 14:
            date_type = 'yyyymmddhhmmss'
        else: 
            date_type = 'twitter'

    try:
        if date_type in ['human','standard']:
            dt = date_in.split(' ')
            dl = dt[0].split('-')
            year = int(dl[0])
            month = int(dl[1])
            day = int(dl[2])
            tl = dt[1].split(':')
            hour = int(tl[0])
            minute = int(tl[1])
            second = int(tl[2])
    
        if date_type in ['filedate','yyyymmdd','yyyymmddhhmmss']:
            d = date_in
            year = int(d[0:4])
            month = int(d[4:6])
            day = int(d[6:8])
    
        if date_type == 'yyyymmddhhmmss':
            hour = int(d[8:10])
            minute = int(d[10:12])
            second = int(d[12:14])
    
        if date_type in ['twitter']:
            months={'Jan':'01','Feb':'02','Mar':'03','Apr':'04',
                    'May':'05','Jun':'06','Jul':'07','Aug':'08',
                    'Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
            dl = date_in.split(' ')
            year = int(dl[-1])
            month = int(months[dl[1]])
            day = int(dl[2])
            tl = dl[3].split(':')
            hour = int(tl[0])
            minute = int(tl[1])
            second = int(tl[2])
    
        if date_type in ['datetime']:
            year = date_in.year
            month = date_in.month
            day = date_in.day
            hour = date_in.hour
            minute = date_in.minute
            second = date_in.second
    
        if incl_time:
            date_out = datetime.datetime(year, month, day, hour, minute, second)
        else:
            date_out = datetime.datetime(year, month, day)
    
        if output in ['human', 'standard']:
            if incl_time:
                date_out = str(date_out.strftime('%Y-%m-%d %H:%M:%S'))
            else: 
                date_out = str(date_out.strftime('%Y-%m-%d'))
        elif output in ['filedate', 'yyyymmdd']:
            date_out = str(date_out.strftime('%Y%m%d'))
        elif output  == 'yyyymmddhhmmss':
            date_out = str(date_out.strftime('%Y%m%d'))

    except:
        print('\nThe dt_format function failed to parse datetime as input type:',date_type)
        print('Input data was: ',date_in)
        print('  Converting to:',output)
        print('Output data was:',date_out,'\n')

    return date_out


### criteria_match function
# 
# l_list is a list of data to review for matches
# cols is a dictionary keys and associated data column #s
# vals is a list of value parameters to match with 
#
###
def criteria_match(l_list=[], cols={}, vals=[], returnparams=False):
    first = True
    v_and = False
    matched_val = False
    params = []
    for v in vals:
        v = re.sub(' ','',v)
        if '&' in v:
            v = re.sub('&','',v)
            v_and = True
            
        if '>=' in v:
            v = v.split('>=')
            if returnparams:
                params.append(v)
            else:
                if float(l_list[cols[v[0]]]) >= float(v[1].strip()):
                    if first:
                        first = False
                        matched_val = True
                    elif v_and and matched_val:
                        matched_val = True
                    else:
                        matched_val = False
                else:
                    matched_val = False
        elif '>' in v:
            v = v.split('>')
            if returnparams:
                params.append(v)
            else:
                if float(l_list[cols[v[0]]]) > float(v[1].strip()):
                    if first:
                        first = False
                        matched_val = True
                    elif v_and and matched_val:
                        matched_val = True
                    else:
                        matched_val = False
                else:
                    matched_val = False
        elif '<=' in v:
            v = v.split('<=')
            if returnparams:
                params.append(v)
            else:
                if float(l_list[cols[v[0]]]) <= float(v[1].strip()):
                    if first:
                        first = False
                        matched_val = True
                    elif v_and and matched_val:
                        matched_val = True
                    else:
                        matched_val = False
                else:
                    matched_val = False
        elif '<' in v:
            v = v.split('<')
            if returnparams:
                params.append(v)
            else:
                if float(l_list[cols[v[0]]]) < float(v[1].strip()):
                    if first:
                        first = False
                        matched_val = True
                    elif v_and and matched_val:
                        matched_val = True
                    else:
                        matched_val = False
                else:
                    matched_val = False
        elif '==' in v or '=' in v:
            v = re.sub('==','=',v)
            v = v.split('=')
            if returnparams:
                params.append(v)
            else:
                try:
                    if float(l_list[cols[v[0]]]) == float(v[1].strip()):
                        if first:
                            first = False
                            matched_val = True
                        elif v_and and matched_val:
                            matched_val = True
                        else:
                            matched_val = False
                    else:
                        matched_val = False
                except:
                    if str(l_list[cols[v[0]]]) == str(v[1].strip()):
                        if first:
                            first = False
                            matched_val = True
                        elif v_and and matched_val:
                            matched_val = True
                        else:
                            matched_val = False
                    else:
                        matched_val = False
        else:
            matched_val = False
            
    if returnparams:
        return params
    else:
        return matched_val




###############################################################################


### OTHER FUNCTIONS
# 
# THESE ARE EITHER EXPERIMENTAL OR DEPRECATED
#
###

### kwslist function
#
# DEPRECATED (use newer othlist function)
#
###
def kwslist(dir_in_kws, f_kws=None, f_ext='.kws', silent=False):
    return othlist(dir_in_oth=dir_in_kws, f_oth=f_kws, f_ext=f_ext, silent=silent)


### ts function 
#
# DEPRECATED (use newer dt_format function)
#
###
def ts(stamp=None, reform=None):
    if reform is False:
        output = 'yyyymmddhhmmss'
    else:
        output = 'standard'
    date_out = dt_format(date_in=stamp, date_type='detect',output=output,incl_time=True) 
    return date_out


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



###############################################################################


### COMMAND LINE PROCESSES
# 
# OTHER STUFF THAT MIGHT NOT WARRANT MAKING SEPARATE SCRIPTS
#
###
        
if __name__ == '__main__':
    cv = cmdvars()
    start = cv['start']
    end = cv['end']
    dir_in = cv['dir_in']
    dir_in_kws = cv['dir_in_kws']
    dir_in_uid = cv['dir_in_uid']
    dir_in_tid = cv['dir_in_tid']
    dir_in_gid = cv['dir_in_gid']
    dir_in_val = cv['dir_in_val']
    dir_out = cv['dir_out']
    f1 = cv['f1']
    f2 = cv['f2']
    f_kws = cv['f_kws']
    f_uid = cv['f_uid']
    f_tid = cv['f_tid']
    f_gid = cv['f_gid']
    f_val = cv['f_val']
    f_ext = cv['f_ext']
    delimiter = cv['delimiter']
    rt_include = cv['rt_include']
    rt_ignore = cv['rt_ignore']
    rt_status = cv['rt_status']
    f_stem = cv['f_stem']
    get_uid = cv['get_uid']
    get_tid = cv['get_tid']
    get_gid = cv['get_gid']
    get_kws = cv['get_kws']
    get_val = cv['get_val']
    do_this = cv['do_this']
    inp_id = cv['id']
    inp_val = cv['val']
    
    # Get keywords
    if get_kws:
        keywords = kwslist(dir_in_kws, f_kws)

    # Get UIDs
    if get_uid:
        uids = othlist(dir_in_uid, f_uid, f_ext='.uid', prefix='\'')

    # Get TIDs
    if get_tid:
        tids = othlist(dir_in_tid, f_tid, f_ext='.tid', prefix='\'')

    # Get GIDs
    if get_gid:
        gids = othlist(dir_in_gid, f_gid, f_ext='.gid')

    # Get values
    if get_val:
        vals = othlist(dir_in_val, f_val, f_ext='.val')



    ### -do mkgroups
    # 
    # This is to extract u_id values from file containing a grouping variable
    # Output is a valid UID file format w/ GID in the file name 
    #
    #  -id (+1 argument) Column name where the u_id is (case sensitive)
    #  -val (+1 argument) Logical argument including g_id column name (case sensitive)
    #       e.g.,  g_id_column_name = 123456789
    #  OR -valfile (+1 argument) File containing val parameters on separate lines
    ###
    if do_this in ['mkgroups', 'mkgroup']:
        if inp_val:
            vals = [inp_val]
        for val_i in vals:
            inp_val = val_i
            with open(dir_in+f1,'r') as f_in:
                [col_name, group_id] = criteria_match(vals=[val_i], returnparams=True)[0]
                #val = criteria_match(vals=[val_i], returnparams=True)[0]
                #col_name = val[0]
                #group_id = str(val[1])
                ids = []
                li = 0
                for l in f_in:
                    if li == 0:
                        head = l
                        cols = t_col(head=head, delimit=delimiter)
                        t_id = t_col(inp_id, head, delimit=delimiter)
                    else:
                        l_list = l.strip().split(delimiter)
                        if criteria_match(l_list=l_list, cols=cols, vals=[inp_val]):
                            ids.append(l_list[t_id]) 
                    li += 1
            print('\nFile:',f1)
            print('Matching:',inp_val)
            print(len(ids),'users identified')
            o_file = dir_out+f_stem+'group_'+group_id+'.uid'
            print('Saving to:',o_file,'\n')
            with open(o_file,'w+') as f_out:
                for u_id in ids:
                    f_out.write(str(u_id)+'\n') 


    ### -do hashtags
    # To-do: Hashtag frequency counter 
    ###
    if do_this in ['hashtags', 'hashtag']:
        pass
