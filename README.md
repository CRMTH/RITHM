## Real-time Infoveillance of Twitter Health Messages (RITHM)
__[Center for Research on Media, Technology, and Health](http://mth.pitt.edu/)__

_This is the future home of documentation for installing and utilizing the RITHM framework to retrieve and parse Twitter Streaming API data for public health research. An associated mauscript is currently under development and this repository will continue to be updated in parallel._

### _RITHM streamer_
The [streamer](https://github.com/CRMTH/RITHM/tree/master/streamer) implements the _[tweepy](http://www.tweepy.org/)_ package to interface with the Twitter Streaming API. This allows for easy integration of technical updates if Twitter's API changes in the future. In order to access the Twitter API, you need to (1) have a Twitter account and (2) [register](https://apps.twitter.com/) a new application associated with that account. 

Additional documentation for setting up the RITHM streamer will be posted in [./streamer/](https://github.com/CRMTH/RITHM/tree/master/streamer) as it is developed. 

### _RITHM parser_
The parser re-formats raw Twitter data to human-readable format for coding and analysis. It includes features for in-depth search and retreival from raw data files, recoding emoji, and data sub-sampling. Various aspects of these features are still being refined and currently live in  [./decoder/](https://github.com/CRMTH/RITHM/tree/master/decoder). 

