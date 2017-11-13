## Real-time Infoveillance of Twitter Health Messages (RITHM)
![MTH logo](http://mth.pitt.edu/sites/all/themes/pitt_cromh/img/CROMH-mark-revised.png)

__[Center for Research on Media, Technology, and Health](http://mth.pitt.edu/)__

_This is the documentation for installing and utilizing the RITHM framework to retrieve and parse Twitter Streaming API data for public health research. An associated mauscript is currently under development and this repository will continue to be updated in parallel. Technical questions can be sent to Jason Colditz (colditzjb@pitt.edu)._

___Update (7 Nov. 2017)__ - The Twitter platform has extended the maximum length of tweets from 140 to 280 characters. This has not affected the fidelity of RITHM data and makes negligible difference on overall file sizes. However, please be aware that this may impact the validity of analyses conducted across the transitional period._

### _RITHM streamer_
The [streamer](https://github.com/CRMTH/RITHM/tree/master/streamer) implements the _[Twython](https://github.com/ryanmcgrath/twython)_ package to interface with the Twitter Streaming API. This allows for easy integration of technical updates if Twitter's API changes in the future. In order to access the Twitter API, you need to (1) have a Twitter account and (2) [register](https://apps.twitter.com/) a new application associated with that account. 

Additional documentation for setting up the RITHM streamer is posted in the [./streamer/](https://github.com/CRMTH/RITHM/tree/master/streamer) folder. 

### _RITHM parser_
The parser re-formats raw Twitter data to human-readable format for coding and analysis. It includes features for in-depth search and retreival from raw data files, recoding emoji, and data sub-sampling. The documentation is still being developed in the [./parser/](https://github.com/CRMTH/RITHM/tree/master/parser) folder. 

