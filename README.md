## Real-time Infoveillance of Twitter Health Messages (RITHM)
![MTH logo](http://mth.pitt.edu/sites/all/themes/pitt_cromh/img/CROMH-mark-revised.png)

__[University of Pittsburgh Center for Research on Media, Technology, and Health](http://mth.pitt.edu/)__

_This is the documentation for using the RITHM Python framework to work with Twitter Streaming API data for public health research. This code is provided as-is, with no expectation that it will work exactly as you want it to. However, we will do our best to be responsive to reasonable questions/issues posted here, make updates, and provide additional documentation._

___Update (4 Apr. 2018)__ - Our paper related to RITHM has been accepted for publication at American Journal of Public Health! This paper will provide practical considerations for enhancing the validity of RITHM implementations related to collecting, formatting, and human coding of data. A link will be posted here when the article is published online._

___Update (7 Nov. 2017)__ - The Twitter platform has extended the maximum length of tweets from 140 to 280 characters. This has not affected the fidelity of RITHM data collection and makes negligible difference on overall raw data file sizes. However, please be aware that this may impact the validity of analyses conducted across the transitional period._

### _RITHM setup_
The RITHM code has been tested on Windows and Linux systems. It is designed to run in a Python 3.x environment. In order to set up a RITHM implementation, you will need access to the Twitter API (to connect and collect tweets) and Git (to get the RITHM code from here to the machine that you are running it on). Please see our [Getting Started Guide](https://github.com/CRMTH/RITHM/blob/master/GetStarted.md) for additional details.

### _RITHM streamer_
The [streamer](https://github.com/CRMTH/RITHM/tree/master/streamer) implements the _[Twython](https://github.com/ryanmcgrath/twython)_ package to interface with the Twitter Streaming API. This allows for easy integration of technical updates if Twitter's API changes in the future. In order to access the Twitter API, you need to (1) have a Twitter account and (2) [register](https://apps.twitter.com/) a new application associated with that account. 

Additional documentation for setting up the RITHM streamer is posted in the [./streamer/](https://github.com/CRMTH/RITHM/tree/master/streamer) folder. 

### _RITHM parser_
The parser re-formats raw Twitter data to human-readable format for coding and analysis. It includes features for in-depth search and retreival from raw data files, recoding emoji, and data sub-sampling. The documentation is still being developed in the [./parser/](https://github.com/CRMTH/RITHM/tree/master/parser) folder. 

