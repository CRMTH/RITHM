# -*- coding: utf-8 -*-
"""
Created on Fri Jan 06 14:08:24 2017

@author: GMTemp
"""

###############################################################################
###############################################################################
###############################################################################

############   IMPORTS AND GLOBAL VARIABLES AND GLOBAL FUNCTIONS  #############

from __future__ import division
import json, re, os, datetime, time, csv, traceback, operator, sys

starttime = datetime.datetime.now()
print '  Start time:'+str(time.strftime("%Y-%m-%d %H:%M"))

# defines global variables to be used throughout code
def globs():
    global tweet_count  # counts the number of tweets written to the file
    tweet_count = 0
    global tweets_checked   # counts the number of tweets it finds in the json files
    tweets_checked = 0
    global coords_found
    coords_found = 0
    global keywords # provides of dictionary of keywords to filter the tweets it checks
    keywords = {}
    global date_data
    date_data = {}
globs()

def clear():
    global tweet_count
    tweet_count = 0
    global tweets_checked
    tweets_checked = 0
    global keywords
    for kw in keywords.keys():
        keywords[kw] = 0    

def getCoords(data):
    try:    #attempts to get the coordinates from the tweet
        return data['coordinates']['coordinates']
    except: #if there are no coordinates then exception is called and make coords blank
        return ['','']

def checkCoords(coords):
    if coords[0] == '':
        return 1 #determines if a tweet has been written to the file
    else:
        return 0

def parseText(data):       
    try: text = data['text'].encode('unicode-escape')
    except: text = '[missing data]'
    text = re.sub('"', ' ["] ', text)
    text = re.sub(r'\\n', ' [RETURN] ', text)
    text = re.sub(r'\\r', ' [RETURN] ', text)
    text = re.sub(',', ' [COMMA] ', text)
    text = re.sub('&amp;', '&', text)  
    return text
    
def formatText(text):    
     kwtext = re.sub(',', ' ', text)
     kwtext = re.sub('\.', ' ', kwtext)
     kwtext = re.sub('\\\\', ' ', kwtext)
     kwtext = re.sub('\?', ' ', kwtext)
     kwtext = re.sub('!', ' ', kwtext)
     kwtext = re.sub('#', ' ', kwtext)
     kwtext = re.sub('@', ' ', kwtext)
     kwtext = re.sub('-', ' ', kwtext)
     kwtext = kwtext.lower()
     return kwtext

def writeToCSV(data, text, fn, count): 
    # Pull out various data from the tweets
    outfile = directory_out+str(datetime.datetime.today().strftime('%Y%m%d'))+'_'+fn[:14]+'_data.csv'   ######################### <--- update to be more descriptive
    #Collect data about the user:
    u_id = '\''+str(data['user']['id'])
    user = data['user']['screen_name'].encode('utf-8')
    try: utc_off = str(int(data['user']['utc_offset'])/3600)
    except TypeError: utc_off = ''
    created = data['user']['created_at']
    faves = str(data['user']['favourites_count'])
    followers = str(data['user']['followers_count'])
    following = str(data['user']['friends_count'])
    tweets = str(data['user']['statuses_count'])
    #tweet_favs = data['favorite_count']
    #Collect data about the tweet:
    t_id = '\''+data['id_str']
    try:
        t_id_rt = '\''+data['retweeted_status']['id_str']
        user_rt = data['retweeted_status']['user']['screen_name']
        #url_rt = 'http://twitter.com/'+user_rt+'/status/'+t_id_rt
        rt_count = data['retweeted_status']['retweet_count']
    except:
        t_id_rt = ''
        user_rt = ''
        #url_rt = ''
        rt_count = 0
    date = data['created_at']
    day = date[:3]
    yyyy = date[-4:]
    month = date[:7][-3:]
    dd = date[:10][-2:]
    hh = date[:13][-2:]
    mm = date[:16][-2:]
    ss = date[:19][-2:]
    url = 'http://twitter.com/'+str(data['user']['screen_name'].encode('utf-8'))+'/status/'+str(data['id_str'])
    #lc_text = text.lower()
    coords = getCoords(data)
    if coords != '':
        #print coords[0]
        global coords_found
        coords_found += 1                    
    #Append a row of data to file 
    #Append a row of data to file 
    with open(outfile,'a') as csvfile:      #appends tweets to the data.csv file
        saveFile = csv.writer(csvfile, delimiter=',', lineterminator='\n')        
        if count == 0:
            saveFile.writerow(['userID', 'username', 'retweet user', 'utc off', 'profile created',
                               'favorites', 'followers', 'following', 'tweets', 'date', 'tweetID',
                               'retweetID', 'retweet count', 'text', 'day', 'year', 'month', 'day', 
                               'hour', 'min', 'sec', 'url', 'lat', 'lon'])                    
        saveFile.writerow([u_id , user, user_rt, utc_off, created,
                           faves, followers, following, tweets, date, t_id, 
                           t_id_rt, rt_count, text, day, yyyy, month, dd, hh, mm, ss, url, coords[0], coords[1]])
    
