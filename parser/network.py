

import parselogic, sys
from parselogic import t_col

def u_netdict(f_in, dir_in=None, u_dict=None, delimit='\t', keywords=[]):
    if not u_dict:
        u_dict = {}
    if not dir_in: 
        indir = ''

    included = 0
    excluded = 0
    
    def kwmatch(lc, keywords=keywords):
        text = ' '+lc[t_col('t_text')]+' '+lc[t_col('t_quote')]+' '
        text = parselogic.reformat(text, emojis=None, mode=4.5) #format text for matching 
        for k in keywords: #for each keyword
            matched = parselogic.match(k, text) #test it against the tweet
            if matched:
                return True
        return False
    
    l_i = 0
    with open (dir_in+f_in,'r') as f:
        for l in f:
            if l_i > 0: # ignore header
                lc = l.split(delimit)

                if len(keywords)==0:
                    include = True
                else:
                    include = kwmatch(lc)

                if include:
                    included += 1
                    u_id = lc[t_col('u_id')]
                    if u_id not in u_dict:
                        u_dict[u_id] = {
                                        'counts':{'rt':0, 're':0, 'qu':0},
                                        'ties':{},
                                        'meta':{}
                                       }
                    
                    u_dict[u_id]['meta']['u_handle']=lc[t_col('u_handle')]
                    u_dict[u_id]['meta']['u_tweets']=lc[t_col('u_tweets')]
                    u_dict[u_id]['meta']['u_fo_out']=lc[t_col('u_fo_out')]
                    u_dict[u_id]['meta']['u_fo_in']=lc[t_col('u_fo_in')]
                    u_dict[u_id]['meta']['u_create']=lc[t_col('u_create')]
                    
                    # Populate RT ties
                    rt_u_id = lc[t_col('rt_u_id')]
                    rt_t_id = lc[t_col('rt_t_id')]
                    if len(rt_u_id) > 0:
                        u_dict[u_id]['counts']['rt'] += 1
                        if rt_u_id not in u_dict[u_id]['ties']:
                            u_dict[u_id]['ties'][rt_u_id] = {}
                            u_dict[u_id]['ties'][rt_u_id]['rt'] = []
                            u_dict[u_id]['ties'][rt_u_id]['re'] = []
                            u_dict[u_id]['ties'][rt_u_id]['qu'] = []
                        u_dict[u_id]['ties'][rt_u_id]['rt'].append(rt_t_id)
                
                    # Populate reply ties
                    re_u_id = lc[t_col('re_u_id')]
                    re_t_id = lc[t_col('re_t_id')]
                    if len(re_u_id) > 0:
                        u_dict[u_id]['counts']['re'] += 1
                        if re_u_id not in u_dict[u_id]['ties']:
                            u_dict[u_id]['ties'][re_u_id] = {}
                            u_dict[u_id]['ties'][re_u_id]['rt'] = []
                            u_dict[u_id]['ties'][re_u_id]['re'] = []
                            u_dict[u_id]['ties'][re_u_id]['qu'] = []
                        u_dict[u_id]['ties'][re_u_id]['re'].append(re_t_id)
                
                    # Populate quote ties
                    qu_u_id = lc[t_col('qu_u_id')]
                    qu_t_id = lc[t_col('qu_t_id')]
                    if len(qu_u_id) > 0:
                        u_dict[u_id]['counts']['qu'] += 1
                        if qu_u_id not in u_dict[u_id]['ties']:
                            u_dict[u_id]['ties'][qu_u_id] = {}
                            u_dict[u_id]['ties'][qu_u_id]['rt'] = []
                            u_dict[u_id]['ties'][qu_u_id]['re'] = []
                            u_dict[u_id]['ties'][qu_u_id]['qu'] = []
                        u_dict[u_id]['ties'][qu_u_id]['qu'].append(qu_t_id)
                else:
                    excluded += 1
            l_i += 1
    return {'u_dict':u_dict, 'included':included, 'excluded':excluded}
    

def edges(u_dict, tie_rt=True, tie_re=False, tie_qu=False):
    e_list= []
    e_dict = {'rt':{},
              're':{},
              'qu':{}
             }

    for u1, d1 in u_dict.items():
        include = False
            
        if d1['counts']['rt'] > 0 and tie_rt:
            include = True
            e_dict['rt'][u1] = {}

        if d1['counts']['re'] > 0 and tie_re:
            include = True
            e_dict['re'][u1] = {}

        if d1['counts']['qu'] > 0 and tie_qu:
            include = True
            e_dict['qu'][u1] = {}

        if include:
            for u2, d2 in d1['ties'].items():
                if tie_rt:
                    try:
                        t_rt = len(d2['rt'])
                        if t_rt > 0:
                            e_dict['rt'][u1][u2] = t_rt
                    except: 
                        pass
                
                if tie_re:
                    try:
                        t_re = len(d2['re'])
                        if t_re > 0:
                            e_dict['re'][u1][u2] = t_re
                    except: 
                        pass

                if tie_qu:
                    try:
                        t_qu = len(d2['qu'])
                        if t_qu > 0:
                            e_dict['qu'][u1][u2] = t_qu
                    except: 
                        pass
            
    return e_dict
        



