'''
vowel system simulation based on deBoer (2000) J. Phonetics
article, with small changes from two sources:

1. deBoer (1999) book
2. Java implementation by Julian Bradfield (Edinburgh)

Author: Morgan, 7/2013

run with -h flag for information on all parameters, including default
values for each parameter:
> python deboer.py -h

sample run, for 5000 its (total) for 20 agents, all other parameters at default values, store log in sample.csv:
> python deboer.py --nIts 5000 --nAgents 20 sample.csv

'''

import random, itertools, csv, argparse, itertools, math, copy
import os.path as path


## parse command line arguments
##


parser = argparse.ArgumentParser(description = 'de boer model simulation')
parser.add_argument('--nIts', type = int, default = 10000, help = 'number of interactions between agents (default: %(default)s)')

parser.add_argument('--nRuns', type = int, default = 1, help = 'number of runs of the whole game (default: %(default)s)')

parser.add_argument('csvF', help = '.csv file to output to')

parser.add_argument('--noise', type = float, default = 0.1, help = 'amount of acoustic noise (deboer: varies; default: %(default)s)')

parser.add_argument('--nAgents', type = int, default = 5, help = 'number of agents (deboer: 20; default: %(default)s)')

parser.add_argument('--discardThresh', type=float, default=0.7, help = 'success/uses ratio under which vowels are discarded (deboer: 0.7; default: %(default)s)')

parser.add_argument('--successThresh', type=float, default=0.5, help = 'success/uses ratio under which vowel added (deboer: 0.5; default: %(default)s)')

parser.add_argument('--minUsesDiscard', type = int, default = 5, help = 'minimum number of times a vowel must be used to consider discarding (deboer: 5; default: %(default)s)')

parser.add_argument('--acousticMergeThresh', type=float, default=1.0, help = 'perceptual distance under which vowels merged (deboer: not defined; default: %(default)s)')

parser.add_argument('--articMergeThresh', type=float, default=0.17, help = 'euclidean distance in articulatory space space under which vowels merged (deboer: n.d. in article, 0.17 in book; default: %(default)s)')

parser.add_argument('--articEps', type=float, default=0.03, help = 'how much to shift by, in articulatory space, when calculating neighbors (deboer: 0.1; default: %(default)s)')

parser.add_argument('--L', type=float, default=0.3, help='lambda: weighting of F2\' difference vs F1 difference in calculating perceptual distance (deboer: 0.3; default: default: %(default)s)')

## deboer says something weird about this
parser.add_argument('--additionProb', type=float, default=0.005, help = 'probability with which an agent adds a random new vowel (deboer: 0.01; default: %(default)s)')

parser.add_argument('--cleanUpProb', type=float, default=1.0, help = 'probability with which an agent cleans up (discards and merges) in each round (deboer: n.d. in article, 0.1 in book; default: %(default)s)')

parser.add_argument('--storeIvl', type=int, default=100, help = 'write info to CSV every storeIvl iterations (default: %(default)s)')

parser.add_argument('--verbose', action='store_true', help = "verbose output (default: false)")

args = parser.parse_args()

## for convenience
nIts, noise, verbose, L, articEps = args.nIts, args.noise, args.verbose, args.L, args.articEps



# class for a vowel
class Vowel:
    ## initialize with no articulation, formants, or label
    def __init__(self):
        self.art = ['','','']
        self.form = ['','','','']
        self.label = ''

    ## return formants with noise added
    def production(self):
        return [f*(1+random.uniform(-noise/2,noise/2)) for f in self.form]

    
    ## shift this vowel closer to formants A
    ##
    def shiftCloser(self, A):
        ## find 6 closest neighbors
        neighbs  = neighbors(self.art)

        ## find which of these directions, if any, is closer to A, and
        ## shift vowel in the best direction (if any)
        bestV = (self.art, self.form)
        minDist = acousticDistance(A, self.form)
        
        for n in neighbs:
            if acousticDistance(A, n[1]) < minDist:
                minDist = acousticDistance(A, n[1])
                bestV = n
                
        self.art, self.form = bestV[0], bestV[1]

## END VOWEL CODE
##


