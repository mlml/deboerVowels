library(ggplot2)
library(plyr)

## 
## helper functions
##


##
## input: hz
## output: bark (formula deBoer uses)
##
hzToBark <- function(hz){
  stopifnot(hz>0)
  if(hz > 271.32){
    bark <- log(hz/271.32)/0.1719 + 2
  }
  else{
    bark <- (hz - 51)/110
  }
  return(bark)
}

##
## load csv file and transform hz to Bark.
##
loadDataFile <- function(csvF){
  x <- read.csv(csvF, header=T)

  ## make bark columns
  x$F1bark <- sapply(x$F1, hzToBark)
  x$F2bark <- sapply(x$F2, hzToBark)
  x$F3bark <- sapply(x$F3, hzToBark)
  x$F4bark <- sapply(x$F4, hzToBark)
  return(x)
}


##
## compute distance between two signals A and B
##
vowelDist <- function(x, lambda=0.3){
  d <- sqrt( (x[1]-x[3])^2 + lambda * (x[2]-x[4])^2)
  return(d)  
}

##
## find energy for vowel system of agent A at time T
##
findEnergy <- function(F1, F2prime, lambda=0.3){
  pairs <- data.frame(F1=F1,F2prime=F2prime)
  z <- ddply(pairs, .(), function(d) if (nrow(d) == 1) NULL
             else {
               row_pairs <- combn(nrow(d),2)
               cbind( a = d[ row_pairs[1,], ],
                      b = d[ row_pairs[2,], ] )
             })[, -1]    
  return(sum(apply(z, 1, function(x) 1/vowelDist(x)^2)))
}

##
## creates data frame containing summary statistics for agent A
## at time T. this only works for data frames containing a single run
##
agentTimeSummary <- function(df,lambda=0.3){
  k <- ddply(df, .(agent, time), summarise, successRate=mean(SuccessCount/UseCount, na.rm=T), size=length (unique(vowel.id)), energy=findEnergy(F1bark,F2prime,lambda))
  k$agent <- as.factor(k$agent)
  return(k)
}

## (added for jiang)
agentTimeGroupSummary <- function(df,lambda=0.3){
  k <- ddply(df, .(agent, time), summarise, successRate=mean(SuccessCount/UseCount, na.rm=T), size=length (unique(vowel.id)), energy=findEnergy(F1bark,F2prime,lambda), group=identity(group[1]))
  
  k$agent <- as.factor(k$agent)
  k$group <- as.factor(k$group)
  return(k)
}


##
## creates data frame containing summary statistics for agent A 
## after run R. requires a data frame containing multiple runs.
##
agentRunSummary <- function(df){
  k <- ddply(df, .(run), function(x) agentTimeSummary(x))
  k <- subset(k, time == max(k$time))
  k <- ddply(k, .(run), summarise, meanSuccess = mean(successRate), meanSize = mean(size), meanEnergy=mean(energy))
  return(k)
}


##
## visualization functions
##

##
## plot vowel inventories for all agents at a user-specified 
## number of time points.
##
invPlotAllAgents <- function(df, times=c()){
    if(length(times)>0){ df <- subset(df, time %in% times) }
    g <- ggplot(aes(x=F2prime, y=F1bark), data=df) + geom_point() + facet_wrap(~time) + theme(legend.position='none') + xlab("F2' (Bark)") + ylab("F1 (Bark)") + scale_x_reverse(limits=c(17,7)) + scale_y_reverse(limits=c(9,0))
  return(g)
}


##
## produces one facet per agent, with one point drawn every fact time 
## points (default:1000).
##
invPlotEachAgent <- function(df, times=c(), agents=unique(df$agent)){ 
    if(length(times)>0){ df <- subset(df, time %in% times) }
    df$time<-as.factor(df$time)
    g <- ggplot(aes(x=F2prime, y=F1bark), data=subset(df, agent %in% agents)) + geom_point(aes(color=time)) + facet_wrap(~agent) + xlab("F2prime (Bark)") + ylab("F1 (Bark)") + scale_x_reverse(limits=c(17,7)) + scale_y_reverse(limits=c(9,0))
  return(g)
}


##
## plots probability of success over time.
## transform=TRUE shows logit transform.
## 
plotSuccessProb <- function(summaryDf, agents = unique(summaryDf$agent), method="loess", transform=FALSE){
  if(transform==TRUE){ 
    g <- ggplot(aes(x=time, y=successRate), data=data.frame(subset(summaryDf, agent %in% agents), group='a')) + geom_line(aes(color=agent), alpha=0.5) + geom_smooth(se=F,size=1, method=method) + scale_y_log10(breaks=c(0,0.25,0.5,0.75,1)) 
  } else {
  g <- ggplot(aes(x=time, y=successRate), data=data.frame(subset(summaryDf, agent %in% agents), group='a')) + geom_line(aes(color=agent), alpha=0.5) + geom_smooth(se=F,size=1, method=method) + ylim(0,1) 
  }
  return(g)
}

##
## plots size of vowel inventories over time
##
plotSize <- function(summaryDf, agents = unique(summaryDf$agent), method="loess"){
  g <- ggplot(aes(x=time,y=size), data=data.frame(subset(summaryDf, agent %in% agents))) + geom_line(aes(group=agent, color=agent), alpha=0.5) + geom_smooth(se=F,size=1, method=method) 
  return(g)
}

##
## plots mean energy over time
##
plotEnergy <- function(summaryDf, agents = unique(summaryDf$agent), method="loess"){
  ## <hack> ##
  temp <- summaryDf[!is.finite(summaryDf$energy),]
  if(nrow(temp) > 0){ summaryDf[!is.finite(summaryDf$energy),]$energy <- 0 }
  ## </hack> ##
  g <- ggplot(aes(x=time,y=energy), data=data.frame(subset(summaryDf, agent %in% agents))) + geom_line(aes(group=agent, color=agent), alpha=0.5) + geom_smooth(se=F,size=1, method=method)
  return(g)
}

##
## plots success distribution over R runs
##
plotSuccessDist <- function(runsDf) {
  g <- ggplot(aes(x=meanSuccess), data=runsDf) + geom_histogram(aes(fill = ..count..)) + labs(title = "Success distribution") + xlab("Success")
  return(g)
}


##
## plots size distribution over R runs
##
plotSizeDist <- function(runsDf) {
  g <- ggplot(aes(x=meanSize), data=runsDf) + geom_histogram(aes(fill = ..count..)) + labs(title = "Size distribution") + xlab("Size")
  return(g)
}


##
## plots energy distribution over R runs
##
plotEnergyDist <- function(runsDf) {
  g <- ggplot(aes(x=meanEnergy), data=runsDf) + geom_histogram(aes(fill = ..count..)) + labs(title = "Energy distribution") + xlab("Energy")
  return(g)
}


##
## for debugging only
##
eProb <- function(df) {
   a<-df$F1bark 
   b<-df$F2prime
   pairs <- data.frame(F1=a,F2prime=b)
   z <- ddply(pairs, .(), function(d) if (nrow(d) == 1) NULL
             else {
               row_pairs <- combn(nrow(d),2)
               cbind( a = d[ row_pairs[1,], ],
                      b = d[ row_pairs[2,], ] )
             })[, -1]    
  for(i in 1:nrow(z)) {print(1/vowelDist(z[i,])^2)} 
}
