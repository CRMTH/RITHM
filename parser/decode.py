import json, re, csv, traceback

class decoder:

    _tweets_checked = 0
    _tweet_count = 0
    _tweet_infile = 0
    _date_data = {}

    def __init__ (self, keywords, dirIn, dirTemp, dirOut, 
                  hiMem, emojiFile):
        self.keywords = {}
        for kw in keywords.keys():
            self.keywords.update({kw.lower() : 0})
        #self.dirIn = dirIn
        self.dirTemp = dirTemp
        #self.dirOut = dirOut
        #self.hiMem = hiMem
        self.emojis = {}
        if emojiFile:
            with open(emojiFile, 'r') as f:
                reader = csv.reader(f)
                emoji_list = list(reader)
                for emoji in emoji_list:
                    self.emojis.update({emoji[0].lower() : emoji[1]})
        

    # This is the first thing that needs to be done!
    # This esentially cleans up each tweet in the json format and seperates them into their individual tweet data
    # It will return a list at the end containing all the tweets and their data
    def fixjson(self, dirIn, fileName, hiMem, emojiFile, *kargs):
        if hiMem:
            with open(dirIn+fileName, 'r') as f: 
                data = f.read().replace('}{','},{')
                data = '{\"tweet\": ['+data+']}' #creates a list of tweets to be read
                try: fixed = json.loads(data)
                except:
                    print('JSON did not parse normally - trying with "strict=False".')
                    try: 
                        fixed = json.loads(data, strict=False)
                    except: 
                        traceback.print_exc()
                        print('JSON failed to parse! - trying with "hiMem=False"') 
                        f.close()
                        decoder.fixjson(self, dirIn, fileName, hiMem=False, emojiFile=emojiFile)
                        return False
                f.close() #closes the file 
                decoder.jsontocsv(self, fixed, fileName, emojiFile, 
                                  hiMem=True)
                #return fixed

        else:
            with open(dirIn+fileName, 'r') as f:
                line = 0
                decoder._tweet_infile = 0
                reading = True
                while reading:
                    if line == 0:
                        tweet = ''
                    else:
                        tweet = '{'
                    while("}{" not in tweet):
                        chunk = f.readline()
                        tweet += chunk
                        if chunk == '':
                            tweet += '}}'
                            reading = False
                            break
                    tweet = tweet[:-2]
                    try:
                        dic = json.loads(tweet)
                        decoder.jsontocsv(self, dic, fileName, emojiFile,
                                          hiMem=False)
                    except:
                        continue
                    line += 1


        
    # This text the text portion of the tweet and formats it into a way that we can read it  
    def parseText(self, data):       
        
        try: text = data['extended_tweet']['full_text'] #REMEMBER TO UPDATE THIS
        except: 
            try: text = data['retweeted_status']['text']
            except:
                try: text = data['text']
                except: text = ''

        # Also include any quoted content
        try: quote = ' ..... "'+data['quoted_status']['text']+'"'
        except: quote = ''
        text = text+quote

        # Format common punctuation
        text = re.sub('`', "'", text)
        text = re.sub('&amp;', ' & ', text)
        text = re.sub('&gt;', ' > ', text)
        text = re.sub('&lt;', ' < ', text)
        text = re.sub(r'\(', ' ( ', text)
        text = re.sub(r'\)', ' ) ', text)
        text = re.sub(r'\[', ' ] ', text)
        text = re.sub(r'\[', ' ] ', text)
        text = re.sub(r'\"', ' " ', text)
        text = re.sub(r'\*', ' * ', text)
        text = re.sub(r'\-', ' - ', text)
        text = re.sub(r'\.', ' . ', text)
        text = re.sub(r'\!', ' ! ', text)
        text = re.sub(r'\?', ' ? ', text)
        text = re.sub(r'\:', ' : ', text)
        text = re.sub(r'\;', ' ; ', text)
        
        # Commas/returns/tabs get recoded because CSV output
        text = re.sub(r'\,0', '0', text) #Comma in common number
        text = re.sub(r'\,', ' ; ', text)
        text = re.sub(r'\n', ' --- ', text)
        text = re.sub(r'\r', ' --- ', text)
        text = re.sub(r'\t', ' ', text)

        # Repair hyperlinks
        text = re.sub(r' \: \/\/', '://', text)
        text = re.sub(r't . co', 't.co', text)


        # Formatting common Unicode punctuation
        text = str(text.encode("unicode-escape"))[2:-1].lower()
        text = text.replace('\\\\u2026' , ' ... ')
        text = text.replace('\\\\u2122' , ' ... ')
        text = text.replace('\\\\u2018' , "'")
        text = text.replace('\\\\u2019' , "'")
        text = text.replace("\\'" , "'")
        text = text.replace('\\\\u200d' , '')
        
        text = text.replace('\\\\u2014' , ' - ')
        text = text.replace('\\\\u' , ' \\\\u')

        while '  ' in text:
            text = text.replace('  ' , ' ')
        while '. .' in text:
            text = text.replace('. .' , '..')

        return text


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
        hit = 0
        for kw in self.keywords.keys():     #for each keyword in the file
            if (' '+ kw+' ') in (' '+kwtext+' '):      #if the keyword is in the text
                self.keywords[kw] += 1             #add one to the keyword counter
                #print(kwtext+'\n')
                hit = 1
            if kw[-1:]=='*':
                if (' '+ kw[:-1]) in (' '+kwtext):      #if the keyword is in the text
                    self.keywords[kw] += 1             #add one to the keyword counter
                    #print(kwtext+'\n')
                    hit = 1
        if '#' not in kw and ' ' not in kw:
            for kw in self.keywords.keys():     #for each keyword in the file
                if (' #'+ kw+' ') in (' '+kwtext+' '):      #if the keyword is in the text
                    self.keywords[kw] += 1             #add one to the keyword counter
                    hit = 1
                if kw[-1:]=='*':
                    if (' #'+ kw[:-1]) in (' '+kwtext):      #if the keyword is in the text
                        self.keywords[kw] += 1             #add one to the keyword counter
                        hit = 1
        if '@' not in kw and ' ' not in kw and '*' not in kw:
            for kw in self.keywords.keys():     #for each keyword in the file
                if (' #'+ kw+' ') in (' '+kwtext+' '):      #if the keyword is in the text
                    self.keywords[kw] += 1             #add one to the keyword counter
                    #print(kwtext+'\n')
                    hit = 1

        return hit


    def writeToCSV(self, data, text, fn, count):

        entities = []
        outfile = self.dirTemp+str(fn[:14]+'_data.csv')   ######################### <--- update to be more descriptive
        entities.append('\''+str(data['user']['id']))   #userID
        entities.append(data['user']['screen_name'])#.encode('utf-8')) #user
        try: entities.append(str(int(data['user']['utc_offset'])/3600)) #utc
        except TypeError: entities.append('') #utc
        entities.append(data['user']['created_at']) #created
        entities.append(str(data['user']['favourites_count'])) #faves
        entities.append(str(data['user']['followers_count'])) #followers
        entities.append(str(data['user']['friends_count'])) #following
        entities.append(str(data['user']['statuses_count'])) #tweets
        entities.append('\''+data['id_str']) #t_id
        try:
            entities.append('\''+data['retweeted_status']['id_str']) #t_id_rt
            entities.append(data['retweeted_status']['user']['screen_name']) #user_rt
            entities.append(data['retweeted_status']['retweet_count']) #rt_count
        except:
            entities.append('') #t_id_rt
            entities.append('') #user_rt
            entities.append(0) #rt_count
        entities.append(text) #text
        date = data['created_at']
        entities.append(date) #date
        entities.append('http://twitter.com/'+str(data['user']['screen_name'])+'/status/'+str(data['id_str'].strip('\''))) #url
        coords = decoder.getCoords(self, data)
        entities.append(coords[0]) #Lat
        entities.append(coords[1]) #Lon
        
        
        with open(outfile,'a') as csvfile:      
            saveFile = csv.writer(csvfile, delimiter=',', lineterminator='\n')        
            if count == 0:
                saveFile.writerow(['userID', 'username', 'utc off', 'profile created',
                                   'favorites', 'followers', 'following', 'tweets', 'tweetID',
                                   'retweetID', 'retweet user', 'retweet count', 
                                   'text', 'date', 'url', 'lat', 'lon'])                    
            saveFile.writerow([entity for entity in entities])


    # This needs to take in the record list from the fixjson function and this will split it all up into a happy format for the csv file
    def jsontocsv(self, record, fileName, emojiFile, hiMem):
        
        # This is used to control header rows in output
        if hiMem: 
            count = 0
        else: 
            count = decoder._tweet_infile
        
        # This is the main loop where all the tweets in the record get checked
        if hiMem:            
            for data in record['tweet']:        # This grabs each tweet one by one
                kwtext = decoder.parseText(self, data) # parse the text so that it can be examined
                decoder._tweets_checked += 1 #increment the number of tweets checked

                if decoder.checkForKWs(self, kwtext) == 1: #means that a keyword was found in the tweet
                    decoder._tweet_count += 1    #increment the count on the number of tweets printed
                    if emojiFile:
                        kwtext = decoder.emojify(self, kwtext)
                    decoder.writeToCSV(self, data, kwtext, fileName, count)
                    count += 1

        else:
            kwtext = decoder.parseText(self, record) # parse the text so that it can be examined
            decoder._tweets_checked += 1 #increment the number of tweets checked 

            if decoder.checkForKWs(self, kwtext) == 1: #means that a keyword was found in the tweet
                decoder._tweet_infile += 1
                decoder._tweet_count += 1    #increment the count on the number of tweets printed
                if emojiFile:
                    kwtext = decoder.emojify(self, kwtext)
                decoder.writeToCSV(self, record, kwtext, fileName, count)