def checkForKWs(kwtext):    
    kwFound = 0
    #print keywords
    for kw in keywords:     #for each keyword in the file
        if ' ' + kw + ' ' in kwtext:      #if the keyword is in the text
            keywords[kw] += 1             #add one to the keyword counter
            kwFound = 1
    return kwFound

def checkForNewEmoji(text):
    None
##     #checks if there is an emoji in the text 
##     find = re.compile('.U000.....')
##     if re.search(find, text):    
##         #tries to replace any emojis we know of with the text equivalent
##         for key, val in emoji:
##             text = re.sub(key, val, text)
##         text = re.sub(r'\\ \[',' [',text)
##         #checkes to see if any unknown emojis are in the text
##         if re.search(find, text):
##             l = text.split()    #splits the text into a list of strings
##             matches = [string for string in l if re.match(find, string)]    #gets a list of unknown emoji unicode
##             for string in matches:  #replaces any unknown emoji unicode
##                 text = re.sub(string , '[unknown_emoj]', text)
##                 text = text.replace("\\[", "[") 
##             with open('./emojilist0.csv', 'a') as f:    #appends the unknown unicode to the emoji list
##                 emoj = csv.writer(f, delimiter=',', lineterminator='\n')
##                 for string in matches:
##                     emoj.writerow(['U'+string.replace("\\U", "").lower()[:8] ,'[unknown_emoj]'])
##             while len(matches) != 0:   #resets the matches list
##                 matches.remove(matches[0]) 





#Dates:
    #only care about yyyymmdd
    #startDate <= endDate < today
#prompts the user for a start date to read tweets from
def startDate():
    startDate = int(input('Enter a Start Date (yyyymmdd) or 0 to run all the Tweet Data: '))
    if startDate == 0:
        return 20060321
    while startDate >= int(datetime.datetime.today().strftime('%Y%m%d')):
         print 'The Start Date must be before today (' + str(int(datetime.datetime.today().strftime('%Y%m%d'))) + ')'
         startDate = int(input('Enter a Start Date (yyyymmdd) or 0 to run all the Tweet Data: '))  
         if startDate == 0:
             return 20060321
    return startDate

def endDate(startDate):                    
    #gets and end date for the tweets to be filtered from
    endDate = 0
    if startDate == 20060321:
        endDate = int(datetime.datetime.today().strftime('%Y%m%d')) - 1
    elif startDate == 0:
        endDate = int(datetime.datetime.today().strftime('%Y%m%d')) - 1
    elif startDate == int(datetime.datetime.today().strftime('%Y%m%d')) - 1:
        endDate = startDate
    while endDate < startDate:
        endDate = int(input('Enter an End Date (yyyymmdd) that is greater than ' + str(startDate) + ' : '))
        if endDate >= int(datetime.datetime.today().strftime('%Y%m%d')): 
            print 'The End Date must be before today (' + str(int(datetime.datetime.today().strftime('%Y%m%d'))) + ')'
            endDate = 0 
    return endDate                          
                                         
                        
        
###############################################################################
###############################################################################
###############################################################################

#######   FILE PATH AND INITIALIZATION OF KEYWORDS DICTIONARY COUNT   #########

directory_in = '/pylon2/db4s82p/jcolditz/twitter/'   #path to all of the .json files
directory_out = '/pylon2/db4s82p/jcolditz/twitter/outfiles/'   #path to all of the .json files
#directory_in = 'C:/Users/gmtemp/Desktop/'   #path to all of the .json files
#directory_out = 'C:/Users/gmtemp/Desktop/'   #path to all of the .json files
files = sorted(os.listdir(directory_in))

#set up a path to the keywords file and pull them all into the keyword dictionary
with open('./keyword_dictionary.txt', 'r') as f:       #name of the dictionary file
    keywords = {}
    for line in f:
        if line.rstrip() not in keywords.keys():
            keywords.update({line.rstrip():0})   
    #print keywords
            
# Load the emoji conversion file 
with open('emojilist4.csv', 'rb') as f:       #with statement closes the directory automatically when the indentation ends
    reader = csv.reader(f)
    emoji = list(reader)
            
###############################################################################
###############################################################################
###############################################################################
            
#######################   SPECIALIZED FUNCTIONS   #############################

#opens the json file and separates out the tweets from it to be read by jsontocsv
def fixjson(directory_in, fn, coords_only, fileName):
    f = open(directory_in+'/'+fn) 
    data = f.read().replace('}{','},{')
    #data = data.replace('}{','},{')
    data2 = '{\"tweet\": ['+data+']}' #creates a list of tweets to be read
    try: record = json.loads(data2)
    except:
        print 'JSON did not parse normally - trying with "strict=False".' 
        try: 
            record = json.loads(data2, strict=False)
            #record = json.loads(data, strict=False)
        except: 
            traceback.print_exc()
            print 'JSON failed to parse!' 
            return 0
    f.close() #closes the file 
    jsontocsv(record, coords_only, fn, fileName)

