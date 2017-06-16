# -*- coding: utf-8 -*-
"""
Center for Research on Media, Technology, and Health
University of Pittsburgh

Author: colditzjb
Update: 2017-06-12

Python: 2.7 (tested) & 3.5 (preferred)

Required Python packages:
 tweepy: http://docs.tweepy.org/en/v3.4.0/install.html
   & requests_oauthlib: http://github.com/requests/requests-oauthlib

"""

import time, datetime, sys, json, os
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

## SET DIRECTORIES AND OPTIONS HERE
indirectory = '//home/jason/repos/streamer/' #Input directory
outdirectory = '//home/jason/repos/streamer/out/' #Output directory
suffix = '_streamer.json' #Suffix (always include ".json" extension)
auth = 'auth.ini' #Text file w/ Twitter API authentication keys
lang = ['en'] #Language filters: https://dev.twitter.com/web/overview/languages


## --------------------------------------------------------------------
## --- Don't mess with the rest, unless you are improving the code. ---
## --------------------------------------------------------------------


# Delete the "DeleteToKill.txt" file to stop the streamer 
## Check for killSwitch file
def killSwitch(killDirectory=indirectory):
    if 'DeleteToKill.txt' in list(os.listdir(killDirectory)):
        return False
    else:
        return True

## Get Twitter API keys    
def keyring(infile=indirectory+auth):
    lines = [line.rstrip('\n') for line in open(infile)]
    consumer_key = lines[0]
    consumer_secret = lines[1]
    access_token = lines[2]
    access_token_secret = lines[3]
    return consumer_key, consumer_secret, access_token, access_token_secret

## Get streaming API search filters
def getKeywords(kwDirectory=indirectory, lang=lang):
    fileTerms = []
    keywords = []
    files = list(os.listdir(kwDirectory))
    for f in files:
        if f[-4:] == '.kws':
            try:
                fileTerms.append([line.rstrip('\n') for line in open(f)])
            except:
                pass
    for group in fileTerms:
        for term in group:
            if len(term) < 2:
                pass
            else:
                keywords.append(term)
    if len(list(set(keywords))) == 0:
        return False
    else:
        return list(set(keywords)), lang

## Set output file
def set_file(suffix=suffix):
    global outfile
    outfile = outdirectory+datetime.datetime.today().strftime('%Y%m%d%H%M%S')+suffix 
    global oldtime
    oldtime = datetime.datetime.today().strftime('%y%m%d') 
    getKeywords(indirectory)
    return outfile, oldtime

## Post to log file 
def err_log(err, code='err', errDir=outdirectory):
    err_str=str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))+'\t'+code+'\t'+err+'\n'
    errlog = str(datetime.datetime.today().strftime('%Y%m%d'))+'_errors.tsv'
    with open(errDir+errlog,'a+') as log:
        log.write(err_str)

## Clear log file
def err_clr():
    global err_count
    if err_count > 0:
        err_count = 0

## Exponential backoff
err_count = 0
def back_off(seconds=0):
    global err_count 
    if seconds==0:
        err_count += 1
        seconds = 2**err_count*30
    err = 'backing-off for\t'+str(seconds)
    err_log(err, code='zzz')
    time.sleep(seconds)
        
## Set streamer process and common error handling
def setStreamer(KW=getKeywords()):
    while True:
        try:
            if killSwitch():
                err_log(err='Stream killed by user', code='xit')
                break
            l = StdOutListener()
            auth = OAuthHandler(keyring()[0], keyring()[1])
            auth.set_access_token(keyring()[2], keyring()[3])        
            stream = Stream(auth, l) 
            if KW == False:
                stream.sample() #Use 1% sample of all Twitter activity
            else:
                stream.filter(track=KW[0], languages=KW[1]) #Keywords + language                
            
        except: #Error handling for known error types
            err = str(sys.exc_info()[1])
            #print(err)
            if killSwitch():
                err_log(err='Stream killed by user', code='xit')
                break
            elif 'retries exceeded' in err:
                err_log(err='Connection broken')
                back_off()  #Connection issue 
                pass
            elif 'Incomplete' in err:
                err_log(err) #Connection hiccup
                pass
            elif 'timed out' in err:
                err_log(err) #Connection hiccup
                pass
            elif 'decode' in err:
                err_log(err)  #Formatting error
                pass
            elif 'attribute' in err:
                err_log(err) #Formatting error
                pass
            elif 'length' in err:
                #err_log(err) #Twitter API "keep alive" ping
                pass
            else: #Error handling for unknown error types
                err_log(err)
                back_off()

## Tweepy listener class and serious Twitter error handling
class StdOutListener(StreamListener):
    def on_data(self, data):
        if not killSwitch():
            global oldtime
            if datetime.datetime.today().strftime('%y%m%d') > oldtime:        
                err_clr()
                set_file()
                setStreamer()
                err_log(err='Streamer running', code='ini')
                err_log(err=str(getKeywords()), code='kws')
            out_file = open(outfile,"a")
            decoded = json.loads(data)
            json.dump(decoded, out_file, indent=0)
            #print('.', end=' ')
        else:
            #err_log(err='Stream killed by user (StdOut)', code='xit')
            return False

    def on_error(self, status_code):
        print(status_code, ' Twitter error')
        if status_code in ['104', '420']: 
            err = 'Twitter error'
            err_log(err, code=str(status_code))
            back_off()
        return True

## --------------------------------------------------------------------
## --- Start the process...
## --------------------------------------------------------------------
if __name__ == '__main__':

    # Creates new killSwitch file
    with open(indirectory+'DeleteToKill.txt','w+') as switch:
        switch.write('Delete this file to kill the streamer.')
        
    # Logs startup and keywords
    err_log(err='Streamer initialized', code='ini')
    err_log(err=str(getKeywords()), code='kws')

    # Set new output data file and streamer process
    set_file()
    setStreamer()
