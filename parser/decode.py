import json, re, csv, traceback

class decoder:

    _tweets_checked = 0
    _tweet_count = 0
    _tweet_infile = 0
    _date_data = {}

    def __init__ (self, keywords, dirIn, dirOut, 
                  hiMem, emojiFile):
        self.keywords = {}
        for kw in keywords.keys():
            self.keywords.update({kw.lower() : 0})
        #self.dirIn = dirIn
        #self.dirTemp = dirTemp
        self.dirOut = dirOut
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

        # This is a work in progress... 
        def lineparse(self, dirIn, fileName, emojiFile):
            count = 0
            tweet = ''


            def jsonline(line, tweet, status): #UPDATE THIS
                #tweet = ''

                if tweet[-1:] in ['[',']','{','}','(',')']:
                    end = False
                elif line[:1] in ['[',']','{','}','(',')']:
                    end = False
                else:
                    end = True

                if status in ['first','more']:
                    tweet = '{'
                    status = 'working'
                    
                elif line.strip() == '}{':
                    tweet = tweet + '}'
                    status = 'more'

                elif line.strip() == '}' and end:
                    tweet = tweet + '}'
                    status = 'done'
                                        
                else:
                    tweet = tweet+line.strip()
                    
                return [tweet, status]


            #count = decoder._tweet_infile
            with open(dirIn+fileName, 'r') as f:
                #decoder._tweet_infile = 0
                count = 0
                errors = 0
                j = ['','first']
                for line in f.readlines():
                    tweet = j[0]
                    status = j[1]
                    j = jsonline(line, tweet, status) ### FIX THIS TO CATCH FIRST TWEET
                    
                    if j[1] in ['more', 'done']:
                        tweet = j[0]
                        try:
                            dic = json.loads(tweet, strict=False)
                            kwtext = decoder.parseText(self, dic) # parse the text so that it can be examined
                            #decoder._tweets_checked += 1 #increment the number of tweets checked 
                
                            if decoder.checkForKWs(self, kwtext) == 1: #means that a keyword was found in the tweet
                                #decoder._tweet_infile += 1
                                #decoder._tweet_count += 1    #increment the count on the number of tweets printed
                                if emojiFile:
                                    kwtext = decoder.emojify(self, kwtext)
                                decoder.writeToCSV(self, dic, kwtext, fileName, count)
                                count += 1
                                if j[1] == 'done':
                                    f.close()
                                    return None
                                
                        except:
                            errors += 1
                            print('\n Count: '+str(count)+
                                  '\nErrors: '+str(errors)+
                                  '\nLength: '+str(len(tweet))+
                                  '\n')
                            if len(tweet) < 100:
                                print(tweet)
                            j = ['','more']
                            #print(tweet)
                            #traceback.print_exc()
                                                        
                            pass #break ### Point Break when testing
                f.close()
                return None
            

        # hiMem is preffered, when working memory permits
        if hiMem:
            count = 0
            with open(dirIn+fileName, 'r') as f: 
                data = f.read().replace('}{','},{')
                data = r'{"tweet": ['+data+']}' #creates a list of tweets to be read
                try: 
                    fixed = json.loads(data, strict=False)
                    f.close() #closes the file 
                    for data in fixed['tweet']: # This grabs each tweet one by one
                        kwtext = decoder.parseText(self, data) # parse the text so that it can be examined
                        decoder._tweets_checked += 1 #increment the number of tweets checked
        
                        if decoder.checkForKWs(self, kwtext) == 1: #means that a keyword was found in the tweet
                            decoder._tweet_count += 1    #increment the count on the number of tweets printed
                            if emojiFile:
                                kwtext = decoder.emojify(self, kwtext)
                            decoder.writeToCSV(self, data, kwtext, fileName, count)
                            count += 1
                    
                except: 
                    traceback.print_exc()
                    print(fileName+' : JSON failed to parse! - trying with "hiMem=False"') 
                    f.close()
                    try:
                        decoder.fixjson(self, dirIn, fileName, hiMem=False, emojiFile=emojiFile)
                    except:
                        traceback.print_exc()
                        pass
                    return False
                    f.close()
                #return fixed

        else:
            lineparse(self, dirIn, fileName, emojiFile)


        
    # This text the text portion of the tweet and formats it into a way that we can read it  
    def parseText(self, data):       
        
        # Try for extended text of original tweet, if RT'd
        try: text = data['retweeted_status']['extended_tweet']['full_text']
        except: 
            # Try for extended text of an original tweet
            try: text = data['extended_tweet']['full_text']
            except:
                # Try for basic text of original tweet if RT'd 
                try: text = data['retweeted_status']['text']
                except:
                    # Try for basic text of an original tweet
                    try: text = data['text']
                    # Nothing left to check for
                    except: text = ''

        # Maintain the RT moniker at the beginning 
        try: 
            if data['retweeted_status']['text']:
                try: rt = data['text'].split(':')[0]+' : '
                except: rt = ''
                text = rt+text
        except: pass

        # Also include any quoted content
        try: quote = ' ..... "'+data['quoted_status']['extended_tweet']['full_text']+'"'
        except: 
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
        text = re.sub(r'\[', ' [ ', text)
        text = re.sub(r'\]', ' ] ', text)
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

        # Repair quote on rt
        #text = re.sub(r'\"rt', 'rt', text)


        # Formatting common Unicode punctuation
        text = str(text.encode("unicode-escape"))[2:-1].lower()
        text = text.replace('\\\\u2026' , ' ... ')
        text = text.replace('\\\\u2122' , ' ... ')
        text = text.replace('\\\\u2018' , "'")
        text = text.replace('\\\\u2019' , "'")
        text = text.replace('\\\\u201c' , '"')
        text = text.replace('\\\\u201d' , '"')
        text = text.replace("\\'" , "'")
        text = text.replace('\\\\u200d' , '')
        
        text = text.replace('\\\\u2014' , ' - ')
        text = text.replace('\\\\u' , ' \\\\u')

        # Formatting punctuation oddities
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
        outfile = self.dirOut+str(fn[:14]+'_data.csv')   ######################### <--- update to be more descriptive
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