## class for an agent
class Agent:
    ## start out with an empty inventories
    def __init__(self, id):
        self.id = id
        self.v = []
        self.labels = []
        self.useCount = {}
        self.successCount = {}

##
## add random vowel to agent's inventory
##
    def addRandomVowel(self):
        vow = Vowel()

        ## random vowel
        vow.art= [random.random(), random.random(), random.random()]

        ## find its label and formant frequencies
        vow.label = max(self.labels)+1 if self.v else 1
        vow.form = calFormFreq(vow.art)

        ## update agent's vowel inventory and counters
        self.v.append(vow)
        self.labels.append(vow.label)
        self.useCount[vow.label] = 0
        self.successCount[vow.label] = 0
        if verbose:
                print "agent %s randomly added a vowel" % self.id

## add non-random new vowel to agent's inventory
##                
    def addNewVowel(self, newV):
        ## rename this vowel
        newVLabel = max(self.labels)+1 if self.v else 1
        newV.label = newVLabel 

        ## add the vowel to the inventory
        self.v.append(newV)
        self.labels.append(newVLabel)
        self.useCount[newVLabel] = 0
        self.successCount[newVLabel] = 0
        if verbose:
                print "agent %s non-randomly added a vowel" % self.id
        #self.v.append(

## step 1 of the imitation game (agent 1)
##
    def step1(self):
        ## if no vowels in inventory, add a random one
        if not self.v:
            self.addRandomVowel()

        ## choose a random vowel from the inventory, increment its use
        ## count
        randomV = random.choice(self.v)
        self.useCount[randomV.label] += 1

        ## return vowel's label plus formants+noise
        return randomV.label, randomV.production()

    ## step 2 of the imitation game (agent 2)
    ##
    ## A1: formants of production by agent 1
    def step2(self, A1):
        
        ## if no vowel in inventory, adds the perceptually closest one
        ## to A1 by talking to herself
        if not self.v:
            vNew = self.findPhoneme(A1)
            self.addNewVowel(vNew)

        ## find the perceptually closest vowel in inventory to A1
        closest = ''
        minDist = 10000
        for vowel in self.v:
            curDist = acousticDistance(vowel.form, A1)
            if(curDist < minDist):
                minDist = curDist
                closest = vowel

        ## return production with noise of this vowel, plus the vowel itslef
        return closest.production(), closest


    ## step 3 of the imitation game (agent 1)
    ##
    ## lab1: label of production by agent 1
    ## A2: formants of production by agent 2
    def step3(self, lab1, A2):
        ## find the perceptually closest vowel in inventory to A2
        closest = ''
        minDist = 10000
        for vowel in self.v:
            curDist = acousticDistance(vowel.form, A2)
            if(curDist < minDist):
                minDist = curDist
                closest = vowel

        ## if that vowel is the one used in step 1, success; else, failure.
        if(lab1 == closest.label):
            success = True
            self.successCount[lab1] += 1
        else:
            success = False
        return success

    '''
    step4 of the imitation game (agent 2)
    
    success: see step3
    myV: vowel produced in step2
    A1: formants of production by agent 1 in step1
    '''
    def step4(self, success, myV, A1):
        ## increment use count for this vowel
        self.useCount[myV.label] += 1

        ## if interaction was successful, shift this vowel closer to
        ## A1, and increment success count.
        if success:
            myV.shiftCloser(A1)
            self.successCount[myV.label] += 1
        ## otherwise, if success ratio high enough, add a new vowel
        ## near A1. if it's not, just shift this vowel closer to A1.
        else:
            if float(self.successCount[myV.label])/self.useCount[myV.label] > args.successThresh: # backwards in paper (p. 451)
                vNew = self.findPhoneme(A1)
                self.addNewVowel(vNew)
            else:
                myV.shiftCloser(A1)

    '''
    find a vowel near a signal A (formants), by talking to self.
    '''
    def findPhoneme(self, A):
        ## start from schwa
        v = Vowel()
        v.art = [0.5, 0.5, 0.5]
        v.form = calFormFreq(v.art)

        ## shift closer to A using shiftCloser until converge on a
        ## point where all neighbors are no closer to A.
        newArt = [0.5, 0.5, 0.5]
        v.shiftCloser(A)

        while(newArt != v.art):
            newArt = v.art
            v.shiftCloser(A)

        ## return a new vowel with the articulation and formants
        ## converged on.
        vNew = Vowel()
        vNew.art = newArt
        vNew.form = calFormFreq(newArt)

        return(vNew)
        
    """
    remove a vowel from the inventory
    """
    def removeVowel(self, vow):
        lab = vow.label
        if verbose:
            uses, successes = self.useCount[lab], self.successCount[lab]
            if(uses):
                print "agent %s removed a vowel with uses=%d, successes=%d, ratio=%f" % (self.id, uses, successes, float(successes)/uses)
            else:
                print "agent %s removed a vowel with uses=%d, successes=%d" % (self.id, uses, successes)
        self.v.remove(vow)
        del self.useCount[lab]
        del self.successCount[lab]
        self.labels.remove(lab)
        
    '''
    do other updates (Table V, p. 451)
    '''
    def doOtherUpdates(self):
        ## the book says to only 'clean up' on 10% of games, i think meaning this.
        if(random.random() < args.cleanUpProb):

            ## 1. remove vowels that have been used enough times to
            ## be judged, and whose successes/uses ratio is too low.
            for vow in self.v:
                lab = vow.label
                uses = self.useCount[lab]
                if uses > args.minUsesDiscard and float(self.successCount[lab])/uses < args.discardThresh:
                    self.removeVowel(vow)

            ## 2. add random vowel with some probability
            if(random.random() < args.additionProb):
                self.addRandomVowel()

            ## 3. merge vowels that are too close
            self.merge()

    '''
    Merge vowels that are too close.  deBoer leaves exactly how this
    is done ambiguous, saying only to consider all possible pairs of
    vowels.  There are two issues which come up in doing so which he
    doesn't discuss; we've chosen the fixes described below.
    '''
    def merge(self):
        ## deboer says to try *all* vowel pairs. but it's possible to
        ## want to merge (1,2) and (2,3), but once merged (1,2) and
        ## discarded 2 the latter doesn't make sense. What to do in
        ## this situation?  We use a dumb recursive merge:
        ## 1. make a list of all vowel pairs close enough to be merged
        ## 2. pick one pair at random, and merge them, deleting vowel X
        ## from the inventory
        ## 3. consider all pairs again, from a list with X removed.
        ## 4. If there are still pairs close enough to be merged, go to step 2.
        ## if not, we're done.
        ##

        ## helper function to find all vowel pairs close enough to be merged
        ##
        ## another issue comes up here: we're going to decide which
        ## vowel in a pair should be deleted by comparing
        ## successes/uses ratios, but they're undefined if uses=0.
        ## What we'll do is automatically choose the vowel with uses=0
        ## to be deleted if its the member of a pair to be merged.
        def helper(v):
            toMerge = []
            for (v1,v2) in itertools.combinations(v,2):
                if((acousticDistance(v1.form, v2.form) < args.acousticMergeThresh) or
                   (articDistance(v1.art, v2.art)<args.articMergeThresh)):
                    toMerge.append((v1,v2))
            return toMerge

        toMerge = helper(self.v)

        ## while there are vowels to be merged
        while(toMerge):
            ## choose a pair to merge, at random, from those close enough
            v1, v2 = random.choice(toMerge)
            lab1, lab2 = v1.label, v2.label
            uses1, uses2 = self.useCount[v1.label], self.useCount[v2.label]
            acDist = acousticDistance(v1.form, v2.form)
            arDist = articDistance(v1.art, v2.art)

            # if both have uses=0 or if v2 alone does, discard v2
            if(uses1==0 or uses2==0):
                if(uses2==0):
                    self.successCount[lab1] += self.successCount[lab2]
                    self.useCount[lab1] += uses2
                    self.removeVowel(v2)
                ## if v1 alone has uses=0, discard v1
                else:
                    self.successCount[lab2] += self.successCount[lab1]
                    self.useCount[lab2] += uses1
                    self.removeVowel(v1)
                if verbose:
                    print "agent %s merged vowels %d and %d with %d and %d uses" % (self.id, lab1, lab2, uses1, uses2)
                    print "acoustic dist = %f, artic dist = %f" % (acDist, arDist)
            else:
                ## compute the success/uses ratio for each vowel
                ratio1 = float(self.successCount[lab1])/uses1
                ratio2 = float(self.successCount[lab2])/uses2

                ## remove the 'worse' vowel by this measure, giving its
                ## successes and uses to the other vowel
                if(ratio1 < ratio2):
                    self.successCount[lab2] += self.successCount[lab1]
                    self.useCount[lab2] += uses1
                    self.removeVowel(v1)
                else:
                    self.successCount[lab1] += self.successCount[lab2]
                    self.useCount[lab1] += uses2
                    self.removeVowel(v2)
                if verbose:
                    print "agent %s merged vowels %d and %d with %d and %d uses" % (self.id, lab1, lab2, uses1, uses2)
                    print "acoustic dist = %f, artic dist = %f, ratio1 = %f, ratio2 = %f" % (acDist, arDist, ratio1, ratio2)

            ## check if there are still pairs to be merged
            toMerge = helper(self.v)
       
