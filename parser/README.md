# Basic command line arguments:
These are some common command line arguments used by RITHM scripts. These are defined and documented further in parselogic.py _cmdvars_ function. Of note: some directory and file paths can include './' and '../' prefixies, which will make them relative to the path defined by '-dir'. By specifying a relative path for an output step, the directory will be created if it does not exist. Directory paths must ALWAYS include a trailing slash '/'.

* `-date` or `-dates` indicates start/end dates (+2; MMDDYYYY objects) 
* `-dir` or `-dirin` indicates primary directory path to read files (+1)
* `-out` or `-dirout` specifies output directory path (+1)
* `-mkdir` or `-mkout` are same as '-out' but will also create the output directory
* `-file` or `-filein` indicates a primary file to read (+1)
* `-file2` or `-fileout` indicates a secondary file to read or an output file (+1)
* `-fstem` indicates a stem to append to beginning of output file name (+1)
* `-kwdir` indicates input directory for KWS files (+1)
* `-kwfile` indicates specific KWS file (+1; overrides '-kwdir')
* `-rt` indicates that retweets should be included in the process / output 


# RITHM Parser

## Basic use:
The *RITHM parser* allows you to effectively work with data obtained through the *RITHM streamer*. It converts complex JavaScript Object Notation (JSON) data types to Tab Separated Value (TSV) data types that are easier to work with for analysis. It performs basic text and punctuation tokenization for machine learning approaches (e.g., n-gram text classification, Natural Language Processing) and converts common Unicode representations (e.g., emoji) to a human-readable text format. Several data subsampling approaches are also included.

### Requirements:
The *RITHM parser* is built in/for Python 3.5+ and not tested in earlier Python versions. It relies on Python core libraries and should not require 3rd party packages to be installed. 

### Running:
The `parser.py` reads commands from a template file (`template.par` by default) and passess arguments to `decode.py` and other ancillary scripts for data processing. After updating the template file, simply run `parser.py` to parse data. 

### Basic settings:
The `template.par` file provides a range of options for customization. Each project should have a separate `*.par` file, so that you can keep track of how you handled each distinct job. When you run `parser.py` in command line, you can also specify other `*.par` files to read from...

#### Command line arguments:
When you run `parser.py`, the following command line arguments will override settings related to `*.par` files:
*  `-file` indicates template file input (must be followed by a valid `*.par` file name)
* `-dates` indicates date range (must be followed by two _YYYYMMDD_ formatted dates)
*   `-low` indicates that the process should run in low memory mode

So, an example command might look like: `python3 parser.py -file template2.par -dates 20180101 20181231 -low`

#### Date ranges:
Date ranges follow a _YYYYMMDD_ format and are inclusive of start and end date. If files are currently being written by a streamer process, it is advisable to set an end date prior to today. Depending on your system settings, file locking protocols may cause the streamer to fail if you try to read from an active file.

#### Memory considerations and data handling:
As the raw data files can become quite large (up to several GB per file/day), we have included options to read files in "high memory" or "low memory" modes. *High memory* mode loads an entire raw file into working memory before extracting data. This is time efficient but memory intensive for large files. *Low memory* mode processes one tweet at a time from the raw file, which is considerably slower but may be necessary on machines with limited working memory. If a file fails to read in high memory mode, the parser will attempt to use low memory mode for that particular file. This overcomes issues of file curruption that might occur if the streamer process was terminated with a partially-written tweet (e.g., power outage or system reboot caused abrupt streamer termination). 

#### Keywords:
Keywords are specified to refine the scope of tweets that are returned. In general, if you use the same keywords from the streamer `*.kws` file(s), you should retrieve all available results. 


# Analysis procedures:
*\[This section needs to be updated to reflect freq_out.py\]*

## Data sub-sampling (subsample.py)
When you run `subsample.py` in command line, the following arguments are used:
* Arguments that direct input/output:
  *    `-dir` (+1 parameter) input directory to find parsed `*.tsv` files (e.g., `../data/parser_out/`)
  *    `-out` (+1 parameter) output directory (e.g., `../data/parser_out/subsamples/`)
  *  `-fstem` indicates a stem to append to beginning of output file name (+1)

* Arguments that affect the data scope before randomization procedures:
  *  `-dates` specifies a date range
  * `-kwfile` is a `*.kws` file to restrict output to keyword-matched criteria (overrides '-kwdir')
  *  `-kwdir` indicates input directory (will include all available `*.kws` files) 
  *     `-rt` indicates that re-tweets should be included (default is no RTs)

* Arguments that affect the randomization procedures:
  * `-r` (+1) reduction scalar (0<r<1 is a percentage, r>=1 is a frequency)
  * `-s` (+0) indicates that randomization should be stratified by day (do not use with `-h `)
  * `-h` (+3) indicates that randomization should be stratified by popular hashtag prevalence

#### Randomization behavior
For a simple random sample of tweets, specify `-r` followed by a percentage (e.g., 0.02) or a whole number. All data files will be read into memory and a random sample will be generated. 

#### Stratification behavior
For a stratified sample, add the `-s` flag. The `-r` value must be a proportion and not a whole number. This process will read all files into memory to obtain tweet frequencies and then read files individually to select a random proportion of tweets from each file. 

#### HashSpear behavior
"HashSpear" is shorthand for stratification by _Hashtag prevalence using Spearman correlations_. This method will ensure that the top hashtags in the sub-sample will reflect the top hashtags in full set of parsed tweets (for content validity). Random subsets of data will be drawn until a desirable correlation coefficient is achieved. The `-h` option requires three numeric arguments, in this order:
   1. Number of top hashtags to assess. This should generally include top hashtags that are relevant to the topic under investigation.   
   2. Spearman coefficient (_Sr_) threshold. The minimum acceptable Spearman coefficient (0>_Sr_>1) needed to accept the data randomization.
   3. Iteration ceiling. The maximum number of randomizations to perform to achieve the desired _Sr_ value.

