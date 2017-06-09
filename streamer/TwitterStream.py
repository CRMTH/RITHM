# -*- coding: utf-8 -*-
"""
Created on Tue Feb 24 11:25:35 2015

@author: ColdJB
"""


# Useful links:
#   Working with timelines: https://dev.twitter.com/docs/working-with-timelines
#   Twython info: https://github.com/ryanmcgrath/twython

# Required packages:
#   twython
#       requests_oauthlib
#           requests
#           oauthlib

from twython import Twython
import time, datetime, sys, json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import cPickle as pickle
import os, csv


pkl_mode = False

## Twitter API keys (ATOD_stream):
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

# Set directory and use dynamic file names
indirectory = '//home/colditz/'
outdirectory = '//data/colditz/twitter/'

def globs():
    global filters
    filters = []
globs()

def getKeywords(kwDirectory):
    # Search terms: (separated with commas; spaces = OR)
    files = list(os.listdir(kwDirectory))
    global filters
    filters = []
    kwFs = [datetime.datetime.today().strftime('%m-%d-20%y')]
    for f in files:
        if f[-4:] == '.kws':
            kwFs.append(f)
            filter_file = kwDirectory+f
            get_filters = open(filter_file,"r")
            lines = get_filters.readlines()
            get_filters.close()
            kws = [l.replace('\n', '') for l in lines]
            for kw in kws:
                if kw not in filters:
                    filters.append(kw)
    with open(kwDirectory+'kwLog.csv' , 'ab') as log:
        logFile = csv.writer(log, delimiter=',', dialect='excel')
        logFile.writerow([fn for fn in kwFs])
    #print filters
        #filters = ''.join(lines).replace('\n',',')

topic = 'streamer' 
def set_file():
    global outfile
    if pkl_mode:
        outfile = outdirectory+datetime.datetime.today().strftime('%Y%m%d%H%M%S')+'_'+topic+'.pkl' 
    else:
        outfile = outdirectory+datetime.datetime.today().strftime('%Y%m%d%H%M%S')+'_'+topic+'.json' 
    global errlog    
    errlog = outdirectory+datetime.datetime.today().strftime('%Y%m%d%H%M%S')+'_errors.txt'
    global oldtime
    oldtime = datetime.datetime.today().strftime('%y%m%d') 
    getKeywords(indirectory)
    #global filters
    #print filters
set_file()

# This is used for exponential backoff
err_count = 0
def back_off():
    global err_count 
    err_count += 1
    time.sleep(2**err_count*30)
def err_clr():
    global err_count
    if err_count > 0:
        err_msg='@ColditzJB Back-off count in recent data: '+str(err_count)+' \n\nSome data were lost.\n'+str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
        try: tweet.update_status(status=err_msg)
        except: pass
        err_count = 0

def setStreamer():
    #stream = MyStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    tweet = Twython(consumer_key, consumer_secret, access_token, access_token_secret)
    #
    while True:
        try:
            l = StdOutListener()
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)        
            stream = Stream(auth, l) 
            global filters
            #print filters
            stream.filter(track=filters, languages=['en']) #This is a limited search based on filters.txt file
            #stream.statuses.sample() #This is a 1% sample of all Twitter activity
        except:
            err = str(sys.exc_info()[1])
            err_str=str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))+',000,'+err+'\n'
            global errlog            
            log_err = open(errlog,"a")
            log_err.write(err_str)
            log_err.close()
            if 'Max retries exceeded' in err:
                err_msg='@ColditzJB CONNECTION REFUSED!\n\nTime-out.\n'+str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
                try: tweet.update_status(status=err_msg)
                except: back_off()
            elif 'IncompleteRead' in err:
                #err_msg='@ColditzJB Experiencing some latency.\n\nQueue dumped.\n'+str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
                #tweet.update_status(status=err_msg)
                pass
            elif 'decode byte' in err:
                #err_msg='@ColditzJB Can not decode byte.\n\nTweet dropped.\n'+str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
                #tweet.update_status(status=err_msg)
                pass
            elif 'has no attribute' in err:
                #err_msg='@ColditzJB No stripping, object.\n\nMoving on...\n'+str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
                #tweet.update_status(status=err_msg)
                pass
            elif 'timed out' in err:
                #err_msg='@ColditzJB Connection timed out.\n\nMoving on...\n'+str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
                #tweet.update_status(status=err_msg)
                pass
            else:
                err_msg='@ColditzJB '+err[:80]+'\n\nTime-out.\n'+str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
                try: tweet.update_status(status=err_msg)
                except: pass
                back_off()
            print err
            continue
        break


class StdOutListener(StreamListener):
    def on_data(self, data):
        global oldtime
        if datetime.datetime.today().strftime('%y%m%d') > oldtime:        
            err_clr()
            set_file()
            setStreamer()
        out_file = open(outfile,"a")
        decoded = json.loads(data)
        if pkl_mode:
            pickle.dump(decoded, out_file, pickle.HIGHEST_PROTOCOL)
        else:
            json.dump(decoded,out_file, indent=0)

    def on_error(self, status_code):
        #err_msg='@ColditzJB ('+str(status_code)+') Twitter error.\n\n\n'+str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
        #tweet.update_status(status=err_msg)
        err_str=str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))+','+str(status_code)+',Twitter error\n'
        log_err = open(errlog,"a")
        log_err.write(err_str)
        log_err.close()
        print status_code, ' Twitter error'
        if status_code in ['104', '420']: 
            back_off()
        return True

setStreamer()

#if __name__ == '__main__':
#    l = StdOutListener()
#    auth = OAuthHandler(consumer_key, consumer_secret)
#    auth.set_access_token(access_token, access_token_secret)
#
#    stream = Stream(auth, l)
#    stream.filter(track=['lol'])
