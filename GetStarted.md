# Getting Started

## Setting up RITHM infrastructure
This guide assumes that you already have [Python 3.x](https://www.python.org/downloads/) installed on your system.

### 1. Install Git client 
Use Git to get the RITHM files from this site to your system. If you don’t have already have it (most Linux distros should have it already but Windows machines generally do not), use the link below to get Git.
> https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

> _Note: There is no PIP installation for RITHM yet, but it is on our to-do list. We will update this guide when that's ready._

### 2. Download RITHM source files
To install the RITHM source files (1.) open the command line, (2.) navigate to the directory that you want the RITHM folder to be in, and (3.) use the command line below:
> `git clone http://github.com/CRMTH/RITHM/`

> _Note: The data that you download will default to a `./RITHM/data/` subfolder, so you may need to pick a location where you can store lots of data, or plan to change that setting (more on that later)._

### 3. Download and install Twython
For the streamer to run, the Twython package must be installed in the Python instance that you are running.~~~loacated within the RITHM folder.~~~ Follow the instructions provided in the link below to donwload and install Twython: 
> https://github.com/ryanmcgrath/twython

## Setting up Twitter

### 4. Create a new Twitter user account
1. You must have a Twitter account to procees to step 2. If you don't already have an account, use the link below to create one.  We strongly recommend using an account that is dedicated to the streamer (i.e., don't use a personal account).
>https://twitter.com/i/flow/signup?lang=en

### 5. Create a Twitter developer account
The next step is to obtain access to Twitter as a developer. Use your Twitter credentials and follow the steps provided in the link below to obtain access.
>https://developer.twitter.com/en/apply-for-access

### 6. Create a Twitter developer app
The next step is to create an app on Twitter. After creating an app, you will receive authentication credentials (i.e., digital keys) to connect to the Twitter streaming API.
>https://apps.twitter.com/app/new

### 7. Save your Twitter app keys 
After creating an app, open the "keys and access tokens " tab. 
There you will find your:
> Consumer Key (API Key), Consumer Secret (API Secret), Access Token, and Access Token Secret

Using a text editor, open the `./RITHM/streamer/auth.ini` file and paste in your Consumer Key (API Key),
Consumer Secret (API Secret), Access Token, and Access Token Secret into their respective places.

## You're \[almost\] ready to go!
From here on out, use the [streamer documentation](https://github.com/CRMTH/RITHM/tree/master/streamer).