if __name__ == '__main__':

    # Default variables
    tie_rt = True
    tie_re = False
    tie_qu = False
    halt = False
    keywords = []


    cv = parselogic.cmdvars()
    start = cv['start']
    end = cv['end']
    dir_in = cv['dir_in']
    dir_out = cv['dir_out']
    f1 = cv['f1']
    f2 = cv['f2']
    delimiter = cv['delimiter']
    f_ext = cv['f_ext']
    f_stem = cv['f_stem']
    dir_in_kws = cv['dir_in_kws']
    f_kws = cv['f_kws']


    # Unique command line arguments
    i = 0
    try:
        for arg in sys.argv:
            if arg.lower() in ['-nort','-norts','-noretweet','-noretweets']: # Do not map RT's 
                tie_rt = False
            if arg.lower() in ['-rt','-retweet','-retweets']: # Map RT's (default) 
                tie_rt = True
            if arg.lower() in ['-re','-reply','-replies','-response','-responses']: # Map replies 
                tie_re = True
            if arg.lower() in ['-qu','-quote','-quotes']: # Map quotes
                tie_qu = True
            if arg.lower() in ['-net','-netvars','-network','-networkvars']: # Network vars
                if int(sys.argv[i+1]) > 0:
                    tie_rt = True
                if int(sys.argv[i+2]) > 0:
                    tie_re = True
                if int(sys.argv[i+3]) > 0:
                    tie_qu = True
            if arg.lower() in ['-filekws','-filekw','-kwsfile','-kwfile','-kwf',
                               '-dirkws','-dirkw','-kwsdir','-kwdir','-kwd']:
                keywords = parselogic.kwslist(dir_in_kws, f_kws)

            i = i+1
    
    except:
        print ('ERROR: Command line arguments failed to parse.')
        halt = True


    if not halt:
        fl = parselogic.filelist(dir_in, start=start, end=end)
    
        print('\nCreating user dictionary.\n')
        f_i = 0
        for f in fl:
            if f_i == 0:
                u_dict = u_netdict(f, dir_in, keywords=keywords)
            else:
                u_dict = u_netdict(f, dir_in, u_dict['u_dict'], keywords=keywords)
            f_i += 1
            
        if len(keywords) > 0:
            print('----- Keyword matching:')
            print('Tweets included: '+str(u_dict['included']))
            print('Tweets excluded: '+str(u_dict['excluded'])+'\n')
        print('Users included:  '+str(len(u_dict['u_dict'])))


        print('\n----- Calculating edges and writing out...')
        print('Retweets: '+str(tie_rt))
        print('Replies:  '+str(tie_re))
        print('Quotes:   '+str(tie_qu))
        
        e_dict = edges(u_dict['u_dict'], tie_rt=tie_rt, tie_re=tie_re, tie_qu=tie_qu)


        # TO-DO: output user metadata in node file 
        nodehead = 'user1\n'
        def nodewriter(datatype, f_ext=f_ext, f_stem=f_stem, dir_out=dir_out, head=nodehead, delimiter=delimiter):
            outfile = datatype+'_nodes'+f_ext
            if head:
                with open(dir_out+f_stem+outfile, 'w+') as ofile:
                    ofile.write(head)
            with open(dir_out+f_stem+outfile, 'a+') as ofile:
                for u1,d1 in e_dict[datatype].items():
                    line = u1 #delimiter.join([u1])
                    ofile.write(line+'\n')
        
        edgehead = 'user1'+delimiter+'user2'+delimiter+'ties\n'
        def edgewriter(datatype, f_ext=f_ext, f_stem=f_stem, dir_out=dir_out, head=edgehead, delimiter=delimiter):
            outfile = datatype+'_edges'+f_ext
            if head:
                with open(dir_out+f_stem+outfile, 'w+') as ofile:
                    ofile.write(head)
            with open(dir_out+f_stem+outfile, 'a+') as ofile:
                for u1,d1 in e_dict[datatype].items():
                    for u2,d2 in d1.items():
                        line = delimiter.join([u1,u2,str(d2)])
                        ofile.write(line+'\n')


        if tie_rt:
            nodewriter('rt')
            edgewriter('rt')
        if tie_re:
            nodewriter('re')
            edgewriter('re')
        if tie_qu:
            nodewriter('qu')
            edgewriter('qu')

        print('\nJob complete!\n\n')
