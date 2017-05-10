from __future__ import division
import json, re, os, datetime, time, csv, traceback, operator, sys

class decoder

	_tweet_count = 0
	_tweets_checked = 0
	_coords_found = 0
	_date_data = {}
	
	def __init__(self, keywords = {}):
		self.keywords = keywords
		
	def clear(self):
		self._tweet_count = 0
		self._tweets_checked = 0
		for kw in self.keywords.keys():
			self.keywords[kw] = 0  
	