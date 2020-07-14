# -*- coding: utf-8 -*-
"""
Center for Research on Media, Technology, and Health
University of Pittsburgh

Authors:  @colditzjb, @sanyabt
Version: 2018-12-07

Python version: 2.7 (tested) & 3.5+ (preferred)

Required Python packages:
 twython: https://github.com/ryanmcgrath/twython
   & requests_oauthlib: http://github.com/requests/requests-oauthlib

"""

import time, datetime, sys, json, os, csv
from twython import TwythonStreamer

## SET DIRECTORIES AND OPTIONS HERE
suffix = '_streamer.json' # Suffix (always include ".json" extension!)
lang = ['en'] # Language filters: https://dev.twitter.com/web/overview/languages
dir_path = '~/RITHM/streamer/' # A default directory path for streamer folder


## --------------------------------------------------------------------
## --- Don't mess with the rest, unless you are improving the code! ---
## --------------------------------------------------------------------


## Define file paths from paths.ini
try: 
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/'
except: 
    print('Failed to set dir_path programmatically!\n',
              'Streamer works better if run from command line.\n',
              'Setting dir_path to: ', dir_path)
    input('Press Enter to continue...')
    
def paths(dir_path):
    for line in open(dir_path+'paths.ini'):
        if 'setup_in' in line:
            indirectory = line.split(':')[1].strip()
        if 'data_out' in line:
            outdirectory = line.split(':')[1].strip()
    if not indirectory:
        print('failed to set indirectory')
        indirectory = dir_path
    if not outdirectory:
        print('failed to set outdirectory')
        outdirectory = '../data/streamer_raw/'
    return indirectory, outdirectory

indirectory = paths(dir_path)[0]
outdirectory = paths(dir_path)[1]




# Delete the "DeleteToKill.txt" file to stop the streamer 
## Check for killSwitch file
global kill
kill = False
def killSwitch(killDirectory=indirectory):
    global kill
    if kill == True:
        return True
    elif 'DeleteToKill.txt' not in list(os.listdir(killDirectory)):
        return True
    else:
        return False



def keyring(infile=dir_path+'auth.ini'):
    keys = []
    for line in open(infile):
            if line[:1] =='#' or line.strip()=='':
                continue # Ignore comments or blank lines 
            else:
                if ': ' in line:
                    keys.append(str(line.split(': ')[1]).strip())
                else:
                    keys.append(str(line).strip())
    return keys


## Clear log file
err_count = 0
def err_clr():
    global err_count
    if err_count > 0:
        err_count = 0

## Exponential backoff
def back_off(seconds=None):
    global err_count 
    if seconds is None:
        err_count += 1
        seconds = 2**err_count*30
    err = 'backing-off (seconds)\t'+str(seconds)
    err_log(err, code='zzz')
    time.sleep(seconds)


## Post to Sentry
try:
    from raven import Client
    def sentry(msg):
    
        t_client = Client(
            # This is the secret key
            dsn=keyring[5],
            
            # This will appear as the host name in alerts
            name='Twitter',
            
            ignore_exceptions = [
                    'Http404',
                    'django.exceptions.*',
                    TypeError,
                    ValueError,
                    ]
            )
        t_client.captureMessage(msg)
    ravenStatus = True

except:
    ravenStatus = False


## Post to log file 
def err_log(err, code='err', errDir=outdirectory, errPrint=False, sentryPost=ravenStatus):
    errlog = str(datetime.datetime.today().strftime('%Y%m%d'))+'_log.tsv'
    timestamp = str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
    err_str = timestamp+'\t'+code+'\t'+err+'\n'
    errcatch = False
    if code in ['ini', 'kws', 'zzz', 'xit']:
        if errPrint: print(err_str)
        if sentryPost: sentry(err_str)
        errcatch = True
        with open(errDir+errlog,'a+') as log:
            log.write(err_str)
    else:
        with open('errors.csv','r') as error_file:
            reader = csv.reader(error_file)
            errors = list(reader)
            for erratum in errors:
                if erratum[0] in err.lower() or erratum[0] in code:
                    errcatch = True
                    errmsg = (timestamp+'\t'+code+'\t'+erratum[2]+' ('+erratum[0]+')'+'\n')
                    if 'backoff' in erratum[1]:
                        if errPrint: print(errmsg)
                        if sentryPost: sentry(err_str)
                        with open(errDir+errlog,'a+') as log:
                            log.write(errmsg)
                        back_off()
                    elif 'log' in erratum[1]:
                        if errPrint: print(errmsg)
                        if sentryPost: sentry(err_str)
                        with open(errDir+errlog,'a+') as log:
                            log.write(errmsg)
                    elif 'pass' in erratum[1]:
                        if errPrint: print(errmsg)
                        if sentryPost: sentry(err_str)
                        pass
                    else:
                        if errPrint: print(errmsg)
                        if sentryPost: sentry(err_str)
                        with open(errDir+errlog,'a+') as log:
                            log.write(errmsg+'\tunexpected directive in error file!')
                        back_off()
                        pass
                        
    if errcatch == False:
        if errPrint: print(err_str)
        with open(errDir+errlog,'a+') as log:
            log.write(err_str)
            ###The next 3 lines kill the stream when an unanticipated error is encountered
            #err_log(err='killing stream', code='xit')
            #global kill
            #kill=True
            err_log(err='unanticipated error', code='zzz')
            back_off()


