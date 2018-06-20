### Use:
The *RITHM parser* allows you to effectively work with data obtained through the *RITHM streamer*. It converts complex JavaScript Object Notation (JSON) data types to tabular Comma Separated Value (CSV) data types that are easier to work with for analysis. It performs basic text and punctuation tokenization for machine learning approaches (e.g., n-gram text classification, Natural Language Processing) and converts common Unicode representations (e.g., emoji) to a human-readable text format. Several data subsampling approaches are also included.

### Requirements:
The *RITHM parser* is built in/for Python 3.5+ and not tested in earlier Python versions. It relies on Python core libraries and should not require 3rd party packages to be installed. 

### Running:
The `parser.py` reads commands from a template file (`template.par` by default) and passess arguments to `decode.py` and other ancillary program files for data processing. After updating the template file, simply run `parser.py` to parse data. 

### Basic settings:
The `template.par` file provides a range of options for customization. Each project should have a separate `*.par` file, so that you can keep track of how you handled each distinct job. When you run `parser.py` in command line, you can also specify other `*.par` files to read from. \[Advenced documentation to be added here.\]

#### Memory considerations and data handling:
As the raw data files can become quite large (up to several GB per file/day), we have included options to read files in "high memory" or "low memory" modes. *High memory* mode loads an entire raw file into working memory before extracting data. This is time efficient but memory intensive for large files. *Low memory* mode processes one tweet at a time from the raw file, which is considerably slower but may be necessary on machines with limited working memory. If a file fails to read in high memory mode, the parser will attempt to use low memory mode for that particular file. This overcomes issues of file curruption that might occur if the streamer process was terminated with a partially-written tweet (e.g., power outage or system reboot caused abrupt streamer termination). 

#### Date ranges:
Date ranges follow a _*YYYYMMDD*_ format and are inclusive of start and end date. If files are currently being written by a streamer process, it is advisable to set an end date prior to today. Depending on your system settings, file locking protocols may cause the streamer to fail if you try to read from an active file.

#### Keywords:
Keywords are specified to refine the tweets that are returned. In general, if you use the same keywords from the streamer `*.kws` file, you should retrieve all available results. 
...
