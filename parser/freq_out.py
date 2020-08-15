# -*- coding: utf-8 -*-
"""
Created on 2018-04-12

@author: ColditzJB
"""

import parselogic, os, sys


def DataDict(dir_in, start=None, end=None,
             rt_ignore=True, rt_col=36, 
             loc_check=False, loc_col=11,
             text_col=20, quote_col=21, 
             f_ext='.tsv', delimiter='\t',
             keywords=[]):
    date_list = []
    datafiles = parselogic.filelist(dir_in, f_ext=f_ext, start=start, end=end)
    for fi in datafiles:
        date_list.append(fi[:8])

    data_dict = {}
    for date in list(set(date_list)):
       data_dict[date] = {}
       data_dict[date]['_tweets'] = 0
       data_dict[date]['_tweets_inloc'] = 0 #loc_check functionality not used
       data_dict[date]['_rts_ignored'] = 0
       data_dict[date]['_hits'] = 0
       data_dict[date]['_hits_inloc'] = 0 #loc_check functionality not used
       data_dict[date]['_error'] = 0 #_error functionality not used
       for k in keywords:
           data_dict[date][k] = 0
           
    for f in datafiles: 
        with open(dir_in+f, 'r') as o:
            i=0
            for l in o: #for each line in the open file
                i+=1
                try:text = l.split(delimiter)[text_col]+' '+l.split(delimiter)[quote_col] #get text from tweet and quote fields
                except Exception as e: 
                    print('error: '+str(e))
                    print('file:  '+f)
                    print('line:  '+str(i))
                    print('data:  '+str(l))
                    
                text = parselogic.reformat(text, emojis=None, mode=4.5) #format text for matching 
                hit = False
                if l.split(delimiter)[text_col].strip() in ['text', 't_text']: #ignore header row
                    pass
                else:
                    if rt_ignore and not len(l.split(delimiter)[rt_col].strip()) > 0:
                        for k in keywords: #for each line of keyword(s)
                            matched = parselogic.match(k, text) #test it against the tweet
                            if matched:
                                data_dict[f[:8]][k] += 1
                                hit = True
                    elif rt_ignore:
                        data_dict[f[:8]]['_rts_ignored'] += 1
                    else:
                        for k in keywords: #for each line of keyword(s)
                            matched = parselogic.match(k, text) #test it against the tweet
                            if matched:
                                data_dict[f[:8]][k] += 1
                                hit = True
                        
                    if hit: 
                        data_dict[f[:8]]['_hits'] += 1
                        #if loc_check: data_dict[f[:8]]['_hits_inloc'] += parselogic.locmatch(l.split(delimiter)[loc_col]) #loc_check functionality not used
                        
                    data_dict[f[:8]]['_tweets'] += 1
                    #if loc_check: data_dict[f[:8]]['_tweets_inloc'] += parselogic.locmatch(l.split(delimiter)[loc_col]) #loc_check functionality not used

    return data_dict


if __name__ == '__main__':

    # Get variable defaults and command line arguments
    cv = parselogic.cmdvars()
    start = cv['start']
    end = cv['end']
    dir_in = cv['dir_in']
    dir_in_kws = cv['dir_in_kws']
    f_kws = cv['f_kws']
    dir_out = cv['dir_out']
    f_stem = cv['f_stem']
    f_ext = cv['f_ext']
    delimiter = cv['delimiter']
    rt_ignore = cv['rt_ignore']
    rt_status = cv['rt_status']

    # Get keywords and data dictionary
    keywords = parselogic.kwslist(dir_in_kws, f_kws)
    dw = DataDict(dir_in, start, end, rt_ignore=rt_ignore, keywords=keywords)

    with open(dir_out+f_stem+'frequencies'+rt_status+f_ext, 'w+') as f:
        #head = delimiter.join(['date','_tweets','_tweets_inloc','_rts_ignored','_hits','_hits_inloc','_error'])+delimiter #_error and loc_check functionality not used
        head = delimiter.join(['date','_tweets','_rts_ignored','_hits'])+delimiter
        kws_list_formatted = str(keywords).replace(',',delimiter)[1:-1]
        f.write(head+kws_list_formatted+'\n') #header
        for day in sorted(dw.keys()):
            f.write(str(day)+delimiter) 
            f.write(str(dw[day]['_tweets'])+delimiter)
            #f.write(str(dw[day]['_tweets_inloc'])+delimiter) #loc_check functionality not used
            f.write(str(dw[day]['_rts_ignored'])+delimiter)
            f.write(str(dw[day]['_hits'])+delimiter)
            #f.write(str(dw[day]['_hits_inloc'])+delimiter) #loc_check functionality not used
            #f.write(str(dw[day]['_error'])+delimiter) #_error functionality not used
            for kw in keywords:
                f.write(str(dw[day][kw])+delimiter)
            f.write('\n')
    f.close()
    print('\nProcess complete!\n\n')
    #print(dw)