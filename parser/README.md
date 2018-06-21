# RITHM Parser

## Basic use:
The *RITHM parser* allows you to effectively work with data obtained through the *RITHM streamer*. It converts complex JavaScript Object Notation (JSON) data types to tabular Comma Separated Value (CSV) data types that are easier to work with for analysis. It performs basic text and punctuation tokenization for machine learning approaches (e.g., n-gram text classification, Natural Language Processing) and converts common Unicode representations (e.g., emoji) to a human-readable text format. Several data subsampling approaches are also included.

### Requirements:
The *RITHM parser* is built in/for Python 3.5+ and not tested in earlier Python versions. It relies on Python core libraries and should not require 3rd party packages to be installed. 

### Running:
The `parser.py` reads commands from a template file (`template.par` by default) and passess arguments to `decode.py` and other ancillary program files for data processing. After updating the template file, simply run `parser.py` to parse data. 

### Basic settings:
The `template.par` file provides a range of options for customization. Each project should have a separate `*.par` file, so that you can keep track of how you handled each distinct job. When you run `parser.py` in command line, you can also specify other `*.par` files to read from...

#### Command line arguments:
When you run `parser.py` in command line, the following arguments will override settings related to `*.par` files:
* `-f ` indicates template file input (must be followed by a valid `*.par` file name)
* `-d ` indicates date range (must be followed by two _YYYYMMDD_ formatted dates)
* `-h ` indicates that the process should run in high memory mode
* `-l ` indicates that the process should run in low memory mode

So, an example command might look like: `python3 parser.py -f template2.par -d 20180101 20181231 -l`

#### Date ranges:
Date ranges follow a _YYYYMMDD_ format and are inclusive of start and end date. If files are currently being written by a streamer process, it is advisable to set an end date prior to today. Depending on your system settings, file locking protocols may cause the streamer to fail if you try to read from an active file.

#### Memory considerations and data handling:
As the raw data files can become quite large (up to several GB per file/day), we have included options to read files in "high memory" or "low memory" modes. *High memory* mode loads an entire raw file into working memory before extracting data. This is time efficient but memory intensive for large files. *Low memory* mode processes one tweet at a time from the raw file, which is considerably slower but may be necessary on machines with limited working memory. If a file fails to read in high memory mode, the parser will attempt to use low memory mode for that particular file. This overcomes issues of file curruption that might occur if the streamer process was terminated with a partially-written tweet (e.g., power outage or system reboot caused abrupt streamer termination). 

#### Keywords:
Keywords are specified to refine the tweets that are returned. In general, if you use the same keywords from the streamer `*.kws` file, you should retrieve all available results. 


## Advanced use:
_\[This needs to be updated to reflect subsampling and frequency counting.\]_

### Data sub-sampling (documentation in-progress)
When you run `subsample.py` in command line, the following arguments are used:
* `-i ` input directory to find parsed `*.csv` (e.g., `../data/parser_out/`)
* `-o ` output file directory/filename (e.g., `../data/parser_out/subsamples.csv`)
* `-r ` reduction scalar (0<r<1 is a percentage, r>=1 is a frequency)
* `-s ` indicates that randomization should be stratified by day
* `-h ` indicates that randomization should be stratified by hashtag prevalence
* `-d ` indicates date range (NOT CURRENTLY IMPLEMENTED)
* `-k ` `*.kws` file to restrict output by keyword matching criteria
* `-rt` indicates that re-tweets should be included in output (default is no RTs)

#### Basic randomization behavior
...

#### Stratification behavior
...

#### _HashSpear_ behavior
"HashSpear" is shorthand for stratification by _Hashtag prevalence using Spearman correlations_. This method will ensure that the top hashtags in the sub-sample will reflect the top hashtags in full set of parsed tweets (for content validity). Random subsets of data will be drawn until a desirable correlation coefficient is achieved. This option requires three numeric arguments, in this order:
   1. Number of top hashtags to assess. This should generally include top hashtags that are relevant to the topic under investigation.   
   2. Spearman coefficient (_Sr_) threshold. The minimum acceptable Spearman coefficient (0>_Sr_>1) needed to accept the data randomization.
   3. Iteration ceiling. The maximum number of randomizations to perform to achieve the desired _Sr_ value.

