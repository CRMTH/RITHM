# -*- coding: utf-8 -*-
"""
Created on Tue May 29 20:18:09 2018
@author: colditzjb

Description: Several of these functions are embedded in different 
places within the parsing infrastructure. This package is a work 
in progress, to eventually take the place of the various functions 
that are located within other places, for example:

  decode.parseText(self, data)
  decode.checkForKWs(self, kwtext)
  freq_out.tokens(text)
  freq_out.LogicMatch(kw, text, matched=False)
  freq_out.TermMatch(kw, text, matched=False)
  subsample.subsample() --> kw_redux functionality  

"""
# Regex is required
import re 


### REFORMAT FUNCTION
# 
# This reformats text so that it is keyword searchable or machine/human readable
#   "mode" variable options include: 
#     0 'min' = Only replace commas, tabs, and returns (for CSV compatability) 
#     1 'kws' = Format for keyword matching (default for search procedures)
#     2 'mac' = Format for machine processing (basic cleaning and tokenizing)
#     3 'hum' = Format for maximum human readability (useful for coding)
###
def reformat(text, mode='kws', lcase=True, 
             emoji='emojilist5.csv'):
    
    # Lower case
    if lcase: text = text.lower()
    
    # Reformat common Unicode punctuation
    text = text.replace(u'\u2026' , '...')
    text = text.replace(u'\u2122' , '...')
    text = text.replace(u'\u2018' , "'")
    text = text.replace(u'\u2019' , "'")
    text = text.replace(u'\u201c' , '"')
    text = text.replace(u'\u201d' , '"')
    text = text.replace(u'\u200d' , '')
    text = text.replace(u'\u2014' , ' - ')
    text = text.replace('\\u' , ' \\u') # CHECK THIS

    ### WE SHOULD UPDATE THE REST AS text.replace() IF FASTER?
    # Format common punctuation and buffer with spaces
    text = re.sub('`', "'", text)
    text = re.sub('&amp;', ' & ', text)
    text = re.sub('&gt;', ' > ', text)
    text = re.sub('&lt;', ' < ', text)
    text = re.sub(r'\(', ' ( ', text)
    text = re.sub(r'\)', ' ) ', text)
    text = re.sub(r'\[', ' [ ', text)
    text = re.sub(r'\]', ' ] ', text)
    text = re.sub(r'\"', ' " ', text)
    text = re.sub(r'\*', ' * ', text)
    text = re.sub(r'\-', ' - ', text)
    text = re.sub(r'\.', ' . ', text)
    text = re.sub(r'\!', ' ! ', text)
    text = re.sub(r'\?', ' ? ', text)
    text = re.sub(r'\:', ' : ', text)
    text = re.sub(r'\;', ' ; ', text)
    
    # Commas/returns/tabs get recoded because CSV output
    text = re.sub(r'\,0', '0', text) #Comma in common number
    text = re.sub(r'\,', ' - ', text)
    text = re.sub(r'\n', ' --- ', text)
    text = re.sub(r'\r', ' --- ', text)
    text = re.sub(r'\t', ' ', text)

    # Repair hyperlinks
    text = re.sub(r' \: \/\/', '://', text)
    text = re.sub(r't . co', 't.co', text)

    # Repair quote on rt
    #text = re.sub(r'\"rt', 'rt', text)
    

    # Format punctuation oddities
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

    # Add whitespace for matching
    text = ' '+text+' '

    return text



# This performs matching on text, using boolean test phrases
def match(test, text):

    ### Term syntax includes '*' as wildcard and '!' as NOT operator
    # wildcards do not respect space delimitations (full-text inclusive)
    # NOT "!" operator must be prefixed onto the keyword (no spaces) 
    # NOT "!" operator may have unpredictable behavior - use with caution!  
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
    # parentheses are not currently implemented - don't use them!
    # this currently defaults to basic LogicMatch() functionality
    def ParentMatch(test, text):
        return LogicMatch(test, text)
        
    ### Returns boolean for a logical keyword test within a given text
    return ParentMatch(test, text)

"""
### UNIT TESTING

texts = ['THIS is a Generic tweet about vAPing...',
         'this is a generiC twEEt that mentions JUUL',
         'when i vape , i prefer juul\u2026',
         'i am the based vape god , so i juul']

tests = ['vaping & juul',
         'vape | vaping & juul',
         'generic | based & vaping | juul',
         ' vap*',
         '...']
         
for test in tests:
    print(test)
    for text in texts:
        print('  '+text+' - '+str(match(test, reform(text))))
"""
