deboerVowels
============

Description: 

Vowel system simulation based on ['Self Organization in Vowel Systems'](http://ai.vub.ac.be/~bart/papers/deBoerJOP2000.pdf) (deBoer 2000)
with some small changes from two sources: deBoer's 1999 [book](http://ukcatalogue.oup.com/product/9780198299653.do)
and Java implementation by [Julian Bradfield](http://homepages.inf.ed.ac.uk/jcb/).

Requirements: 

a computer with python and R environments. If you don't have them...

	python.org/getit/
	cran.r-project.org/

and follow the instructions on the site.


Author:  Morgan Sonderegger and Misha Schwartz, 7/2013

This code was developed for the "Computational Models of Sound Change" MS co-taught with [James Kirby](http://www.lel.ed.ac.uk/~jkirby/) at the [2013 LSA Institute](http://lsa2013.lsa.umich.edu/).

---------------------------------------------------------------------------------------

How to use deboer.py:

deboer.py can be run directly from the command line. 
To run with all default settings you only need to specify a .csv file to write to.

	$ python deboer.py sample.csv

To check the default values and information for all parameters run with the -h flag.

	$ python deboer.py -h

This will give a list of all parameters, the flag to specify a change, as well a 
description of the parameter, the setting used in the de Boer article (if applicable)and the default setting if the flag is not used. For example...

	--successThresh SUCCESSTHRESH
                        success/uses ratio under which vowel added (deboer:
                        0.5; default: 0.5)

To change a parameter from the default, run with the flag followed by the new
setting. For example, to run with 5000 interactions and 20 agents (default is 10000
interactions and 5 agents)...

	$ python deboer.py --nIts 5000 --nAgents 20 sample.csv

The .csv file that has been created can now be visualized using the plotDeBoer.R 
program. And so...

---------------------------------------------------------------------------------------

How to use plotDeBoer.R:

On the command line, launch R by typing 

	$ R

Then call the plotDeBoer.R file, this will allow you to run functions from 
plotDeBoer.R  

	> source('/Users/me/deBoerVowels/plotDeBoer.R')

Now load the .csv file created by the deboer.py program and assign it to a variable

	> x <- loadDataFile('sample.csv')

You can now use the functions outlined in plotDeBoer.R to illustrate the data 
in the .csv file.  

------------------------------

Here are four examples of how you might choose to implement 
these functions (start at the command line):

------------------------------

1. emergence of a vowel system (as seen in deboer 2000 figure 4)

Run a simulation with 20 agents for 10,000 imitation games, keeping the results of every 20 games

	$ python deboer.py --nAgents 20 --nIts 10000 --storeIvl 20 runs/nAgents20_nIts10000_storeIvl20.csv

then:

	$ R
	> source('/Users/me/deBoerVowels/plotDeBoer.R')
	> x <- loadDataFile('nAgents20_nIts10000_storeIvl20.csv')

Use invPlotAllAgents to plot the vowel inventories different points in time (
default is every 100 interactions)
	
	> invPlotAllAgents(x)

To only show inventories at times 100, 500, 2000, and 10000

	> invPlotAllAgents(x, times=c(100,500,2000,10000))

To only show vowel inventories for specific agents

	> invPlotEachAgent(x, times=c(100,1000,2000,5000,10000), agents=c(1,2,5,6))

In order to plot the success rate, inventory size and inventory energy over time
first create a time summary data frame for each agent (containing success rate, 
inventory size, and inventory energy), and then use it to plot each over time. 
Hit enter after each line to generate each plot.

	> ats <- agentTimeSummary(x)
	> plotSuccessProb(ats)
	> plotSize(ats)
	> plotEnergy(ats)

specific agents can be specified for each, for example

	> plotSuccessProb(ats, agents=c(1,2,20))

different smooths can be used, (see ?stat_smooth for details). For example, a linear 
smooth for agents 1 to 10 and 20

	> plotSuccessProb(ats, agents=c(1:10, 20), method="lm") 

To plot on a logistic scale use transform=TRUE

	> plotSuccessProb(ats, transform=TRUE)

Finally, to reduce spikes at certain timepoints that reduce readability of the plot
apply a limiter on the y axis of the plot (Note: this will produce a warning)

	> plotSuccessProb(ats) + ylim(0,11)

------------------------------

2. plot the average success, size and energy over runs (instead of agents)

Run a simulation with multiple runs: 500 runs, 20 agents, 5000 interactions (with only 
the last one stored): 

	$ python deboer.py --nAgents 20 --nIts 5000 --storeIvl 5000 --nRuns 500 runs/nAgents20_nIts5000_storeIvl5000_nRuns1000.csv

then:

	$ R
	> source('/Users/me/deBoerVowels/plotDeBoer.R')
	
Load the .csv file containing data from multiple runs 

	> xRuns <- loadDataFile('nAgents20_nIts5000_storeIvl5000_nRuns1000.csv')

Then create run summary data for this file (like agentTimeSummary but over runs
instead of agents).

	> ars <- agentRunSummary(xRuns)

Now, plotSuccessDist, plotSizeDist, and plotEnergyDist can take ars as their 
input and will produce histograms showing the distribution of each feature as
height

	> plotSuccessProb(ats)
	> plotSize(ats)
	> plotEnergy(ats)

-------------------------------

3. exploring the effects of added noise

Run a simulation increasing the noise from 0.1 to 0.25 (otherwise similar to the first
example):

	$ python deboer.py --nAgents 20 --noise 0.25 --nIts 10000 --storeIvl 100 runs/nAgents20_noise25_nIts10000_storeIvl100.csv

then:

	$ R
	> source('/Users/me/deBoerVowels/plotDeBoer.R')	

Load the .csv file containing data with adjusted noise

	> y <- loadDataFile('nAgents20_noise25_nIts10000_storeIvl100.csv')

Then you can plot the inventories to see the effects of added noise

	> invPlotAllAgents(y, times=c(100,500,2000,10000))

plot success probability, size and energy (theme(legend.position="none") will 
supress the legend)

	> yats <- agentTimeSummary(y)
	> plotSuccessProb(yats) + theme(legend.position="none") ## supress legend
	> plotSize(yats) + theme(legend.position="none") 
	> plotEnergy(yats) + theme(legend.position="none")

-------------------------------

4. exploring the effect of increased population size

Run a simulation increasing the population from 20 to 200 (otherwise similar to the first
example):

	$ python deboer.py --nAgents 200 --nIts 10000 --storeIvl 100 runs/nAgents200_nIts10000_storeIvl100.csv

then:

	$ R
	> source('/Users/me/deBoerVowels/plotDeBoer.R')	

Load the .csv file containing data with adjusted population size

	> z <- loadDataFile('sample_nAgents200.csv')

Then you can plot the inventories to see the effects of increased population

	> invPlotAllAgents(z, times=c(100,500,2000,10000))

plot success probability, size and energy 

	> zats <- agentTimeSummary(z) 
	> plotSuccessProb(zats) + theme(legend.position="none")
	> plotSize(zats) + theme(legend.position="none") 
	> plotEnergy(zats) + theme(legend.position="none")

	