## Get streaming API search filters
def getKeywords(kwDirectory=indirectory, lang=lang):
    fileTerms = []
    keywords = []
    files = list(os.listdir(kwDirectory))
    for f in files:
        if f[-4:] == '.kws':
            try:
                fileTerms.append([line.rstrip('\n') for line in open(kwDirectory+f)])
            except:
                print('Failed to parse KWS file: '+f)
                pass
    for group in fileTerms:
        for term in group:
            if len(term) < 2:
                pass
            else:
                keywords.append(term)
    keywords = list(set(keywords))
    err_log(err=str(keywords)+','+str(lang), code='kws')
    if len(keywords) == 0:
        return False
    else:
        return sorted(keywords), lang

## Set output file
def set_file(suffix=suffix):
    global outfile
    outfile = outdirectory+datetime.datetime.today().strftime('%Y%m%d%H%M%S')+suffix 
    global oldtime
    oldtime = datetime.datetime.today().strftime('%Y%m%d') 
    #getKeywords(indirectory)
    return outfile, oldtime


        
## Set streamer process and common error handling
def setStreamer():
    KW=getKeywords()
    while True:
        try:
            if killSwitch():
                err_log(err='stream terminated by user', code='xit')
                break
            else:
                err_log(err='stream connecting', code='ini')
                stream = MyStreamer(keyring()[0],keyring()[1],keyring()[2],keyring()[3]) 
                if KW == False:
                    stream.statuses.sample() #Use 1% sample of all Twitter activity
                elif len(KW[1]) == 0 or KW[1] == False or KW[1] == None:
                    stream.statuses.filter(track=KW[0]) #Keywords, no language                                   
                else:
                    stream.statuses.filter(track=KW[0], language=KW[1]) #Keywords + language
                    
            
        except: #Error handling
            err = str(sys.exc_info()[1])
            #print(err)
            if killSwitch():
                err_log(err='stream terminated with error', code='xit')
                break
            else: #Error handling
                err_log(err)
                pass
                
## Tweepy listener class and serious Twitter error handling
class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        if not killSwitch():
            global oldtime
            if datetime.datetime.today().strftime('%Y%m%d') > oldtime:        
                err_clr()
                set_file()
                setStreamer()
                #err_log(err='Streamer running', code='ini')
                err_log(err=str(getKeywords()), code='kws')
            out_file = open(outfile,"a")
            #decoded = json.loads(data)
            #json.dump(decoded, out_file, indent=0)
            json.dump(data, out_file, indent=0)
            data
            #print('.', end=' ')
        else:
            #err_log(err='Stream killed by user (StdOut)', code='xit')
            self.disconnect()

    def on_error(self, status_code, data):
        print(status_code, str(data), ' Twitter error')
        if not killSwitch():
            if str(status_code) in ['104', '420']: 
                err = 'Twitter error'
                err_log(err, code = str(status_code))
                back_off()
            else:
                err = 'Twitter error'
                err_log(err, code = str(status_code))            
            #return True
        else:
            self.disconnect()
            

                

## --------------------------------------------------------------------
## --- Start the process...
## --------------------------------------------------------------------
if __name__ == '__main__':

    # Creates new killSwitch file
    with open(indirectory+'DeleteToKill.txt','w+') as switch:
        switch.write('Delete this file to kill the streamer.')
    # Sets permissions as "-rwxrwxr-x", i.e., 0o775
    try:
        os.chmod(indirectory+'DeleteToKill.txt', 0o775)
    except:
        print('Failed to set custom file permissions for DeleteToKill.txt')
        
    # Logs startup and keywords
    #err_log(err='streamer initialized', code='ini')
    #err_log(err=str(getKeywords()), code='kws')

    # Set new output data file and streamer process
    set_file()
    try:
        # Sets the process into motion
        setStreamer()
    except:
        # Tries to email a message if the process crashed
        try:
            import mailmsg
            mailmsg.main(dir_path)
        except:
            print('mailmsg.py failed to send a message for streamer.py failure.\n'+
                  'Ensure dependencies are installed and mail.ini is configured.')
        pass