## END AGENT CODE
##

## calculate bark (formula from de Boer)
##
## f: Hz
## output: bark
def bark(f):
    if f>271.32:
        return math.log(f/271.32)/0.1719 + 2
    else:
        return (f-51)/110

## articulatory synthesizer from deBoer
##
## v: articulation of a vowel ([height, backness, roundness] list)
## output: F1-F4
##
def calFormFreq(v):
    h = v[0]
    b = v[1]
    r = v[2]
    formants = [0,0,0,0]
    formants[0] = int(((- 392+ 392*r)*(h*h) + ( 596- 668*r)*h + (- 146+ 166*r))*(b*b)  + (( 348- 348*r)*(h*h) + (- 494+ 606*r)*h + ( 141- 175*r))*b + (( 340-  72*r)*(h*h) + (- 796+ 108*r)*h + ( 708-  38*r)))
    formants[1] =  int(((-1200+1208*r)*(h*h) + (1320-1328*r)*h + (  118- 158*r))*(b*b) + ((1864-1488*r)*(h*h) + (-2644+1510*r)*h + (-561+ 221*r))*b + ((-670+ 490*r)*(h*h) + ( 1355- 697*r)*h + (1517- 117*r)))
    formants[2] = int(((  604- 604*r)*(h*h) + (1038-1178*r)*h + (  246+ 566*r))*(b*b) + ((-1150+1262*r)*(h*h) + (-1443+1313*r)*h + (-317- 483*r))*b + ((1130- 836*r)*(h*h) + (- 315+  44*r)*h + (2427- 127*r)))
    formants[3] = int(((-1120+  16*r)*(h*h) + (1696- 180*r)*h + (  500+ 522*r))*(b*b) + ((- 140+ 240*r)*(h*h) + (- 578+ 214*r)*h + (-692- 419*r))*b + ((1480- 602*r)*(h*h) + (-1220+ 289*r)*h + (3678- 178*r)))
    return formants


