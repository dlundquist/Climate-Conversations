import pdb
import pandas as pd
import time
import numpy as np
import os
from random import randint
from random import shuffle
import datetime
import collections
# Load the events database 

xlsx = pd.ExcelFile('data/firstHistoricClimateEvents.xlsx')
df = xlsx.parse(xlsx.sheet_names[0])
events = df.to_dict()
nevents = len(events['start year'])
earliestAge = 7
#print events.keys()    # We may want to change some of the key names to be more efficient for indexing!


#load temperature and sea ice datasets
temperatureFile = 'data/GLB.Ts+dSST.csv' # from  http://data.giss.nasa.gov/gistemp/
iceFile  = 'data/N_09_seaicearea_v2.txt' # from https://nsidc.org/data/seaice_index/archives.html
#process the temperature timeseries
yrTemp, AnnMeanT = np.genfromtxt(temperatureFile, unpack = True, skip_header = 3, delimiter = ',', usecols = (0,13), skip_footer = 1)
#compute the decadal average for temperature:
decadalT = np.reshape(AnnMeanT[:130], [13,10])
decadalT  = np.nanmean(decadalT, axis = 1)
decadalT = [float("{0:2f}".format(decadalT[i])) for i in range(len(decadalT))]
decadalT = np.asarray(decadalT)
#compute the 1881-1901 average
tempClimo = np.mean(AnnMeanT[:20])
#process the sea ice time series
yrIce, extent, area = np.genfromtxt(iceFile, unpack = True, usecols = (0,4,5), skip_footer = 14, skip_header = 1)
iceExtentClimo = np.mean(extent[:20]) #1979-1999 average
iceAreaClimo  = np.mean(area[:20]) 

# Set up global variables
delayinseconds = 1

# set up functions
def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def getplayerinfo():
    # Get input from user (name, birthdate, number of rounds) 
    names = []      # initialize here so it resets if re-asking
    birthyears = []
    if test == 1:
        nplayers = 4
        nrounds = 1
        names.append('Judy')
        names.append('Rachel')
        names.append('Michelle')
        names.append('Katie')
        birthyears.append(1982)
        birthyears.append(1986)
        birthyears.append(1988)
        birthyears.append(1992)

    else:
        nplayers  = int(raw_input('How many people are in the conversation? '))
        nrounds = int(raw_input('How many rounds would you like to play? '))

        # Work out how long to delay between questions
        delayinseconds = 1

        indices = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th']
        for i in range(nplayers):
            thisname = raw_input('Please enter the ' + indices[i] + ' players name: ')
            names.append(thisname)
            

            needage = True
            while needage:
                thisage = raw_input('Please enter ' + thisname + '\'s year of birth: ')

                if is_number(thisage):
                    while (int(thisage) < 1880 or int(thisage) > datetime.datetime.now().year):
                        thisage = raw_input('You are either over 130 years old, or haven\'t been born yet. Please re-enter ' + thisname + '\'s players year of birth: ')
                    birthyears.append(int(thisage))
                    needage = False
                else:
                    print('Please enter a number, for example, 1980')   
                
    return(nplayers,nrounds,names,birthyears)   # return these variables so they are globally known

def getgameinfo():
    test  = int(raw_input('Is this a test run? 1= yes, 0 = no '))
    needgame = True
    while needgame:
        game  = raw_input('Would you like to play for points? yes/no? ')
        if game in ('yes','Yes'):
            needgame = False
            isgame = True
        elif game in ('no','No'):
            needgame = False
            isgame = False
        else:
            print('Sorry, I didn\'t understand that, please answer yes or no')
    return(test,isgame)


def getevent(k,ievents):
    check = True
    itcheck = 0
    while check:
        ind = randint(0,nevents-1)
        #check that the date is appropriate and index is unused
        if birthyears[k] + earliestAge < events['start year'][ind]:
            if ind not in ievents:
                check = False
                ievents.append(ind)
        itcheck += 1
        if itcheck > maxchecks:
            exit('I\'m sorry, we\'ve run out of events for your group!')
    return(ind)



# Main program
print('Welcome! Lets get a little information before we start the conversation.')

needinfo = True
while needinfo:
    test,isgame = getgameinfo()
    nplayers,nrounds,names,birthyears = getplayerinfo()
    # Print out a summary of players and dates of birth
    os.system('clear')
    print('These are the players for this game:')
    for i in range(nplayers):
        print(names[i] + ', born in ' + str(birthyears[i]))
    print(' ')
    print('You want to play ' + str(nrounds) + ' rounds')
    print(' ')
    if isgame:
        print('You want to play against the game for points')
    else:
        print('You want to play without scoring')
    print(' ')
    correctinput = raw_input('Is this correct? Yes/No? ')

    while correctinput not in ['Yes','yes']:
        if correctinput in ['No','no']:
            print('Ok, let\'s try again')
            break
        else:
            correctinput = raw_input('I\'m sorry, I didn\'t understand that. Is the game information correct, please enter Yes or No ')

    print(birthyears)
    print(list(set(birthyears)))
    if collections.Counter(list(set(birthyears))) != collections.Counter(birthyears) and isgame:    # if two people have same birth year, can't play as game
        needcheck = True
        while needcheck:
            check = raw_input('Sorry, you have two people in your group born in the same year, you cannot play for points! Press 0 to restart with a different team, and 1 to continue playing without scoring ')
            if check == '0':
                needcheck = False
            elif check == '1':
                needinfo = False
                isgame = False
                needcheck = False
            else:
                print('Sorry, I didn\'t catch that, please enter 0 or 1')   
