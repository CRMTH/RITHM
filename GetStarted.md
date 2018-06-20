# Getting Started
> This markdown file needs to be updated so that others can get started using RITHM. There is an open [issue](https://github.com/CRMTH/RITHM/issues/12) related to this. For formatting, don't use these quote blocks (they are just here as placeholders). Use heading formats, numbered lists, and links as much as possible (check your markdown cheat sheet or [here](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)).

## Setting up Twitter
> There are a couple links under "RITHM Streamer" in [README.md](https://github.com/CRMTH/RITHM/blob/master/README.md) to get you started with outlining the processes under this heading. Follow those links and document the steps that you took to get the infrastructure set up.

### Create a new Twitter user account

You must have a Twitter account to run the streamer. If you don't already have an account, use the link below to create one.  I strongly recommend using an account one unique to the streamer.
>
>https://twitter.com/i/flow/signup?lang=en

### Create a Twitter developer account

The next step is to obtain access to Twitter as a developer. Use your Twitter credentials and follow the steps provided in the link below to obtain access.
> 
>https://developer.twitter.com/en/apply-for-access

## Setting up RITHM

### Install Git client 

To use the RITHM streamer you must install git, use the link below to install git if you don’t have git already.

> https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

### Download RITHM source files

Insall the RITHM source files by opening the command line and use the command line method below:
> ```git clone http://github.com/CRMTH/RITHM/```

Follow the instructions provided in the link below to donwload Twython: 
>
> https://github.com/ryanmcgrath/twython

For the streamer to run Twython must be loacated within the RITHM folder. **This is crucial**.

### Create a Twitter developer app

The next step is to create an app on Twitter. After creating an app, your authentication keywords will become available.
> 
>https://apps.twitter.com/app/new

### Set up RITHM streamer 
  
 After creating an app, open the "keys and access tokens " tab. 
 There you will find your:
> Consumer Key (API Key), Consumer Secret (API Secret), Access Token, and Access Token Secret.

Using your preffered text editor open the "auth.ini' stored within the RITHM folder and put your Consumer Key (API Key),
Consumer Secret (API Secret), Access Token, and Access Token Secret into their respective places.

_The "auth.ini" file will have well defined places to paste your authentication keys._

> How to start the streamer. From here on out, use the streamer documentation!