## calculate effective second-formant frequency (p. 448)
##
## input: [F1, F2, F3, F4] (in Hz)
## output: F2' (in bark)
##
def F2prime(formants):
    c = 3.5
    
    F1, F2, F3, F4 = bark(formants[0]), bark(formants[1]), bark(formants[2]), bark(formants[3])

    w1 = (c - F3+F2)/c
    w2 = (F4-2*F3+F2)/(F4-F2)

    if F3-F2 >c:
        F2prime = F2
    elif (F3-F2)<=c and (F4-F2)>c:
        F2prime = ((2-w1)*F2 + w1*F3)/2.0
    elif (F4-F2)<=c and (F3-F2)<(F4-F3):
        F2prime = (w2*F2 + (2-w2)*F3)/2.0 - 1.0
    elif (F4-F2)<=c and (F3-F2)>=(F4-F3):
        F2prime = ((2+w2)*F3 - w2*F4)/2.0 - 1.0
    else:
        print "PROBLEM" # should never get here

    return F2prime

## calculate perceptual distance between two vowels (p. 449)
##
## form1, form2: 2 sets of formants (Hz)
##
def acousticDistance(form1, form2):
    ## formants in bark
    F1a, F1b = bark(form1[0]), bark(form2[0])
    F2primea, F2primeb = F2prime(form1), F2prime(form2)

    return math.sqrt((F1a - F1b)**2 + L*(F2primea - F2primeb)**2)

