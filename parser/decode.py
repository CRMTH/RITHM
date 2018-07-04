# -*- coding: utf-8 -*-

import json, csv, traceback
import parselogic

class decoder:

    # MAY WANT TO INPUT SOME OF THESE ARGUMENTS W/IN A DICTIONARY?
    def __init__ (self, keywords, dirIn, dirOut, 
                  hiMem, mode, lcase, emoji, logging):
        self.keywords = []
        for kw in keywords:
            self.keywords.append(kw)
        self.dirOut = dirOut
        self.mode = mode
        self.lcase = lcase
        self.emoji = emoji
        self.logging = logging
        
        self.n_tweets = 0
        self.n_matches = 0
        self.n_errors = 0
        
        #self.emojis = {}
        #if emojiFile:
        #    with open(emojiFile, 'r') as f:
        #        reader = csv.reader(f)
        #        emoji_list = list(reader)
        #        for emoji in emoji_list:
        #            self.emojis.update({emoji[0].lower() : emoji[1]})
        



    # This cleans the JSON format and seperates into individual tweet data
    # It will return a list of tweets
    def fixjson(self, dirIn, fileName, hiMem, *kargs):

        # This is always a work in progress... 
        def lineparse(self, dirIn, fileName):
            count = 0
            tweet = ''


            def jsonline(line, tweet, status): #UPDATE THIS?
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


            with open(dirIn+fileName, 'r', encoding='utf-8') as f:
                count = 0
                errors = 0
                j = ['','first']
                for line in f.readlines():
                    tweet = j[0]
                    status = j[1]
                    j = jsonline(line, tweet, status) ### FIX THIS TO CATCH FIRST TWEET?
                    
                    if j[1] in ['more', 'done']:
                        tweet = j[0]
                        try:
                            dic = json.loads(tweet, strict=False)
                            #kwtext = decoder.parseText(self, dic) # parse the text so that it can be examined
                            parsed_text = decoder.parseText(self, dic) # parse the text so that it can be examined
                            parsed_quote = decoder.parseQuote(self, dic) # parse the text so that it can be examined
                            kwtext = parsed_text+' '+parsed_quote
                            self.n_tweets += 1
                            if decoder.checkForKWs(self, kwtext) == True: #means that a keyword was found in the tweet
                                #if emojiFile:
                                #    kwtext = decoder.emojify(self, kwtext)
                                decoder.writeToCSV(self, dic, parsed_text, parsed_quote, fileName, count)
                                count += 1
                                if j[1] == 'done':
                                    f.close()
                                    print('DONE\n')
                                    return None
                                
                        except:
                            errors += 1
                            #print('\n Count: '+str(count)+
                            #      '\nErrors: '+str(errors)+
                            #      '\nLength: '+str(len(tweet))+
                            #      '\n')
                            #if len(tweet) < 100:
                            #    print(tweet)
                            j = ['','more']
                            #print(tweet)
                            print('CRITICAL PARSING ERROR?!')
                            traceback.print_exc() #############
                                                        
                            pass #break ### Point Break when testing
                f.close()
                return None
            

        # hiMem is preffered, when working memory permits
        if hiMem:
            self.n_tweets = 0
            count = 0
            with open(dirIn+fileName, 'r', encoding='utf-8') as f: 
                data = f.read().replace('}{','},{')
                data = r'{"tweet": ['+data+']}' #creates a list of tweets to be read
                try: 
                    fixed = json.loads(data, strict=False)
                    f.close() #closes the file 
                    for data in fixed['tweet']: # This grabs each tweet one by one
                        self.n_tweets += 1
                        parsed_text = decoder.parseText(self, data) # parse the text so that it can be examined
                        parsed_quote = decoder.parseQuote(self, data) # parse the text so that it can be examined
                        kwtext = parsed_text+' '+parsed_quote
                        #decoder._tweets_checked += 1 #increment the number of tweets checked
                        if decoder.checkForKWs(self, kwtext) == True: #means that a keyword was found in the tweet
                            #decoder._tweet_count += 1    #increment the count on the number of tweets printed
                            #if emojiFile:
                            #    kwtext = decoder.emojify(self, kwtext)
                            decoder.writeToCSV(self, data, parsed_text, parsed_quote, fileName, count)
                            count += 1
                    
                except: 
                    #traceback.print_exc()
                    self.n_tweets = 0
                    print(fileName+' : HiMem failed! Trying with LoMem...') 
                    f.close()
                    try:
                        decoder.fixjson(self, dirIn, fileName, hiMem=False)
                    except:
                        print(fileName+' : LoMem also failed! See exception.') 
                        traceback.print_exc()
                        pass
                    return False
                    #f.close()
                #return fixed

        else:
            lineparse(self, dirIn, fileName)


        
    # This loads the most comprehensive text portion of the tweet  
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
                    except: 
                        # Nothing left to check for
                        text = ''
                        self.n_errors += 1
                        #print(data)  ##### These appear to be streamer errors ######
                        ############## THIS COULD BE IMPORTANT!

        # Run parselogic.reformat 
        #text = parselogic.reformat(text)

        
        text = str(text.encode('unicode-escape'))[2:-1]
        return text


    # This loads the most comprehensive quote portion of the tweet  
    def parseQuote(self, data):       

        # Try for extended text of quote
        try: quote = data['quoted_status']['extended_tweet']['full_text']
        except: 
            # Try for basic text of quote
            try: quote = data['quoted_status']['text']
            except: 
                # Nothing left to check for
                quote = ''
                #print('parseQuote FAIL')

        #if len(quote)>0:
        #    quote = parselogic.reformat(quote)
        
        quote = str(quote.encode('unicode-escape'))[2:-1]
        return quote


    # Goes through each keyword in the decoder and checks if it is in the tweet
    # If there is no keyword then return a 0 to skip over the tweet
    def checkForKWs(self, kwtext):
        hit = False
        formattedtext = parselogic.reformat(kwtext, mode=4.5,
                                            lcase=True, emoji=None)
        for kw in self.keywords:
            if parselogic.match(kw, formattedtext):
                hit = True
                self.n_matches += 1
                break # DOES THIS WORK TO SAVE PROCESSING?
        return hit


    # Grabs the coordinates from the tweet
    # If the tweet has no coordinates it just leaves it empty
    def getCoords(self, data):
        try:    #attempts to get the coordinates from the tweet
            return data['coordinates']['coordinates']
        except: #if there are no coordinates then exception is called and make coords blank
            return ['','']


    # THIS COULD USE A TEMPLATE FILE FOR BETTER PORTABILITY
    def writeToCSV(self, data, parsed_text, parsed_quote, fn, count):

        entities = []
        outfile = self.dirOut+str(fn[:14]+'_data.csv')   # DOCUMENT THIS
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
        text = parselogic.reformat(parsed_text, mode=1.5, lcase=self.lcase, emoji=self.emoji)
        entities.append(text) #text
        quote = parselogic.reformat(parsed_quote, mode=1.5, lcase=self.lcase, emoji=self.emoji)
        entities.append(quote) #text
        date = data['created_at']
        entities.append(date) #date
        entities.append('http://twitter.com/'+str(data['user']['screen_name'])+'/status/'+str(data['id_str'].strip('\''))) #url
        coords = decoder.getCoords(self, data)
        entities.append(coords[0]) #Lat
        entities.append(coords[1]) #Lon
        
        ### UPDATE TO REMOVE csv.writer DEPENDENCY
        with open(outfile, 'a') as csvfile:      
            saveFile = csv.writer(csvfile, delimiter=',', lineterminator='\n')        
            if count == 0:
                saveFile.writerow(['userID', 'username', 'utc off', 'profile created',
                                   'favorites', 'followers', 'following', 'tweets', 'tweetID',
                                   'retweetID', 'retweet user', 'retweet count', 
                                   'text', 'quote', 'date', 'url', 'lat', 'lon'])                    
            saveFile.writerow([entity for entity in entities])


