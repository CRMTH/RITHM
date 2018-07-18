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
    as CSV files from a defined system directory.
    
    . 
    """
    ##### If column numbers change, "*_incol" vars need updating - this dependency 
    ##### should be fixed so that the process is aware of standard variable names
    ##### and calculates column numbers accordingly. 
    def __init__(self, data, dirout='', header=True, combine=True,
                 kw_redux=[], kw_incol=12, quote_incol=13, 
                 rt_ignore=True, rt_incol=9, 
                 geo_only=False, geo_incol=16):  
        self.data = data
        self.kw_incol = kw_incol
        self.returns = {}                    
        self.delimit = ','

        if len(kw_redux) > 0 or rt_ignore or geo_only: 
            read_tweet=True
        else: 
            read_tweet=False
            
        if type(data) == str:
            # String data should refer to a directory of CSV data files

            datadict = {}
            datalines = []

            import os
            
            try:
                files = sorted(os.listdir(data))
            except:
                raise IOError('String object passed, but it is not a valid directory.')
            i_total = 0
            i_rt_total = 0
            i_kw = 0
            i_rt_kw = 0
            for fn in files:
                ###### <--- Implement date range constraints about here
                if fn[-4:] in ['.csv', '.tsv']:
                    i_line = 0
                    with open(data+fn, 'r') as infile:
                        for line in infile.readlines():
                            if i_line==0:
                                if '\t' in line: self.delimit = '\t' #Determine if TSV file format from 1st line

                            if i_line==0 and header:
                                head = line #If first line is expected to be a header, save the line as "head"
                            else:
                                if read_tweet: # If tweets need to be read
                                    l_list = line.split(self.delimit)
                                    added = False
                                    ignored = False
                                    is_rt = False
                                    if rt_ignore and len(l_list[rt_incol]) > 0:
                                        i_rt_total = i_rt_total + 1
                                        is_rt = True
                                        ignored = True # Ignore RTs
                                    if geo_only and len(l_list[geo_incol]) < 1:
                                        ignored = True # Ignore non-Geocoded

                                    if len(kw_redux)>0:
                                        kw_is_rt = False
                                        for kw in kw_redux:
                                            # Remember to search text and quoted text!
                                            text = l_list[kw_incol]+' '+l_list[quote_incol]
                                            text = parselogic.reformat(text, mode=4.5, lcase=True)
                                            #if kw in text.lower() and not added and not ignored:
                                            if parselogic.match(kw, text):
                                                if not added and not ignored:
                                                    datadict.setdefault(fn, []).append(line)
                                                    datalines.append(line)
                                                    added = True
                                                    i_kw = i_kw + 1
                                                elif is_rt:
                                                    kw_is_rt = True
                                        if kw_is_rt:
                                            i_kw = i_kw + 1
                                            i_rt_kw = i_rt_kw + 1
                                    else:
                                        if not added and not ignored:
                                            datadict.setdefault(fn, []).append(line)
                                            datalines.append(line)
                                            added = True
                                else: # Fast and simple
                                    datadict.setdefault(fn, []).append(line)
                                    datalines.append(line)
                            i_line = i_line + 1 #Counting all read lines per file
                        i_total = i_total + i_line - 1 #Total data lines (-1 for header line)

            self.head = head
            self.datadict = datadict
            self.data = datalines
            print('\n----- FILE TOTALS:')
            print('Tweets observed:   '+str(i_total))
            print('Retweets observed: '+str(i_rt_total))
            print('Original tweets:   '+str(i_total-i_rt_total))
            
            if len(kw_redux)>0:
                print('\n----- KEYWORD-MATCHED:')
                print('Tweets observed:   '+str(i_kw))
                print('Retweets observed: '+str(i_rt_kw))
                print('Original tweets:   '+str(i_kw-i_rt_kw))

            if rt_ignore: print('\nIGNORING RETWEETS...\n')

            print('Tweets in sample:  '+str(len(datalines)))



    # This provides a simple random sample. 
    # reduce <= 0 results in a shuffled set of all tweets (default)
    # reduce < 1 results in a proportional subsample (percentage of total tweets)
    # reduce >= 1 results in a fixed subsample (a set number of tweets)
    def rand(self, reduce=0):
        data = self.data

        import random

        print('Tweets available:  '+str(len(data)))
        print('Reduction value:   '+str(reduce))

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
            print('Tweets retained:   '+str(len(data)))
            return data
        except: 
            raise ValueError('Reduce argument must be numeric.')
            
    # This provides a stratified random sample. 
    # If reduce < 1, the result is a representative proportion of tweets per day
    # If reduce > 1, the result is an equal number of tweets per day
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
        
        print('\n\nTotal retained:    '+str(len(data)))
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
                text = re.sub('\\',' ', text) # <-- Is this necessary?
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
            

halt = False
### Keyword arguments and default specifications

data_dir = '../data/parser_out/'
outfile = 'reduced/reduced.csv'
reduce = 0.01
stratify = False
hashspear = False
hash_n = 20
spear = 0.90
iterate = 100
kws = False
kw_redux = []
rt_ignore = True


if len(sys.argv) > 1: # If command line arguments were passed
    print(sys.argv)
    i = 0
    try:
        for arg in sys.argv:
            if arg.lower() in ['-i','-input','-indir','-dir']: # '-i' indicates input directory (req. 1 argument)
                data_dir = sys.argv[i+1]
            if arg.lower() in ['-o','-out','-outfile']: # '-o' indicates outfile (req. 1 argument)
                outfile = sys.argv[i+1]
            if arg.lower() in ['-r','-redux','-reduce']: # '-r' indicates reduction approach 
                reduce = float(sys.argv[i+1])
            if arg.lower() in ['-s','-strat','-stratify']: # '-s' indicates stratification 
                stratify = True
            if arg.lower() in ['-h','-hash','-hashspear']: # '-h' indicates hashspear (req. 1 argument)
                stratify = False
                hashspear = True
                hash_n = int(sys.argv[i+1])
                spear = float(sys.argv[i+2])
                iterate = int(sys.argv[i+3])
            if arg.lower() in ['-d','-date','-dates']: # '-d' indicates start/end dates (req. 2 MMDDYYYY objects)
                start = int(sys.argv[i+1])
                end = int(sys.argv[i+2])
            if arg.lower() in ['-k','-kw','-kws', '-keywords']: # '-k' limit to keywords (req. 1 argument for keyword file)
                kws = True
                kw_file = sys.argv[i+1]
            if arg.lower() in ['-rt','-rts']: # '-rt' includes RTs
                rt_ignore = False
            i = i+1
    except:
        print ('ERROR: Command line arguments failed to parse.')
        halt = True

if kws:
    try:
        with open(data_dir+kw_file, 'r') as kf:
            for k in kf:
                if k.strip() not in ['','#']:
                    kw_redux.append(k.strip())
    except:
        print('ERROR: Keyword list failed to load.')
        halt = True

if not halt:
    redux1 = subsample(data_dir, kw_redux=kw_redux, rt_ignore=rt_ignore)
    head = redux1.head
    if hashspear:
        redux2 = redux1.hashspear(reduce=reduce, hash_n=hash_n, spear=spear, iterate=iterate)
    elif stratify:
        redux2 = redux1.strat(reduce=reduce)
    else:
        redux2 = redux1.rand(reduce=reduce)
        

#head = 'userID,username,utc off,profile created,favorites,followers,following,tweets,tweetID,retweetID,retweet user,retweet count,extended,text,date,day,year,month,day,hour,min,sec,url,lat,lon\n'

with open(data_dir+outfile, 'a+') as outfile:
    outfile.write(head)
    #for line in y['data']: #This might be needed for one of the approaches?
    for line in redux2:
        outfile.write(line)