#gets the data from the tweet and writes it to file
def jsontocsv(record, coords_only, fn, fileName):    
    count = 0    
    for data in record['tweet']:        #for each tweet get the text from it
        #parse the text so that it can be examined
        text = parseText(data)   
        kwtext = formatText(text)        
        global tweets_checked
        tweets_checked += 1 #increment the number of tweets checked        
        coords = getCoords(data)    #gets the coords from the tweet
        if coords_only == 1:    #do we only care about tweets with coords?
            printed = checkCoords(coords)   #if yes check to see if the tweet has coords
        else:
            printed = 0 #else print the tweet            
        if printed is 0:
            kwFound = checkForKWs(kwtext)
            if kwFound == 1:
                global tweet_count
                tweet_count += 1    #increment the count on the number of tweets printed
                writeToCSV(data, text, fn, count)
                count += 1
                #checkForNewEmoji(text)
    global date_data 
    if fn[:8] not in date_data: #fn[:8] is the date
        date_data.update({str(fn[:8]):{}})
        for key in keywords:
            date_data[fn[:8]].update({key:keywords[key]})
        #date_data[fn[:8]] is the dictionary associated with the date fn[:8]
        date_data[fn[:8]].update({'Tweets Hit':str(tweet_count)})
        date_data[fn[:8]].update({'Tweets Checked':str(tweets_checked)})
        #print date_data[fn[:8]]
    elif fn[:8] in date_data:
        for key in keywords:
            #print key + ":" + keywords[key]
            date_data[fn[:8]][key] += keywords[key]
        date_data[fn[:8]]['Tweets Hit'] += tweet_count
        date_data[fn[:8]]['Tweets Checked'] += tweets_checked
    clear()
    
###############################################################################
###############################################################################
###############################################################################

######################   MAIN PROGRAM OPERATOR   ##############################

def main(startDate, endDate, coords_only, fileName):          
    print '\nREADING TWEETS FROM ' + str(startDate) + ' to ' + str(endDate) +'\n'
    #read all the files in the directory
    t = str(time.time())
    for f in files:
        if f[-5:] =='.json':
            try:
                if int(f[:8]) >= startDate:
                    if int(f[:8]) <= endDate:
                        print 'Reading: '+str(f)
                        fn = f
                        fixjson(directory_in, fn, coords_only, fileName)
                        #print tweet_count, ' tweets written to file\n'
                    else: 
                        #print 'Bad date: '+str(f)
                        pass
            except:
                traceback.print_exc()
                print 'Invalid: '+str(f)
                
    with open('./keywordCount' + fileName +'.csv', 'wb') as csvfile:
        saveFile = csv.writer(csvfile, dialect='excel')
        words = ['Date']
        for word in keywords.keys():
            words.append(word)
        words.append('Tweets Hit')
        words.append('Tweets Checked')
        saveFile.writerow([word for word in words]) #this will print out the header
        global date_data
        sorted_dates = sorted(date_data.keys())
        for date in sorted_dates:
            words2 = [date[4:6] + '-' + date[6:] + '-' + date[:4]]
            for word in words:
                if word != 'Date':
                    words2.append(date_data[date][word])
            saveFile.writerow([word for word in words2])
            

    #print out all of the keyword information into a csv
    #print str(tweet_count)+' tweets written to file.'
    #with open('./keywordCount.csv','wb') as csvfile:     #prints out a sorted version of the keyword count       
        #sortedDict = sorted(keywords.items(), key=operator.itemgetter(1))
        #sortedDict = list(reversed(sortedDict))
        #saveFile = csv.writer(csvfile, delimiter=',')
        #saveFile.writerows(sortedDict)
        #saveFile.writerow(['coords found' , coords_found]) 
        #saveFile.writerow(['tweets hit' , tweet_count]) 
        #saveFile.writerow(['tweets checked' , tweets_checked]) 
        #if tweets_checked != 0:
            #saveFile.writerow(['tweets hit : tweets checked' , tweet_count / tweets_checked]) 
            #if tweet_count != 0:
                #saveFile.writerow(['kw hits : tweet hits' , kws_hit / tweet_count]) 
        #print sortedDict

###############################################################################
###############################################################################
###############################################################################

####################   COMMAND LINE ARGUMENT PARSER   #########################

args = len(sys.argv) #gets the number of command line arguments
    
################ CASE OF FOUR ARGS ###############
################ startDate = any date before today #############   Format: YYYYMMDD
################ endDate = date between startDate and today ####
################ coords_only = 0 or 1 #############
################ fileName = whatever your heart desires ########
startDate = int(sys.argv[1])
endDate = int(sys.argv[2])
coords_only = int(sys.argv[3])
fileName = str(sys.argv[4])
    
main(startDate, endDate, coords_only, fileName)

endtime = datetime.datetime.now()
print '    End time:'+str(time.strftime("%Y-%m-%d %H:%M"))
print 'Process time:'+str(endtime - starttime)