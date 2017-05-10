# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 12:35:18 2016

@author: ColdJB
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 09:36:52 2016

@author: ColdJB
"""

import csv, re, pickle, os, datetime, time

starttime = datetime.datetime.now()
print '  Start time:'+str(time.strftime("%Y-%m-%d %H:%M"))


directory = '/pylon2/db4s82p/jcolditz/twitter/'
#directory = 'C:/Users/coldjb/Desktop/'
subdir_i = 'outfiles/'
subdir_o = 'emojified/'
emojilist='emojilist4.csv'
outfile_tweets='OutfileTweets.csv'
outfile_days='OutfileDays.csv'
tweets_out = 0

files = sorted(os.listdir(directory))

    
def CodeEmoji():
    with open(directory+emojilist, 'rb') as f:
        reader = csv.reader(f)
        emoji = list(reader)
    
        filedata = None
    
        files_i = sorted(os.listdir(directory+subdir_i))
        files_o = sorted(os.listdir(directory+subdir_o))

        for fn in files_i:
            if fn in files_o:
                #print fn+' is already in directory.'
                pass
            else:
                print fn+' is being emojified using '+emojilist+'.'
                with open(directory+subdir_i+fn, 'r') as data:
                    filedata = data.read()
                
                for key, val in emoji:
                    filedata = re.sub(key, val, filedata)

                #filedata = re.sub('\\\\','', filedata)
                #filedata = re.sub('  ',' ', filedata)
                    
                with open(directory+subdir_o+fn[9:], 'w') as data:
                    data.write(filedata)
                print '   Completed:'+str(time.strftime("%Y-%m-%d %H:%M"))



def FormatText(tweet):
    tweet = re.sub(r'@([A-Za-z0-9_]+)', '_twitter_user_', tweet)
    tweet = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '_url_link_', tweet)
    tweet = re.sub(',', ' ', tweet)
    tweet = re.sub('\.', ' ', tweet)
    tweet = re.sub('\?', ' ', tweet)
    tweet = re.sub('\!', ' ', tweet)
    tweet = re.sub('\#', ' ', tweet)
    tweet = re.sub('\-', ' ', tweet)
    tweet = re.sub('\\\\', ' ', tweet)
    tweet = re.sub('\[COMMA\]', ' ', tweet)
    tweet = re.sub('\[RETURN\]', ' ', tweet)
    tweet = re.sub('\[', ' ', tweet)
    tweet = re.sub('\]', ' ', tweet)
    tweet = tweet.lower()
    return tweet


def Classify():
    #import nltk
    
    f_pos = open(directory+'classifiers/neg_570_hookah.pkl', 'rb')
    classifier_pos = pickle.load(f_pos)
    f_pos.close()
    
    f_neg = open(directory+'classifiers/pos_2120_hookah.pkl', 'rb')
    classifier_neg = pickle.load(f_neg)
    f_neg.close()
    
    def word_feats(words):
        return dict([(word, True) for word in words])
    
    pos_const = classifier_pos.prob_classify(word_feats('\t')).prob('posPres')
    neg_const = classifier_neg.prob_classify(word_feats('\t')).prob('negPres')


    files_o = sorted(os.listdir(directory+subdir_o))
    time = ' 00:00:00'
    date_then = 0
    n=0
    n_geo=0
    E_pos=0
    E_neg=0
    E_sent1=0
    E_sent2=0

    for fn in files_o:
        date_now = fn[9:17]
        with open(directory+subdir_o+fn, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                n=n+1
                if row[22]: n_geo=n_geo+1
                date_time = str(row[16])+' '+str(row[17])+', '+str(row[15])+' '+str(row[18])+':'+str(row[19])+':'+str(row[20])
                time = ' '+str(row[18])+':'+str(row[19])+':'+str(row[20])
                tweet = FormatText(row[13])
                tokens = re.findall(r"[\w']+|[.,!?;]", tweet.rstrip())
                pos = classifier_pos.prob_classify(word_feats(tokens)).prob('posPres')
                E_pos = E_pos + pos
                neg = classifier_neg.prob_classify(word_feats(tokens)).prob('negPres')
                E_neg = E_neg + neg
                sent1 = pos-neg
                E_sent1 = E_sent1 + sent1
                sent2 = (pos-pos_const)-(neg-neg_const)
                E_sent2 = E_sent2 + sent2
                #print str(round(neg,2))+'\t'+str(round(pos,2))+'\t'+str(round(sent1,3))+'\t'+str(round(sent2,3))+'\t\t'+tweet
                with open(directory+outfile_tweets,'a') as oft:
                    saveFile = csv.writer(oft, delimiter=',', lineterminator='\n')
                    #if tweets_out == 1: saveFile.writerow([date_time, row[13], pos, neg, sent1, sent2])
                    if tweets_out == 1: saveFile.writerow([date_time, row[13], pos, neg, sent1])
            if date_then == 0:
                with open(directory+outfile_days,'w') as ofd:
                    saveFile = csv.writer(ofd, delimiter=',', lineterminator='\n')
                    #saveFile.writerow(['date', 'N', 'N_geo', 'E_pos', 'E_neg', 'E_sent', 'E_sent_adj'])
                    saveFile.writerow(['date', 'N', 'N_geo', 'E_pos', 'E_neg', 'E_sent'])
            if date_then == date_now:
                pass
            else:
                date = str(date_now[4:6])+'/'+str(date_now[6:8])+'/'+str(date_now[0:4])+time
                with open(directory+outfile_days,'a') as ofd:
                    saveFile = csv.writer(ofd, delimiter=',', lineterminator='\n')
                    #saveFile.writerow([date, n, n_geo, E_pos, E_neg, E_sent1, E_sent2])
                    saveFile.writerow([date, n, n_geo, E_pos, E_neg, E_sent1])
                print '.',
                n=0
                n_geo=0
                E_pos=0
                E_neg=0
                E_sent1=0
                E_sent2=0

            date_then = date_now

CodeEmoji()

#print 'Now classifying tweets.'
#Classify()

endtime = datetime.datetime.now()
print '    End time:'+str(time.strftime("%Y-%m-%d %H:%M"))
print 'Process time:'+str(endtime - starttime)
