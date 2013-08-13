## 
## examplesDeBoer.R
##
## LSA511, Summer 2013
## Lab #2
##

## 
## plotting examples in runs/ using plotDeBoer.R functions
##

source('plotDeBoer.R')

##
## 1. plot something like Figure 4 of de Boer (2000)
##

##
## load data file
x <- loadDataFile('runs/nAgents20_nIts10000_storeIvl100.csv')

##
## invPlotAllAgents takes a data frame and a list of 
## time points and produces vowel inventories for those times.
invPlotAllAgents(x, times=c(100,500,2000,10000))

##
## invPlotEach Agent takes a data frame and a list of 
## time points and produces vowel inventories for each agent
## at the specified times. a subset of agents can be 
## specified using the optional agents=c() argument.
invPlotEachAgent(x, times=c(100,500,2000,10000))
invPlotEachAgent(x, times=c(100,1000,2000,5000,10000), agents=c(1,2,5,6))


##
## agentTimeSummary takes a data frame as input and 
## returns a by-agent time summary data frame containing
## the success rate, inventory size, and inventory energy
## of agent A at time T.
ats <- agentTimeSummary(x)

##
## this data frame can now be used to produce summaries
## of the success rate, inventory size, and inventory 
## energy over time. the trajectories for individual agents
## are given as coloured lines, with the mean value at 
## each time given by the thicker blue line.
##

##
## by default, plotSuccess() uses a loess smooth for the 
## mean and plots on a linear scale. different smooths 
## can be used by passing the appropriate argument to 
## "method" (see ?stat_smooth for details). to plot on a
## logistic scale, use transform=TRUE.
##
## to plot data from a restricted subset of agents,
## pass the agent IDs as a list. the default is for
## all agents to be included.
plotSuccessProb(ats)
plotSuccessProb(ats, agents=c(1,2,20)) ## subset of agents
plotSuccessProb(ats, agents=c(1:10, 20), method="lm") ## linear smooth
plotSuccessProb(ats, transform=TRUE) ## logistic scale

##
## plotSize() plots inventory size over time. 
## different smooths and numbers of agents may be 
## specified in the same manner as for plotSuccessProb().
plotSize(ats)
plotSize(ats, agents=c(1,2,5,10,20))
plotSize(ats, method="lm")

##
## plotEnergy() plots inventory energy over time. 
## different smooths and numbers of agents can 
## be specified in the same manner as for 
## plotSuccessProb() and plotSize().
##
## note that at some timepoints, energy may 'spike'
## to extreme values. if these spikes are reducing 
## interpretability of the rest of the plot, you can 
## manually restrict the range of values shown by 
## appending '+ ylim(min, max)' to the function call.
plotEnergy(ats)
plotEnergy(ats, agents=c(1,10,11,19,20))
plotEnergy(ats, method="lm")
plotEnergy(ats) + ylim(0,11) ## produces warning


##
## 2. plot something like Figure 4 of de Boer (2000)
##
xRuns <- loadDataFile('runs/nAgents20_nIts5000_storeIvl5000_nRuns500.csv')

##
## agentRunSummary is similary to agentTimeSummary, but 
## computes averages over runs rather than over agents.
ars <- agentRunSummary(xRuns)


##
## the plotSuccessDist, plotSizeDist, and plotEnergyDist
## functions take an agentRunSummary data frame as their
## sole input and produce histograms showing the 
## distribution of each feature over time. count is 
## indicated by colour as well as height.
plotSuccessDist(ars)
plotSizeDist(ars)
plotEnergyDist(ars)

##
## 3. exploring some effects of added noise 
##

y <- loadDataFile('runs/nAgents20_noise25_nIts10000_storeIvl100.csv')
invPlotAllAgents(y, times=c(100,500,2000,10000))
yats <- agentTimeSummary(y)
plotSuccessProb(yats) + theme(legend.position="none") ## supress legend
plotSize(yats) + theme(legend.position="none") 
plotEnergy(yats) + theme(legend.position="none")


##
## 4. exploring the effect of increasing population size
##

z <- loadDataFile('runs/nAgents200_nIts10000_storeIvl100.csv')
invPlotAllAgents(z, times=c(100,500,2000,10000))
zats <- agentTimeSummary(z) ## takes somewhat longer to run...
plotSuccessProb(zats) + theme(legend.position="none")
plotSize(zats) + theme(legend.position="none") 
plotEnergy(zats) + theme(legend.position="none")
plotEnergy(zats) + theme(legend.position="none") + ylim(0,10)

