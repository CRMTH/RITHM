# -*- coding: utf-8 -*-

import json, csv, traceback
import parselogic

class decoder:

    # MAY WANT TO INPUT SOME OF THESE ARGUMENTS W/IN A DICTIONARY?
    def __init__ (self, keywords, dirIn, dirOut,
                  hiMem, mode, lcase, emoji, logging,
                  yesterday_dict, today_dict, out_extension='.tsv'):             #Update parser.csv to set extension
        self.keywords = []
        for kw in keywords:
            self.keywords.append(kw)
        self.dirOut = dirOut
        self.mode = mode
        self.lcase = lcase
        self.logging = logging
        
        self.n_tweets = 0
        self.n_matches = 0
        self.n_warnings = 0
        self.n_errors = 0

        self.out_extension=out_extension
        
        #Dictionaries to keep track of duplicate tweet IDs over all parsed files - logging
        self.yesterday_dict = yesterday_dict
        self.today_dict = today_dict

        self.emojis = {}
        if emoji is not None:
            with open(emoji, 'r') as emoji_file:
                for line in emoji_file:
                    unic = line.split(',')[0].lower()
                    trans = line.split(',')[1]
                    self.emojis[unic] = trans

    # This cleans the JSON format and seperates into individual tweet data
    # It will return a list of tweets
    def fixjson(self, dirIn, fileName, hiMem, *kargs):

        # This is always a work in progress... 
        def lineparse(self, dirIn, fileName):
            count = 0
            tweet = ''


            def jsonline(line, tweet, status): #UPDATE THIS?

                #if tweet[-1:] in ['[',']','{','}','(',')']:
                #    end = False
                #elif line[:1] in ['[',']','{','}','(',')']:
                #    end = False
                #else:
                #    end = True

                if status == 'first':
                    tweet = '{'
                    status = 'working'

                elif status == 'more':
                    tweet = '{'+line.strip()
                    status = 'working'
                    
                elif line.strip() == '}{':
                    tweet = tweet + '}'
                    status = 'more'

                #elif line.strip() == '}' and end:
                #    tweet = tweet + '}'
                #    status = 'done'
                                        
                else:
                    tweet = tweet+line.strip()
                    
                return [tweet, status]


            with open(dirIn+fileName, 'r', encoding='utf-8') as f:
                count = 0
                #errors = 0
                j = ['','first']
                for line in f.readlines():
                    tweet = j[0]
                    status = j[1]
                    #j = jsonline(line, tweet, status) ### 
                    
                    if j[1] in ['more', 'done']:
                        tweet = j[0]
                        try:
                            dic = json.loads(tweet, strict=False)
                            parsed_text = decoder.parseText(self, dic) # Parse the text so that it can be examined
                            parsed_quote = decoder.parseQuote(self, dic) # Parse the quote so that it can be examined
                            kwtext = parsed_text+' '+parsed_quote
                            self.n_tweets += 1
                            if decoder.checkForKWs(self, kwtext) == True: # Means that a keyword was found in the tweet
                                try: 
                                    tweetid = ('\''+dic['id_str'])
                                except:
                                    try: tweetid = ('\''+str(dic['id'])) # t_id
                                    except: tweetid = '\''
                                if tweetid in self.yesterday_dict:
                                    self.yesterday_dict[tweetid] += 1
                                elif tweetid in self.today_dict:
                                    self.today_dict[tweetid] += 1
                                else:
                                    self.today_dict[tweetid] = 1
                                    decoder.writeToCSV(self, dic, parsed_text, parsed_quote, fileName, count)
                                    count += 1
                                #if j[1] == 'done':
                                #    f.close()
                                #    print('DONE\n')
                                #    return None

                        #except ValueError:
                        #    self.n_errors += 1
                        #    j = ['','more'] ### THIS NEEDS UPDATING?
                        #    pass
                        
                        except:
                            ### These can be un-commented if you are trying to diagnose errors
                            ### FUTURE: incorporate error logging here
                            #print(j[0])
                            #print('\n Count: '+str(count)+
                            #      '\nErrors: '+str(errors)+
                            #      '\nLength: '+str(len(tweet))+
                            #      '\n')
                            #if len(tweet) < 100: # This catches Twitter API hiccups
                            #    print(tweet)
                            #print(tweet) 
                            #traceback.print_exc() # This is the most helpful info to print
                            self.n_errors += 1
                            j = ['','more'] ### 
                            #break ### Break here when diagnosing errors
                    j = jsonline(line, tweet, status) # The last tweet will be ignored.

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
                            try: 
                                tweetid = ('\''+data['id_str'])
                            except:
                                try: tweetid = ('\''+str(data['id'])) # t_id
                                except: tweetid = '\''
                            if tweetid in self.yesterday_dict:
                                self.yesterday_dict[tweetid] += 1
                            elif tweetid in self.today_dict:
                                self.today_dict[tweetid] += 1
                            else:
                                self.today_dict[tweetid] = 1
                                decoder.writeToCSV(self, data, parsed_text, parsed_quote, fileName, count)
                                count += 1
                    
                except: 
                    traceback.print_exc()
                    self.n_tweets = 0
                    self.today_dict = {}
                    print('\n'+fileName+' : HiMem failed! Trying with LoMem...') 
                    f.close()
                    try:
                        decoder.fixjson(self, dirIn, fileName, hiMem=False)
                    except:
                        print('\n'+fileName+' : LoMem failed! See exception.') 
                        traceback.print_exc()
                        pass
                    return False

        else:
            lineparse(self, dirIn, fileName)


        
    # This loads the most comprehensive text portion of the tweet  
    def parseText(self, data):       
        # Try for extended text of original tweet, if RT'd (streamer)
        try: text = data['retweeted_status']['extended_tweet']['full_text']
        except: 
            # Try for extended text of an original tweet, if RT'd (REST API)
            try: text = data['retweeted_status']['full_text']
            except:
                # Try for extended text of an original tweet (streamer)
                try: text = data['extended_tweet']['full_text']
                except:
                    # Try for extended text of an original tweet (REST API)
                    try: text = data['full_text']
                    except:
                        # Try for basic text of original tweet if RT'd 
                        try: text = data['retweeted_status']['text']
                        except:
                            # Try for basic text of an original tweet
                            try: text = data['text']
                            except: 
                                # Nothing left to check for
                                text = ''
                                self.n_warnings += 1
                                #print(data)  ##### These appear to be streamer errors ######

        #text = str(text.encode('unicode-escape'))[2:-1] # REM 20190423 (moved to parselogic.py)
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

        #quote = str(quote.encode('unicode-escape'))[2:-1]  # REM 20190423
        return quote


    # Goes through each keyword in the decoder and checks if it is in the tweet
    # If there is no keyword then return a 0 to skip over the tweet
    def checkForKWs(self, kwtext):
        hit = False
        formattedtext = parselogic.reformat(kwtext, self.emojis, mode=4.5,
                                            lcase=True)
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

    def getPolygonCoords(self, data):
        try:
            coords = data['place']['bounding_box']['coordinates']
            lat = 0
            lon = 0
            for i in range(len(coords[0])):
                lat += coords[0][i][1]
                lon += coords[0][i][0]
            lat = lat/len(coords[0])
            lon = lon/len(coords[0])
            return [str(lat), str(lon)]
        except:
            return ['', '']

    # THIS COULD USE A TEMPLATE FILE FOR BETTER PORTABILITY
    def writeToCSV(self, data, parsed_text, parsed_quote, fn, count):

        entities = []

        outfile = self.dirOut+str(fn[:14]+'_data'+self.out_extension)   # Changed from .csv to .tsv (20180716 JC)

        ###################
        ### User-level data
        ###################

        entities.append('\''+str(data['user']['id']))   # u_id

        entities.append(data['user']['screen_name'])#.encode('utf-8')) # u_handle

        if data['user']['name']:
            name = parselogic.reformat(data['user']['name'], self.emojis, mode=1.0, lcase=self.lcase)
            entities.append(name)#.encode('utf-8')) # u_name
        else: entities.append('') 

        if data['user']['description']:
            desc = parselogic.reformat(data['user']['description'], self.emojis, mode=self.mode, lcase=self.lcase)
            entities.append(desc)#.encode('utf-8')) # u_desc
        else: entities.append('') 

        try: entities.append(data['user']['url']) # u_url
        except: entities.append('') 

        try: created = parselogic.ts(data['user']['created_at'], format=True) #########
        except: created = data['user']['created_at']
        entities.append(created) # u_create

        entities.append(str(data['user']['statuses_count'])) #u_tweets
        entities.append(str(data['user']['friends_count'])) # u_fo_out
        entities.append(str(data['user']['followers_count'])) # u_fo_in
        entities.append(str(data['user']['favourites_count'])) # u_likes

        #Deprecated
        try: entities.append(str(int(data['user']['utc_offset'])/3600))
        except: entities.append('')

        try: 
            loc = parselogic.reformat(data['user']['location'], self.emojis, mode=self.mode, lcase=self.lcase)
            entities.append(loc)
        except: entities.append('') 
        #Deprecated
        if str(data['user']['geo_enabled']) == 'true':
            entities.append(1) # u_geotag
        else: entities.append(0) # u_geotag

        try: entities.append(data['user']['lang']) # u_lang
        except: entities.append('') 

        try: entities.append(data['user']['profile_image_url']) # u_imgurl
        except: entities.append('') 

        try: entities.append(data['user']['profile_banner_url']) # u_bgurl
        except: entities.append('') 

        if str(data['user']['protected']) == 'true':
            entities.append(1) # u_privat
        else: entities.append(0) # u_privat

        if str(data['user']['verified']) == 'true':
            entities.append(1) # u_verify
        else: entities.append(0) # u_verify

        # placeholder for tracking number of captured tweets / user
        entities.append('') # u_n_capt

        ####################
        ### Tweet-level data
        ####################

        try: 
            t_id = ('\''+data['id_str'])
        except:
            try: t_id = ('\''+str(data['id'])) # t_id
            except: t_id = '\''
        entities.append(t_id) # t_id

        text = parselogic.reformat(parsed_text, self.emojis, mode=self.mode, lcase=self.lcase)
        entities.append(text) # t_text

        quote = parselogic.reformat(parsed_quote, self.emojis, mode=self.mode, lcase=self.lcase)
        entities.append(quote) # t_quote

        entities.append('http://twitter.com/'+str(data['user']['screen_name'])+'/status/'+t_id.strip('\'')) # t_url

        try: date = parselogic.ts(data['created_at'], format=True) ##########
        except: date = data['created_at']
        entities.append(date) # t_date

        coords = decoder.getCoords(self, data)
        coords_str = str(coords[1])+' '+str(coords[0])
        entities.append(coords_str) # t_geolat t_geolon

        poly_coords = decoder.getPolygonCoords(self, data)
        entities.append(poly_coords[0]+' '+poly_coords[1])

        try: place =  parselogic.reformat(data['place']['full_name'], self.emojis, mode=1.0, lcase=self.lcase)
        except: place = ''
        entities.append(place) # t_place


        try: lang =  data['lang'] 
        except: lang = ''
        entities.append(lang) # t_lang

        try:
            entities.append('\''+data['in_reply_to_status_id_str']) # re_t_tid
            entities.append('\''+data['in_reply_to_user_id_str']) # re_u_id
        except:
            entities.append('') # re_t_id
            entities.append('') # re_u_id

        try: entities.append('\''+data['quoted_status']['id_str']) # qu_t_tid
        except: entities.append('')

        try: entities.append('\''+data['quoted_status']['user']['id_str']) # qu_u_id
        except: entities.append('')
        try: entities.append(data['quoted_status']['retweet_count']) # qu_n_rt
        except: entities.append('')
        try: entities.append(data['quoted_status']['favorite_count']) # qu_n_fav
        except: entities.append('')
        try: entities.append(data['quoted_status']['reply_count']) # qu_n_rep
        except: entities.append('')
        try: entities.append(data['quoted_status']['quote_count']) # qu_n_quo
        except: entities.append('')
        try: entities.append('\''+data['retweeted_status']['id_str']) # rt_t_tid
        except: entities.append('')
        try: entities.append('\''+data['retweeted_status']['user']['id_str']) # rt_u_id
        except: entities.append('')
        try: entities.append(data['retweeted_status']['retweet_count']) # rt_n_rt
        except: entities.append('')
        try: entities.append(data['retweeted_status']['favorite_count']) # rt_n_fav
        except: entities.append('')
        try: entities.append(data['retweeted_status']['reply_count']) # rt_n_rep
        except: entities.append('')
        try: entities.append(data['retweeted_status']['quote_count']) # rt_n_quo
        except: entities.append('')

        #Added for age prediction modelling
        if str(data['user']['default_profile']).lower() == 'true':
            entities.append(1)
        else:
            entities.append(0)

        if str(data['user']['default_profile_image']).lower() == 'true':
            entities.append(1)
        else:
            entities.append(0)

        try: entities.append(data['user']['listed_count']) # u_utcoff
        except: entities.append('') 

        try: entities.append(len(data['entities']['hashtags']))
        except: entities.append('')

        try: entities.append(len(data['entities']['urls']))
        except: entities.append('')

        try: entities.append(len(data['entities']['user_mentions']))
        except: entities.append('')

        try:
            media_list = data['extended_entities']['media'] 
            entities.append(len(media_list))
        except: entities.append(0)

        
        ### Might want to update to csv.writer dependency? 
        with open(outfile, 'a', encoding='utf-8') as csvfile:      
            saveFile = csv.writer(csvfile, delimiter='\t', lineterminator='\n')        
            if count == 0:


                saveFile.writerow(['u_id', 'u_handle', 'u_name', 
                                   'u_desc', 'u_url', 'u_create',
                                   'u_tweets', 'u_fo_out', 'u_fo_in', 'u_likes', 'u_utcoff',
                                   'u_locate', 'u_geotag', 'u_lang', 'u_imgurl', 'u_bgurl',
                                   'u_privat', 'u_verify', 'u_n_capt',
                                   't_id', 't_text', 't_quote', 't_url', 
                                   't_date', 't_geopoint', 't_geopoly',
                                   't_place', 't_lang', 
                                   're_t_id', 're_u_id',
                                   'qu_t_id', 'qu_u_id', 
                                   'qu_n_qu', 'qu_n_re', 'qu_n_rt', 'qu_n_fav',
                                   'rt_t_tid', 'rt_u_id', 
                                   'rt_n_qu', 'rt_n_re', 'rt_n_rt', 'rt_n_fav',
                                   'u_profile', 'u_profile_img', 'u_list',
                                   't_hashtags', 't_urls', 't_mentions', 't_media'])
    
            saveFile.writerow([entity for entity in entities])


