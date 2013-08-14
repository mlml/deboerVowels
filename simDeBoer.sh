##
## simDeBoer.py
## NB: Run with Python 2.X (not Python 3)
##
## LSA511, Summer 2013
## Lab #2
##
## this file shows how to run the deboer.py python code to produce
## output files that can be analysed in R with the plotDeBoer.R functions.

##
## this code runs simulations to produce something like Figure 4 of
## de Boer (2000). typing 
##
## python deboer.py --help
##
## at the command line will produce a list of optional arguments. 
## the only obligatory argument is the name of a .csv file which
## stores the output.
##

##
## here, we run a simulation with 20 agents for 10,000 imitation 
## games, keeping the results of every 20 games to a file called
## nAgents20_nIts10000_storeIvl20.csv.
python deboer.py --nAgents 20 --nIts 10000 --storeIvl 20 runs/nAgents20_nIts10000_storeIvl20.csv

## 
## this example can be used to more or less produce Figure 5 of
## de Boer (2000). here, we use the optional --nRuns argument to 
## run multiple simulations with a single command. since in this 
## case we're only interested in the outcomes of the imitation 
## games, we only store the results of the last round of each 
## imitation game (i.e., --nIts == --storeIvl == 5000).
python deboer.py --nAgents 20 --nIts 5000 --storeIvl 5000 --nRuns 500 runs/nAgents20_nIts5000_storeIvl5000_nRuns1000.csv

##
## this example is similar to the first example, but increases 
## the noise from the default of 0.1 to 0.25.
python deboer.py --nAgents 20 --noise 0.25 --nIts 10000 --storeIvl 100 runs/nAgents20_noise25_nIts10000_storeIvl100.csv

##
## this example is similar to the first example, but increases 
## the populaton size from 20 to 200.
python deboer.py --nAgents 200 --nIts 10000 --storeIvl 100 runs/nAgents200_nIts10000_storeIvl100.csv
