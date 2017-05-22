import json, re, datetime, csv, unicodedata, sys, base64

class decoder:

    _tweets_checked = 0
    _tweet_count = 0
    _date_data = {}

    def __init__ (self, keywords, dirOut, directory, dirTemp, emojify, emoji_file):
        self.keywords = {}
        for kw in keywords.keys():
            self.keywords.update({kw.lower() : 0})
        self.dirOut = dirOut
        self.directory = directory
        self.dirTemp = dirTemp
        self.emojis = {}
        if emojify == 1:
            with open(directory + emoji_file, 'r') as f:
                reader = csv.reader(f)
                emoji_list = list(reader)
                for emoji in emoji_list:
                    self.emojis.update({emoji[0].lower() : emoji[1]})
        

    # This is the first thing that needs to be done!
    # This esentially cleans up each tweet in the json format and seperates them into their individual tweet data
    # It will return a list at the end containing all the tweets and their data
    def fixjson(self, dirIn, fileName):
        with open(dirIn+'/'+fileName, 'r') as f: 
            data = f.read().replace('}{','},{')
            data2 = '{\"tweet\": ['+data+']}' #creates a list of tweets to be read
            try: record = json.loads(data2)
            except:
                print('JSON did not parse normally - trying with "strict=False".')
                try: 
                    record = json.loads(data2, strict=False)
                except: 
                    traceback.print_exc()
                    print('JSON failed to parse!') 
                    return 0
            f.close() #closes the file 
            return record
        
    # This text the text portion of the tweet and formats it into a way that we can read it  
    def parseText(self, data):       
        try: text = data['text']
        except: text = '[missing data]'
        #text = unicodedata.encode('ascii', 'ignore')
        text = re.sub('"', ' ["] ', text)
        text = re.sub(r'\\n', ' [RETURN] ', text)
        text = re.sub(r'\\r', ' [RETURN] ', text)
        text = re.sub(',', ' [COMMA] ', text)
        text = re.sub('&amp;', '&', text)
        text = re.sub('\\\\', ' ', text)
        return str(text.encode("unicode-escape"))[2:-1].lower()

    def emojify(self, text):
        if '\\u' in text:
            text = text.replace('\\\\u' , ' \\\\u')
            words = text.split()
            for word in words:
                if '\\u' in word:
                    if word in self.emojis.keys():
                            words[words.index(word)] = self.emojis[word]
            return ' '.join(words)
        return text

    # This clears the counters for everything
    # Used to gather data on each individual day
    def clear(self):
        self._tweet_count = 0
        self._tweets_checked = 0
        for kw in self.keywords.keys():
            self.keywords[kw] = 0   

    # Grabs the coordinates from the tweet
    # If the tweet has no coordinates it just leaves it empty
    def getCoords(self, data):
        try:    #attempts to get the coordinates from the tweet
            return data['coordinates']['coordinates']
        except: #if there are no coordinates then exception is called and make coords blank
            return ['','']

    # Goes through each keyword in the decoder and checks if it is in the tweet
    # If a keyword is in the tweet it will return a 1 so it knows it is to print the tweet in the csv file
    # If there is no keyword then return a 0 to skip over the tweet
    def checkForKWs(self, kwtext):    
        for kw in self.keywords.keys():     #for each keyword in the file
            if ' ' + kw + ' ' in kwtext:      #if the keyword is in the text
                self.keywords[kw] += 1             #add one to the keyword counter
                return 1
        return 0


    def writeToCSV(self, data, text, fn, count): 

        outfile = self.dirTemp+str(fn[:14]+'_data.csv')   ######################### <--- update to be more descriptive
        u_id = '\''+str(data['user']['id'])
        user = data['user']['screen_name'].encode('utf-8')
        try: utc_off = str(int(data['user']['utc_offset'])/3600)
        except TypeError: utc_off = ''
        created = data['user']['created_at']
        faves = str(data['user']['favourites_count'])
        followers = str(data['user']['followers_count'])
        following = str(data['user']['friends_count'])
        tweets = str(data['user']['statuses_count'])
        t_id = '\''+data['id_str']
        try:
            t_id_rt = '\''+data['retweeted_status']['id_str']
            user_rt = data['retweeted_status']['user']['screen_name']
            rt_count = data['retweeted_status']['retweet_count']
        except:
            t_id_rt = ''
            user_rt = ''
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
        coords = decoder.getCoords(self, data)
        
        with open(outfile,'a') as csvfile:      
            saveFile = csv.writer(csvfile, delimiter=',', lineterminator='\n')        
            if count == 0:
                saveFile.writerow(['userID', 'username', 'retweet user', 'utc off', 'profile created',
                                   'favorites', 'followers', 'following', 'tweets', 'date', 'tweetID',
                                   'retweetID', 'retweet count', 'text', 'day', 'year', 'month', 'day', 
                                   'hour', 'min', 'sec', 'url', 'lat', 'lon'])                    
            saveFile.writerow([u_id , user, user_rt, utc_off, created,
                               faves, followers, following, tweets, date, t_id, 
                               t_id_rt, rt_count, text , day, yyyy, month, dd, hh, mm, ss, url, coords[0], coords[1]])


    # This needs to take in the record list from the fixjson function and this will split it all up into a happy format for the csv file
    def jsontocsv(self, record, fileName, coords_only, emojify):
        
        count = 0    # This is only needed to see when it is the first tweet in the list and the csv file will make a header before writing the tweet

        # This is the main loop where all the tweets in the record get checked
        for data in record['tweet']:        # This grabs each tweet one by one           
            kwtext = decoder.parseText(self, data) # parse the text so that it can be examined
            decoder._tweets_checked += 1 #increment the number of tweets checked

            printed = 0
            coords = decoder.getCoords(self, data)    #gets the coords from the tweet
            if coords_only == 1:    #do we only care about tweets with coords?
                if coords[0] == '':
                    printed = 1 #determines if a tweet has been written to the file
            if printed == 0:        
                if decoder.checkForKWs(self, kwtext) == 1: #means that a keyword was found in the tweet
                    decoder._tweet_count += 1    #increment the count on the number of tweets printed
                    if emojify == 1:
                        kwtext = decoder.emojify(self, kwtext)
                    decoder.writeToCSV(self, data, kwtext, fileName, count)
                    count += 1

        # This is the second loop where the data from the day file is checked and written to a csv file
        if fileName[:8] not in self._date_data: #fn[:8] is the date
            self._date_data.update({str(fileName[:8]):{}})
            for key in self.keywords:
                self._date_data[fileName[:8]].update({key:self.keywords[key]})
            #date_data[fn[:8]] is the dictionary associated with the date fn[:8]
            self._date_data[fileName[:8]].update({'Tweets Hit':str(self._tweet_count)})
            self._date_data[fileName[:8]].update({'Tweets Checked':str(self._tweets_checked)})
            #print date_data[fn[:8]]
        elif fileName[:8] in self._date_data:
            for key in self.keywords:
                #print key + ":" + keywords[key]
                self._date_data[fileName[:8]][key] += self.keywords[key]
            self._date_data[fileName[:8]]['Tweets Hit'] += self._tweet_count
            self._date_data[fileName[:8]]['Tweets Checked'] += self._tweets_checked

        decoder.clear(self) #clears the data from that day
