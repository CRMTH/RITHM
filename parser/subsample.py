# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 19:11:08 2017
@author: colditzjb

A command line tool for sub-sampling parsed RITHM data.

"""
import sys
import parselogic


class subsample(object):
    """
    The "subsample" class is used to systematically subsample RITHM output
    as TSV files from a defined system directory.
    
    . 
    """
    ##### If column numbers change, "*_incol" vars need updating - this dependency 
    ##### should be fixed so that the process is aware of standard variable names
    ##### and calculates column numbers accordingly. 
    def __init__(self, data=None, dir_in='', datafiles=[],
                 header=True, combine=True,
                 kw_redux=[], kw_incol=20, quote_incol=21, 
                 rt_ignore=True, rt_incol=36, 
                 geo_only=False, geo_incol=12,
                 uid_redux=[], uid_incol=0):  
        self.data = data
        self.kw_incol = kw_incol
        self.uid_incol = uid_incol
        self.returns = {}                    
        self.delimit = '\t'


        # If no data was passed, then read-in data 
        if not data:
            datadict = {}
            datalines = []

            read_tweet = False    
            i_total = 0
            i_rt_total = 0
            i_kw = 0
            i_rt_kw = 0
            i_uid = 0
            i_rt_uid = 0
            
            if len(kw_redux) > 0:
                read_tweet=True
                match_kw = True
            
            if len(uid_redux) > 0:
                read_tweet=True
                match_uid = True
            
            if rt_ignore or geo_only:
                read_tweet=True
                
            
            for fn in datafiles:
                i_line = 0
                with open(dir_in+fn, 'r') as infile:
                    for line in infile.readlines():
                        if i_line==0 and header:
                            head = line #If first line is expected to be a header, save the line as "head"
                        else:
                            if read_tweet: # If tweets need to be read
                                l_list = line.split(self.delimit)
                                added = False
                                ignored = False
                                is_rt = False
                                matched_kw = False
                                matched_uid = False

                                if len(l_list[rt_incol]) > 0:
                                    i_rt_total = i_rt_total + 1
                                    is_rt = True
                                    if rt_ignore:
                                        ignored = True # Ignore RTs
                                
                                if geo_only and len(l_list[geo_incol]) < 1:
                                    ignored = True # Ignore non-Geocoded
                                
                                if match_kw:
                                    text = ' '+l_list[kw_incol]+' '+l_list[quote_incol]+' '
                                    text = parselogic.reformat(text, emojis=None, mode=4.5, lcase=True)
                                    kw_is_rt = False
                                    for kw in kw_redux:
                                        if parselogic.match(kw, text):
                                            matched_kw = True
                                            i_kw += 1
                                            if is_rt:
                                                kw_is_rt = True
                                                i_rt_kw += 1
                                            break
                                    if not matched_kw:
                                        ignored = True
                                
                                if match_uid and not ignored:
                                    if l_list[uid_incol] in uid_redux:
                                        matched_uid = True
                                        i_uid += 1
                                        if is_rt:
                                            uid_is_rt = True
                                            i_rt_uid += 1
                                    else:
                                        ignored = True
                                        
                                    #for uid in uid_redux:
                                    #    if l_list[uid_incol] == uid:
                                    #        matched_uid = True
                                    #        i_uid += 1
                                    #        if is_rt:
                                    #            uid_is_rt = True
                                    #            i_rt_uid += 1
                                    #        break
                                    #if not matched_uid:
                                    #    ignored = True
                                
                                if not ignored:
                                    datadict.setdefault(fn, []).append(line)
                                    datalines.append(line)
                            
                            else: # Nothing to check
                                datadict.setdefault(fn, []).append(line)
                                datalines.append(line)
                        i_line += 1 #Counting all read lines per file
                    i_total = i_total + i_line - 1 #Total data lines (-1 for header line)
            
            self.head = head
            self.datadict = datadict
            self.data = datalines
            print('\n----- FILE TOTALS:')
            print('All Tweets+RTs:       '+str(i_total))
            print('Retweets:             '+str(i_rt_total))
            print('Original Tweets:      '+str(i_total-i_rt_total))
            
            if match_kw:
                print('\n----- KEYWORD MATCHED:')
                print('All Tweets+RTs:      ',i_kw)
                print('Retweets:            ',i_rt_kw)
                print('Original Tweets:     ',i_kw-i_rt_kw)
            if match_uid:
                if match_kw:
                    print('\n----- USER_ID MATCHED: (w/in keyword matched)')
                else:
                    print('\n----- USER_ID MATCHED:')
                if rt_ignore:
                    print('Retweets ignored')
                else:
                    print('All Tweets+RTs:      ',i_uid)
                    print('Retweets:            ',i_rt_uid)
                print('Original Tweets:     ',i_uid-i_rt_uid)
            
            
            print('\nTweets in sample:    ',len(datalines))



    # This provides a simple random sample. 
    # reduce <= 0 results in a shuffled set of all tweets (default)
    # reduce < 1 results in a proportional subsample (percentage of total tweets)
    # reduce >= 1 results in a fixed subsample (a set number of tweets)
    def rand(self, reduce=0):
        data = self.data

        import random

        print('\nTweets available:    ',len(data))
        print('Reduction value:     ',reduce)

        try:
            reduce = float(reduce)
            if reduce <= 0:
                # Randomization without reduction
                data = random.sample(data, len(data))
            elif reduce < 1:
                # Reduce by percent
                n = int(len(data)*reduce)
                data = random.sample(data, n)
            else:
                # Reduce to max frequency
                if reduce > len(data):
                    reduce = len(data)
                data = random.sample(data, int(reduce))
            print('Tweets retained:     ',len(data))
            return data
        except: 
            raise ValueError('Reduce argument must be numeric.')
            
    # This provides a stratified random sample. 
    # If reduce < 1, the result is a representative proportion of tweets per file
    # If reduce > 1, the result is an equal number of tweets per file (this feature is disabled)
    def strat(self, reduce=0):
        datadict = self.datadict
        files = []
        s = []
        flat_list = []
            
        print('\nSTRATIFICATION ACTIVE...\n')

        for k, v in datadict.items():
            files.append(k)
        for f in sorted(files):
            print('----- '+f)
            s.append(subsample(datadict[f]).rand(reduce))
            print('\n')
        #for k, v in datadict.items():
        #    print('----- '+str(k))
        #    s.append(subsample(v).rand(reduce))
        #    print('\n')
            
        for sublist in s:
            for item in sublist:
                flat_list.append(item)
        data = flat_list
        
        print('\nTotal retained:    '+str(len(data)))
        return data
                
    # This provides a subsample where top hashtags reflect population trends
    # The Spearman Rho correlation coeficient assesses sample representation 
    # This option does not support stratification
    def hashspear(self, reduce=0, hash_n=20, spear=0.9, iterate=100):
        kw_incol = self.kw_incol
        data = self.data
        import string, re, operator, math 
        
        def gethashtags(data=data, hash_n=hash_n):
            hashdict = {}
            hashtop = {}
            for line in data:
                # Get tweet text:
                text = line.lower().split(self.delimit)[kw_incol]
                #text = re.sub('\\',' ', text) # Unclear what this was supposed to accomplish
                # Get unique hashtags from within tweet text:
                hashtags = list(set(part[1:] for part in text.split() if part.startswith('#')))
                # Remove empty entry, if present
                try: hashtags.remove('')
                except: pass
                # Add hashtag and count to hashdict
                for hashtag in hashtags:
                    # Remove punctuation from hashtag strings:
                    hashtag = hashtag.strip(string.punctuation)
                    # Add hashtag to hashdict:
                    if hashtag not in hashdict:
                        hashdict[hashtag] = 1
                    else:
                        hashdict[hashtag] += 1
            n = 0
            for tophash in sorted(hashdict, key=hashdict.get, reverse=True):
                if n <= hash_n or not hash_n:
                    
                    # Add top hashtags to hashtop dict
                    hashtop[str(tophash)] = hashdict[tophash]
                    n = n + 1
                else:
                    # Stop after hash_n is reached
                    break
            return hashtop, data

        def spearman(matrix):
            # Create a list array from a matrix column 
            def array(col, matrix):
                array = []
                for row in matrix:
                    array.append(row[col])
                return array
                
            # Calculate ranks for array values (accounting for ties)
            # From http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
            def rank_simple(vector):
                return sorted(range(len(vector)), key=vector.__getitem__)
            
            def rankdata(a):
                n = len(a)
                ivec=rank_simple(a)
                svec=[a[rank] for rank in ivec]
                sumranks = 0
                dupcount = 0
                newarray = [0]*n
                for i in range(n):
                    sumranks += i
                    dupcount += 1
                    if i==n-1 or svec[i] != svec[i+1]:
                        averank = sumranks / float(dupcount) + 1
                        for j in range(i-dupcount+1,i+1):
                            newarray[ivec[j]] = averank
                        sumranks = 0
                        dupcount = 0
                return newarray
            
            # create separate arrays for sample and population ranks
            rank_samp = rankdata(array(1, matrix))
            rank_pop = rankdata(array(2, matrix))
            
            # calculate means for the arrays
            m_samp = sum(rank_samp) / len(rank_samp)
            m_pop = sum(rank_pop) / len(rank_pop)
            
            # create a list of tuples for paired ranks
            ranks = list(zip(rank_samp, rank_pop))

            # initialize new numerator and denominator values for Sigma values
            n0 = 0
            d1 = 0
            d2 = 0
            
            # calculate Sigma values to be used in the equation
            for row in ranks:
                x = row[0]  # x = sample rank
                y = row[1]  # y = population rank
                xm = m_samp # xm = sample mean
                ym = m_pop  # ym = population mean
                
                # Equation: http://statistics.laerd.com/statistical-guides/spearmans-rank-order-correlation-statistical-guide.php
                n0 = n0 + ((x-xm)*(y-ym))
                d1 = d1 + (x-xm)**2
                d2 = d2 + (y-ym)**2
                
            # insert Sigma values into Spearman equation and calculate Rho
            rho = n0 / math.sqrt(d1*d2)
            
            # return Spearman's Rho
            #print('Rho: ', rho)
            return rho

            
        def resample (self, population):
            
            # get a random sub-sample of the population        
            sample = gethashtags(self.rand(reduce=reduce), hash_n=False)
       
            # Create basic matrix of hashtag counts for sample and associated population value
            matrix = []
            for pk, pv in population[0].items():
                if pk in sample[0]:
                    matrix.append([pk,sample[0][pk],pv,round(sample[0][pk]/pv, 3)])
                else:
                    matrix.append([pk,0,pv,0])
            matrix = sorted(matrix, key=operator.itemgetter(2))
            self.returns['matrix'] = matrix[::-1]
                
            return sample[1], spearman(matrix)


        # get counts for top hashtags in the population of tweets   
        population = gethashtags(self.rand(), hash_n=hash_n)
            
        i = 0
        low_rho = 0
        while i < iterate:
            i = i + 1
            data, i_rho = resample(self, population)
            if i_rho >= spear:
                self.returns['i'] = i
                self.returns['rho'] = i_rho
                self.returns['data'] = data
                print('Rho: ', self.returns['rho'], 'Iterations: ', self.returns['i'])
                return self.returns
            elif i_rho > low_rho:
                self.returns['i'] = i
                self.returns['rho'] = i_rho
                self.returns['data'] = data
                low_rho = i_rho
            else:
                pass
        print('Best Rho: ', self.returns['rho'], 'Iterations: ', self.returns['i'])
        return self.returns
            

if __name__ == '__main__':

    # Default variables
    reduce = 0.02
    stratify = False
    hashspear = False
    hash_n = 20
    spear = 0.90
    iterate = 100
    halt = False
    keywords = []
    uids = []
    
    
    # Unique command line arguments
    i = 0
    try:
        for arg in sys.argv:
            if arg.lower() in ['-r','-redux','-reduce']: # '-r' indicates reduction approach 
                reduce = float(sys.argv[i+1])
            if arg.lower() in ['-s','-strat','-stratify']: # '-s' indicates stratification 
                stratify = True
            if arg.lower() in ['-h','-hash','-hashspear']: # '-h' indicates hashspear (req. 1 argument)
                hashspear = True
                hash_n = int(sys.argv[i+1])
                spear = float(sys.argv[i+2])
                iterate = int(sys.argv[i+3])
            i = i+1
    
    except:
        print ('ERROR: Command line arguments failed to parse.')
        halt = True

    if stratify and reduce >= 1:
        print ('ERROR: Stratification is only supported as proportion, not count value.')
        halt = True

    if stratify and hashspear:
        print ('ERROR: Stratification is not supported within hashspear.')
        halt = True
        

    if not halt:
        # Get typical defaults and command line arguments
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
        dir_in_uid = cv['dir_in_uid']
        f_uid = cv['f_uid']
        
        # Get keywords
        if cv['f_kws'] or cv['dir_in_kws']:
            keywords = parselogic.kwslist(dir_in_kws, f_kws)

        # Get UIDs
        if cv['f_uid'] or cv['dir_in_uid']:
            uids = parselogic.uidlist(dir_in_uid, f_uid)
    
        # Get data files
        if stratify:
            datafiles = parselogic.filelist(dir_in, start=start, end=end, silent=True)
        else:
            datafiles = parselogic.filelist(dir_in, start=start, end=end)

        print('\n----- PROCESSING...\n')
        
        if len(keywords) == 0 and len(uids) > 0:
            print('NOTE: Using UID filtering without KWS filters.\n')
    
        if len(uids) > 0 and rt_ignore:
            print('NOTE: Using UID filtering and also ignoring RTs.',
                  '\n      This may not be desirable if using data for SNA.',
                  '\n      Don\'t forget to specify "-rt" argument if necessary.\n')
        elif rt_ignore: 
            print('\nNOTE: Retweets are being ignored.\n')






    if not halt:
        redux1 = subsample(dir_in=dir_in, datafiles=datafiles, kw_redux=keywords, uid_redux=uids, rt_ignore=rt_ignore)
        head = redux1.head
        if reduce >= 0: r = int(reduce)
        else: r = reduce
        if hashspear:
            out_spec = '_hash'+str(r)+'_h'+str(hash_n)+'_s'+str(spear)+'_i'+str(iterate)
            redux2 = redux1.hashspear(reduce=reduce, hash_n=hash_n, spear=spear, iterate=iterate)
        elif stratify:
            out_spec = '_strat'+str(r)
            redux2 = redux1.strat(reduce=reduce)
        else:
            out_spec = '_rand'+str(r)
            redux2 = redux1.rand(reduce=reduce)
    
        outfile = 'sub'+out_spec+f_ext
                
        #head = 'userID,username,utc off,profile created,favorites,followers,following,tweets,tweetID,retweetID,retweet user,retweet count,extended,text,date,day,year,month,day,hour,min,sec,url,lat,lon\n'
        
        with open(dir_out+f_stem+outfile, 'w+') as ofile:
            ofile.write(head)
        with open(dir_out+f_stem+outfile, 'a+') as ofile:
            for line in redux2:
                ofile.write(line)
    
    if not halt:
        print('\nProcess complete!\n\n')
