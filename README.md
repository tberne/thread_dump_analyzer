# Java Thread Dump Analyzer

Given Java thread dump files, this tool will analyze them and provide a summary of the threads and their states
(long-running threads and threads with the same stacktrace, for now).

It receives a configuration file with the following parameters:
```yaml
debug: false

files: # accepts glob patterns
  - file1.txt
  - file2.txt
  - folder/*.txt

# the configuration for the long-running threads
long_running_threads: 
  # ignores threads with no stacktrace
  ignore_dummy_threads: true
  
  # in how many thread dumps the thread should be present to be considered long-running
  threshold: 2
  
  # the patterns to include or exclude threads
  include_patterns:
    
    # filters threads by their stacktrace
    stack_trace:
      - ^br\.com\.company\.package\..*
        
    # filters threads by their name
    thread_name:
      - ^Some thread name.*
  
  exclude_patterns:
    
    # filters threads by their stacktrace
    stack_trace:
      - ^br\.com\.company\.package\.excluded\..*
    
    # filters threads by their name
    thread_name:
      - ^Some excluded thread name.*

# the configuration for the most recurring threads
most_recurring_threads: 
  # ignores threads with no stacktrace
  ignore_dummy_threads: true
  
  # how many threads must have the same stacktrace to be considered recurring
  threshold: 2
  
  # the patterns to include or exclude threads
  include_patterns:
    
    # filters threads by their stacktrace
    stack_trace:
      - ^br\.com\.company\.package\..*
        
    # filters threads by their name
    thread_name:
      - ^Some thread name.*
  
  exclude_patterns:
    
    # filters threads by their stacktrace
    stack_trace:
      - ^br\.com\.company\.package\.excluded\..*
    
    # filters threads by their name
    thread_name:
      - ^Some excluded thread name.*

renderer:
  type: renderer_type # one of: console, file, json, html
  config:
    output_file: out.html # file, json and html renderers need an output_file config
```
