### Use:
The *RITHM streamer* allows you to access and download real-time data from the Twitter Streaming API. It is designed to run constantly and to be resillient against interference from common Twitter API errors.  It will not collect data while not running nor back-up to catch data that it missed. Therefore, it should ideally be used on a machine that will be running uninterrupted for the duration of data collection. Depending on the scope of data collection, common hardware configurations include: virtual machine on a shared/cloud server, dedicated physical machine with a back-up power supply, micro-computer (e.g., Raspberry PI) set to auto-run the code on restart. 

### Requirements:
Ths code has been tested for Python 2.7, but Python 3.5+ is the preferred environment. You will also need to install the [Twython](https://github.com/ryanmcgrath/twython) package prior to use.


### Authentication:
You must have your own Twitter Developer account and Application Programming Interface (API) keys in order to use the streamer. This is free, but requires some configuration. Please see the [Twython](https://github.com/ryanmcgrath/twython) documentation for additional details. Once obtained, API keys need to be entered in the "auth.ini" file.

***Note:** The streamer is not configured for running multiple streams at once. You should not attempt to operate multiple streams using the same account or using different accounts on the same IP address. Twitter may disable your account(s) for attempting to do this.*


### Selecting keywords:
You should replace the "keywords1.kws" file with a new file that includes the particular keywords that you want to search for. Multiple keyword files are supported! Any file in the streamer directory with a **.kws** extension will be treated as a keyword file. The streamer will check for changes in keyword files at midnight (local time). This allows you to start and stop data collection for particular keywords without interrupting the streamer process. Active keyword listings (combined across all keyword files) are available in **\*\_log.tsv** files that are generally in the **./RITHM/data/streamer_raw/** directory, along with the output data files.

***Note:** There is no available documentation for an upper-limit of keywords allowed, but there is a limit! Estimates are between 200-400 keywords. Additional testing in this area would be appreciated!*


### Running the streamer:
The streamer can be run within a graphical interface for testing, if desired. Generally, the streamer should be run from a command line interface. Navigate to the streamer directory and use a command like ``nohup python3 streamer.py &``\* if you are using Python 3. When activated, the process will automatically create a "KillSwitch.txt" file in the streamer directory.

**\*** *This particular command generally works in a Unix BASH shell. The "nohup" will keep the process running after you close the terminal or log off (if working remotely). The ampersand runs the process in the background.*

### Stopping the streamer:
In order to safely stop the streamer process, simply delete the "KillSwitch.txt" file from the streamer directory. The process will terminate as soon as the next tweet is delivered. If you kill the streamer process in other ways, the current output data file is likely to become corrupted. 


### Advanced options:
You can change input and output directories using the "paths.ini" file. There are also some options available toward the top of the "streamer.py" file, which will allow you to further tweak the working directory and language settings. By default, the streamer is limited to tweets that are recognized as English language by Twitter.


### Using the data:
The tweets are dumped into the currently-active output file in JavaScript Object Notation (JSON) format. At midnight (local time), a new file will be created for the next day's data. File names begin with a datetime stamp in a "YYYYMMDDHHMMSS" format. This helps to limit file size and keeps the output organized, one day at a time. Once data are collected, the *RITHM parser* is used for decoding, formatting, and subsampling the raw data.
