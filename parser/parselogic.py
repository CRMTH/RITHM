# -*- coding: utf-8 -*-
"""
Created on Tue May 29 20:18:09 2018
@author: colditzjb

"""
import os, datetime, re


### ts function
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


### mkdir function
#
# A scrappy way to create a new directory, when needed. Use this function
# on a directory before trying to write out new files to it. 
#
#   "dirs" argument can handle a string or list of strings that correspond 
#       to one or more directories to search for and create if not there.
#       This argument is REQUIRED and strings must end with a "/"
#
#   "base" argument is an optional parent directory to work from.
#
###
def mkdir(dirs, base=''):
    def makeit(base, dirs):
        if dirs[-1] != '/':
            print(str(dirs)+' is an invalid directory name!')
        elif not os.path.exists(base+dirs):
            os.makedirs(base+dirs)
            
    if type(dirs) is str:
        makeit(base, dirs)
    elif type(dirs) is list:
        for d in dirs:
            makeit(base, d)
    else:
        return None

def emojify(text, emojis):
    if '\\u' in text.lower():
        text = text.replace('\\\\U' , '\\\\u')
        text = text.replace('\\\\u' , ' \\\\u')
        words = text.split(' ')
        for word in words:
            if '\\u' in word:
                if word in emojis.keys():
                    words[words.index(word)] = emojis[word]
                elif word[0:11] in emojis:
                    word_1 = word[11:len(word)]
                    words[words.index(word)] = emojis[word[0:11]] + ' ' + word_1
                elif word[0:7] in emojis:
                    word_1 = word[7:len(word)]
                    words[words.index(word)] = emojis[word[0:7]] + ' ' + word_1
        return ' '.join(words)
    return text


# This is a crude, hierarchical way to organize modes
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
#   "ht_include" argument is optional. Hashtags will be included w/ basic keywords. 
#   "emoji" argument contains the emoji dictionary. Will be empty if filepath is invalid. 
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

    text = text.replace('\\\\', '\\') #Fixing backslach escapes
    return text



# This performs matching on text, using boolean test phrases
def match(test, text):
    ### Term syntax includes '*' as wildcard and '!' as NOT operator
    # wildcards do not respect space delimitations (full-text inclusive)
    # "!" operator may have undesirable Boolean behavior: use with caution!

    test = test.replace('! ' , '!') # Remove space after "!" for processing
    
    test = test.replace('#' , '# ') # Reformat to catch hashtags as keywords...
    while '  ' in test:
        text = test.replace('  ' , ' ')


    
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

