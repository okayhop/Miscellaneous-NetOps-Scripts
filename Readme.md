# Miscellaneous NetOps Scripts

### Intro

As projects come and go, I have found that writing some quick scripts for automation work
can save me a ton of time. These scripts are geared to the "one and done" type of task items
where a full fledged development project would be grossly overkill.

I also utilize these scripts.examples in my blog. You can find it at www.koreyhopkins.com
### How To Use

As I add scripts over time, I will update the **Contents** section of this Readme with a 
quick description of what each script is at a high level. Within each script, I will include
more detailed documentation and commenting that should aid *you* in seeing how to use and 
adapt code for your use case and *me* for remembering what I did and for what purpose :)

### Contents

* SVI_config 
	* I needed to configure a TON of SVIs on a Cisco 3850 stack for an infrastructure deployment
	project. This script imports a CSV file, inputs the data into a SVI template, and then pushes 
	configuration snippet, and pushes to the switch. If the switch is not reachable, it dumps the config to
	a text file. Originally written for Python 2.7.
	
* Unit Testing
    * Demonstrating how one could use the concept of unit testing for testing that a network device
    works as intended.

