### Use:
The *RITHM parser* allows you to effectively work with data obtained through the *RITHM streamer*. It converts complex JavaScript Object Notation (JSON) data types to tabular Comma Separated Value (CSV) data types that are easier to work with for analysis. It tokenizes text and punctuation to be useful for machine learning approaches (e.g., n-gram text classification, Natural Language Processing) and converts common Unicode representations (e.g., emoji) to a human-readable text format. Several data subsampling approaches are also included.

### Requirements:
The *RITHM parser* is built in/for Python 3.5+ and not tested in earlier Python versions. It relies on Python core libraries and should not require 3rd party packages to be installed. 

### Memory considerations and data handling:
As the raw data files can become quite large (up to several GB per file/day), we have included options to read files in "high memory" or "low memory" modes. *High memory* mode loads an entire raw file into working memory before extracting data. This is time efficient but memory intensive for large files. *Low memory* mode processes one tweet at a time from the raw file, which is considerably slower but may be necessary on machines with limited working memory. If a file fails to read in high memory mode, the parser will attempt to use low memory mode for that particular file. This overcomes issues of file curruption that might occur if the streamer process was terminated with a partially-written tweet (e.g., power outage or system reboot caused abrupt streamer termination). 

...