# Each user gets a set of indices for the events
    else:
        needinfo = False

    print(needinfo)

ievents = []

os.system('clear')

maxchecks = nevents*2

#TODO:  improve use of the climate indices
# if there's not at least a 20 year gap in age, then maybe an historical reference point to associate to the first date. 
#  i.e. Washington statehood, Gold Rush, Railroads, Hindenberg, women's suffrage, Spruce Goose, World's fair in Seattle, issaquah mining boom, closing of washington mines 
ageGap = max(birthyears) - min(birthyears)
iOldest = np.argmin(birthyears)
iYoungest = np.argmax(birthyears)
print('Before starting the rounds, lets reflect on a few big-picture measurements of Earth')
print()
#Temperature change
if ageGap >=20:
    TempChange = (AnnMeanT[yrTemp == birthyears[iOldest]] - AnnMeanT[yrTemp == birthyears[iYoungest]])*9/5
    print('Between  ' + names[iOldest] + ' and ' + names[iYoungest] + 's birthyears, global mean temperature rose by '+ str(TempChange) + 'degrees Fahrenheit.')
else:
    TempChange = (AnnMeanT[yrTemp == birthyears[iYoungest]] - AnnMeanT[0])*9/5
    print('When ' + names[iYoungest] + ' was born, the average annual temperature of the earths surface had risen ' + str(TempChange) + ' degrees Fahrenheit above its 1880 temperature, when the US census was just over 50 million people.')
#Sea Ice Change    
print
iceLow2012 = min(area)/iceAreaClimo*100
print('When ' + names[iOldest] + ' was '+ str(2012 - min(birthyears)) + ', the September arctic sea ice area dropped to a record low of ' + str(round(iceLow2012,1)) +  '% of its normal area.') 
pdb.set_trace()

# Loop over each user
if isgame:
    playerInds = []   # initialize list
    points = 0  # initialize points
    for j in range(0,nrounds):
        for k in range(0,nplayers): 
            playerInds.append(k)
    # now randomise this list
    shuffle(playerInds)
    print(playerInds)
    nquestions = len(playerInds)
    if nquestions != nplayers * nrounds:
        exit('something went terribly wrong with the player list!')

    for n in range(nquestions): 
        k = playerInds[n]
        ind = getevent(k,ievents)

        # display event, ask questions
        iyear = events['start year'][ind] - birthyears[k]
        print('In the year one player turned ' + str(iyear) + ', ' + events['description'][ind])
        print('What do you remember from the year you turned ' + str(iyear) + '?')
        print(' ')
        time.sleep(delayinseconds)
        needanswer = True
        
        while needanswer:
            answer = raw_input('Who do you think this question is talking about? ')
            if answer.lower() in [x.lower() for x in names]:    # case insensitive check
                needanswer = False
                if answer.lower() == names[k].lower():
                    print('Correct, it was ' + names[k])
                    time.sleep(delayinseconds)
                    points += 1
                else:
                    if nplayers > 2:
                        print('Sorry, it wasn\'t ' + answer + ', have another guess for half a point' )
                        answer = raw_input('Who is your second guess for who this question is talking about? ')
                        if answer.lower() == names[k].lower():
                            print('Correct, it was ' + names[k])
                            time.sleep(delayinseconds)
                            points += 0.5
                        else:
                            print('Sorry, it wasn\'t ' + answer + '; it was ' + names[k])
                            time.sleep(delayinseconds)
                    else:   # if only 2 players, don't allow a second guess!
                            print('Sorry, it wasn\'t ' + answer + '; it was ' + names[k])
                            time.sleep(delayinseconds)                            
            else:
                print('Please enter the name of one of the players: ' + ', '.join(names))

        os.system('clear')
    print ('You have a total of ' + str(points) + ' out of a possible ' + str(nrounds * nplayers) + ' points')
    if (float(points)/float(nrounds + nplayers) > 0.5):
        print('Congratulations!')

else:

    next = []
    for j in range(0,nrounds):
        for k in range(0,nplayers): # need to separate out the points version so it doesn't go through each in turn!
            # Determine the filter and selection of events
            ind = getevent(k,ievents)
            # display event, ask questions
            year = events['start year'][ind]
            iyear = events['start year'][ind] - birthyears[k]
            print('In the year ' + names[k] + ' turned ' + str(iyear) + ' ' + events['description'][ind])
            print(' ')
            # Have count-down time before asking question
            time.sleep(delayinseconds)
            questions = [ 'Do you remember hearing about this in the news?', \
            			  'Where were you in the year {}?'.format(year), \
            			  'Were there any special weather events where you lived in {}?'.format(year), \
            			  'Have you heard anything new about this type of event recently?', \
            			  'Who in the world does this event matter to most?', \
            			  'Did this impact any of your personal lives?']
            qind = randint(0,len(questions)-1)
            print(questions[qind])
            print(' ')
            # Have count-down time before prompting
            time.sleep(delayinseconds)
            raw_input('Press enter when you are ready to move on to the next question.')
            os.system('clear')


# After the loops it would be neat to close with a hopeful event, like the growth in renerable energy
# or the time series of CFC's which show the success of the montreal protocol
# or the  time series of sulfate particles so discuss the success of the clean air act