## articulatory distance (euclidean distance along artic dimensions)
## art1, art2: articulations of two vowels ([height, backness, roundness] lists)
## 
def articDistance(art1, art2):
    return math.sqrt((art1[0] - art2[0])**2 + (art1[1] - art2[1])**2 + (art1[2] - art2[2])**2)


## return (up to) 6 neighbors of this articulation, and their
## corresponding formant values
##
## Ex: [0.2, 0.5, 1] for articEps = 0.1 has 5 neighbors:
##  -- [0.1, 0.5, 1], [0.3, 0.5, 1], [0.2, 0.4, 1], [0.2, 0.6, 1], [0.2, 0.5, 0.9]
def neighbors(art):
    neighbs = []
    ## for height, back, roundness
    for i in [0,1,2]:
        ## subtract articEps from this dimension if not 0, but set to
        ## 0 if you would get number <0
        if art[i]>0:
            temp = copy.copy(art)
            temp[i] = (art[i]-articEps) if art[i]>articEps else 0
            neighbs.append(temp)
        ## add articEps from this dimension if not 1, but set to
        ## 1 if you would get a number >1
        if art[i]<1:
            temp = copy.copy(art)
            temp[i] = (art[i]+articEps) if art[i]<(1-articEps) else 1
            neighbs.append(temp)
    
    return zip(neighbs, [calFormFreq(nb) for nb in neighbs])


###
### play the imitation game
###
def game():
    ## write to the csv file every storeIvl iterations, plus last one
    storeIts = range(0, nIts, args.storeIvl)
    storeIts = storeIts[1:]

    if(not (nIts in  storeIts)):
        storeIts.append(nIts)


    ## start CSV file
    csvfile =  open(path.abspath(args.csvF), 'w')
    w = csv.writer(csvfile)
    w.writerow(['run', 'time','agent','vowel id','height','backness','rounding','F1','F2','F3','F4', 'F2prime', 'UseCount', 'SuccessCount'])


    for i in range(args.nRuns):
        runNum = i+1

        print "run %d" % runNum

        ## initialize agents
        agents = [Agent(str(i+1)) for i in range(args.nAgents)]

        ## initialize number of interactions
        time = 1

        ## pick two agents to interact
        a1, a2 = random.sample(agents,2)
	
        for x in range(nIts):
            ## print status every so often
            ##if(x%100 == 0 and x>0):
            ##    print x

            ## play step 1
            ##
            ## lab1 = label of intended vowel, A1 = formants produced by
            ## agent 1 (incl noise)
            lab1, A1 = a1.step1()

            ## play step 2
            ##
            ## A2 = produced formants (incl noise), v2 = vowel agent 2
            ## produces
            A2, v2 = a2.step2(A1)

            ## play step 3, return whether game was a success
            ## 
            success = a1.step3(lab1, A2) # resp2: True (success) or False (failure)

            ## play step 4
            a2.step4(success, v2, A1)

            ## do discarding, mergers, random additions
            a1.doOtherUpdates()
            a2.doOtherUpdates()
            
            ## once every storeIvl iterations, write all agents' vowel
            ## prototypes to CSV
            if time in storeIts:
                for ag in agents:
                    for v in ag.v:
                        h, b, r = round(v.art[0],4), round(v.art[1],4), round(v.art[2],4)
                        w.writerow([runNum, time, ag.id, v.label, h, b, r, v.form[0], v.form[1], v.form[2], v.form[3], F2prime(v.form), ag.useCount[v.label], ag.successCount[v.label]])
                    
            ## pick two new agents to interact
            a1, a2 = random.sample(agents, 2)
            time += 1

    csvfile.close()

## executes game() with any command-line arguments if run from the
## command line, as expected
if __name__ == '__main__':
    game()

