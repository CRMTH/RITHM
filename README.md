## Real-time Infoveillance of Twitter Health Messages (RITHM)
![MTH logo](http://mth.pitt.edu/sites/all/themes/pitt_cromh/img/CROMH-mark-revised.png)

__[University of Pittsburgh Center for Research on Media, Technology, and Health](http://mth.pitt.edu/)__

_This is the documentation for using the RITHM software framework to work with real-time Twitter data for public health research. This code is provided as-is, with no expectation that it will work exactly as you want it to. However, we will do our best to be responsive to reasonable questions/issues posted here, make updates, and provide additional documentation. This is an ongoing project and the repository (and documentation) will be updated with new developments._

# Overview:

### _[Gettting Started](https://github.com/CRMTH/RITHM/blob/master/GetStarted.md)_
The RITHM code has been tested on Windows and Linux systems. It is designed to run in a Python 3.x environment. In order to set up a RITHM implementation, you will need access to the Twitter API (to connect and collect tweets) and Git (to get the RITHM code from here to the machine that you are running it on). Please see our [Getting Started Guide](https://github.com/CRMTH/RITHM/blob/master/GetStarted.md) for additional details.

### _[RITHM Streamer](https://github.com/CRMTH/RITHM/tree/master/streamer)_
The [streamer](https://github.com/CRMTH/RITHM/tree/master/streamer) implements the _[Twython](https://github.com/ryanmcgrath/twython)_ package to interface with the Twitter Streaming API. This allows for easy integration of technical updates if Twitter's API changes in the future. In order to access the Twitter API, you need to (1) have a Twitter account and (2) [register](https://apps.twitter.com/) a new application associated with that account. Please see our [Getting Started Guide](https://github.com/CRMTH/RITHM/blob/master/GetStarted.md) for additional details.

Once that is all set, please see documentation for running the RITHM streamer, in the [./streamer/](https://github.com/CRMTH/RITHM/tree/master/streamer) folder. 

### _[RITHM Parser](https://github.com/CRMTH/RITHM/tree/master/parser)_
The parser re-formats raw Twitter data to human-readable format for coding and analysis. It includes features for in-depth search and retreival from raw data files, recoding emoji, and data sub-sampling. That documentation is in the [./parser/](https://github.com/CRMTH/RITHM/tree/master/parser) folder. 

# Citation:
If you use the RITHM software or resources for your research, please cite our development paper: 
>Colditz JB, Chu K, Emery SL, Larkin CR, James AE, Welling J, Primack BA. Toward real-time infovellience of Twitter health messages. _American Journal of Public Health_. 2018;108(8). \[Online before print\] doi: [10.2105/AJPH.2018.304497](https://doi.org/10.2105/AJPH.2018.304497)

# Project team updates:

_**`4 Apr. 2018`** - [Our research paper](https://doi.org/10.2105/AJPH.2018.304497) related to RITHM development has been accepted for publication at American Journal of Public Health. This paper provides practical considerations for enhancing the validity and reproducibility of Twitter content analysis._

_**`1 Mar. 2018`** - Our ongoing research is now funded through a grant from the US National Cancer Institute ([R01-CA225773](https://taggs.hhs.gov/Detail/AwardDetail?arg_AwardNum=R01CA225773&arg_ProgOfficeCode=110); PI: [Primack](https://www.dom.pitt.edu/dgim/faculty_info.aspx/Primack4945))._

_**`7 Nov. 2017`** - The Twitter platform has extended the maximum length of tweets from 140 to 280 characters. This has not affected the fidelity of RITHM data collection and makes negligible difference on overall raw data file sizes. However, this may impact the validity of analyses conducted across the transitional period._

_**`1 Apr. 2016`** - We received an initial start-up grant to use the [Bridges](https://www.psc.edu/bridges) infrastructure at Pittsburgh Supercomputing Center (XRAC-TG-DBS160002; PI: [Primack](https://www.dom.pitt.edu/dgim/faculty_info.aspx/Primack4945)). Future publications [should acknowledge](https://www.psc.edu/allocations/acknowledgement-in-publications) that this work "is supported by NSF award number ACI-1445606, at the Pittsburgh Supercomputing Center (PSC)."_
