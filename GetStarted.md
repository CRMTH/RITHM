# Getting Started

## Setting up RITHM infrastructure
0. This guide assumes that you already have [Python 3.x](https://www.python.org/downloads/) installed on your system.

### 1. Install Git client 
To use the RITHM streamer you must install git, use the link below to install git if you don’t have git already.
> https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

### 2. Download RITHM source files
To install the RITHM source files (1.) open the command line, (2.) navigate to the directory that you want the RITHM folder in, and (3.) use the command line below:
> `git clone http://github.com/CRMTH/RITHM/`

### 3. Download and install Twython
For the streamer to run, the Twython package must be installed in the Python instance that you are using.~~~loacated within the RITHM folder.~~~ Follow the instructions provided in the link below to donwload and install Twython: 
> https://github.com/ryanmcgrath/twython


## Setting up Twitter

### 1. Create a new Twitter user account
1. You must have a Twitter account to procees to step 2. If you don't already have an account, use the link below to create one.  We strongly recommend using an account that is dedicated to the streamer (i.e., don't use a personal account).
>https://twitter.com/i/flow/signup?lang=en

### 2. Create a Twitter developer account
The next step is to obtain access to Twitter as a developer. Use your Twitter credentials and follow the steps provided in the link below to obtain access.
>https://developer.twitter.com/en/apply-for-access

### 3. Create a Twitter developer app
The next step is to create an app on Twitter. After creating an app, youwill receive authentication credentials (i.e., digital keys) to connect to the Twitter streaming API.
>https://apps.twitter.com/app/new

### 3. Save your Twitter app keys 
After creating an app, open the "keys and access tokens " tab. 
There you will find your:
> Consumer Key (API Key), Consumer Secret (API Secret), Access Token, and Access Token Secret.

Using your preffered text editor open the `./RITHM/streamer/auth.ini` file and put your Consumer Key (API Key),
Consumer Secret (API Secret), Access Token, and Access Token Secret into their respective places.




### Set up RITHM streamer 

### How to start the streamer. 
From here on out, use the [streamer documentation](https://github.com/CRMTH/RITHM/tree/master/streamer).
