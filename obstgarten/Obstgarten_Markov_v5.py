#!/usr/bin/env python
# coding: utf-8

# In[5]:


"""
Program: Obstgarten Markov Chain analysis
Author: Jonas Schumacher [jonas-schumacher on Github]
"""

"""
Import libraries
"""
import numpy as np
import pandas as pd
import sys
import time
import datetime

# Jupyter parameters
pd.set_option('display.max_columns', 20)

# Measure time 
time_start = time.time()

"""
Define possible states
"""
print('definition: [fullest tree, 2nd fullest tree, 3rd fullest tree, emptiest tree, crow]')
print('start: [10, 10, 10, 10, 9]')
print('victory : [0, 0, 0, 0, x_e], where x_e > 0')
print('defeat: [x_a, x_b, x_c, x_d, 0], where at least one x_i > 0')

"""
Set game parameters
>> Uncomment the strategy you want to use
>> Caution: random calculation takes a long time due to additional calculations
"""
num_fruit = 10
num_raven = 9
num_basket = 2
strategy = 'positive'
#strategy = 'negative'
#strategy = 'random'


# In[6]:


"""
Set all possible states (as list):
""" 
print('Initialize all states ... ')

current = [10, 10, 10, 10, 9]
states = []

states_transitive = []
states_victory = []
states_defeat = []
states_impossible = []

index_transitive = []
index_victory = []
index_defeat = []
index_impossible = []

counter = 0

for a in range(num_fruit,-1,-1):
    current[0] = a
    for b in range(a,-1,-1):
        current[1] = b
        for c in range(b,-1,-1):
            current[2] = c
            for d in range(c,-1,-1):
                current[3] = d
                # e is the raven and therefore independent from the rest
                for e in range(num_raven,-1,-1):
                    current[4] = e
                    
                    # CASE DISTINCTION
                    
                    # Impossible state:
                    if np.logical_and(sum(current[0:4]) == 0, current[4] == 0):
                        index_impossible.append(counter)
                        states_impossible.append(current)
                    # Victory
                    elif np.logical_and(sum(current[0:4]) == 0, current[4] != 0):
                        index_victory.append(counter)
                        states_victory.append(current)
                    # Defeat
                    elif np.logical_and(sum(current[0:4]) != 0, current[4] == 0):
                        index_defeat.append(counter)   
                        states_defeat.append(current)
                    # Transitive
                    else:
                        index_transitive.append(counter)
                        states_transitive.append(current)
                        #print('Transitiv')
                    states.append(current)
                    counter += 1
                    current = current[:]
                    
print('Transitive states: ' + str(len(states_transitive)))
print('Victorious states: ' + str(len(states_victory)))
print('Defeated states: ' + str(len(states_defeat)))
print('Unreachable states: ' + str(len(states_impossible)))

"""
Create transition matrix
"""
states_string = []

for i in states:
    states_string.append(str(i))

P = pd.DataFrame(index = states_string, columns = states_string)
P.iloc[:,:] = 0

print('Number of total states: ' + str(P.shape[0]) + ' [' + str(P.shape[0]-1) + ' without the impossible one]')
print('Size of array in memory: ' + str(sys.getsizeof(P)))


# In[7]:


"""
Fill transition matrix:
"""

"""
Step 1: Calculate transition probabilities
"""
print('Fill transitive states: ')
time_before = time.time()
time_after = time.time()
count = 0
times = []

for incoming in states_transitive:
    if count % 1000 == 0:
        print(count)
        time_after = time.time()
        difference = time_after-time_before
        #print(difference)
        times.append(difference)
        time_before = time_after
    count += 1
    """ 
    Case distinction: 
    1) Regular fruit
    2) Crow
    3) Basket
    """
    
    """
    Case 1: Regular fruit, i.e. 4 possible transitions >> i = 0,1,2,3
    All of these in-out-combinations get probability +1/6 (here +1, because we'll divide by 6 later) 
    """
    for i in range(0,4):
        outgoing = incoming[:]                                  # erzeuge Kopie
        outgoing[i] = max(outgoing[i]-1,0)                      # reduziere bestimmten Baum um eine Frucht
        outgoing[0:4] = sorted(outgoing[0:4], reverse = True)   # sortiere Bäume absteigend
        
        P.loc[str(incoming),str(outgoing)] = P.loc[str(incoming),str(outgoing)] + 1
        
    """
    Case 2: Crow >> Reduce crow by 1, if possible
    """
    outgoing = incoming[:]
    outgoing[4] = max(outgoing[4]-1,0) 
    
    P.loc[str(incoming),str(outgoing)] = P.loc[str(incoming),str(outgoing)] + 1
    
    """
    Case 3: Basket: pick 2 fruits
    - strategy "positive": always pick "fullest" tree
    - strategy "negative": always pick "emptiest" tree
    - strategy "random": pick tree randomly
    """

    # Positive & negative relatively simple calculation 
    outgoing = incoming[:]                                      # create copy
    
    if strategy == 'positive':
        for i in range(0,num_basket):
            outgoing[0] = max(outgoing[0]-1,0)                      # reduce 1st (fullest) tree
            outgoing[0:4] = sorted(outgoing[0:4], reverse = True)   # re-sort tree in descending order
        P.loc[str(incoming),str(outgoing)] = P.loc[str(incoming),str(outgoing)] + 1
            
    elif strategy == 'negative':
        for i in range(0,num_basket):
            if outgoing[3] != 0:                            # reduce emptiest tree (index = 3), if possible
                outgoing[3] = max(outgoing[3]-1,0)
            elif outgoing[2] != 0:                          # otherwise the 2nd emptiest, etc.
                outgoing[2] = max(outgoing[2]-1,0)
            elif outgoing[1] != 0:
                outgoing[1] = max(outgoing[1]-1,0)
            else:
                outgoing[0] = max(outgoing[0]-1,0) 
            outgoing[0:4] = sorted(outgoing[0:4], reverse = True)
        P.loc[str(incoming),str(outgoing)] = P.loc[str(incoming),str(outgoing)] + 1
    
    # Now it's getting complicated: there are several possible outgoing states
    elif strategy == 'random':
        current_outgoing_list = []
        
        # Create nested list with one layer (consisting of outgoing state and proba) for each element in the basket
        current_outgoing_list.append([[outgoing,1]])
        
        for i in range(0,num_basket):
            
            # Append new list to main list for every basket
            current_outgoing_list.append([])
            
            # Iterate over all outgoing states:
            for zu in current_outgoing_list[i]:
                outgoing = zu[0].copy()
                prob_outgoing = zu[1]

                # If all 4 trees carry fruits, then prob = 1/4
                if outgoing[3] != 0:
                    outgoing_temp = outgoing.copy()
                    outgoing_temp[3] = max(outgoing_temp[3]-1,0)
                    outgoing_temp[0:4] = sorted(outgoing_temp[0:4], reverse = True)
                    current_outgoing_list[i+1].append([outgoing_temp,prob_outgoing*1/4])
                    outgoing_temp = outgoing.copy()
                    outgoing_temp[2] = max(outgoing_temp[2]-1,0)
                    outgoing_temp[0:4] = sorted(outgoing_temp[0:4], reverse = True)
                    current_outgoing_list[i+1].append([outgoing_temp,prob_outgoing*1/4])
                    outgoing_temp = outgoing.copy()
                    outgoing_temp[1] = max(outgoing_temp[1]-1,0)
                    outgoing_temp[0:4] = sorted(outgoing_temp[0:4], reverse = True)
                    current_outgoing_list[i+1].append([outgoing_temp,prob_outgoing*1/4])
                    outgoing_temp = outgoing.copy()
                    outgoing_temp[0] = max(outgoing_temp[0]-1,0)
                    outgoing_temp[0:4] = sorted(outgoing_temp[0:4], reverse = True)
                    current_outgoing_list[i+1].append([outgoing_temp,prob_outgoing*1/4])
                # 3 fruits = 1/3
                elif outgoing[2] != 0:
                    outgoing_temp = outgoing.copy()
                    outgoing_temp[2] = max(outgoing_temp[2]-1,0)
                    outgoing_temp[0:4] = sorted(outgoing_temp[0:4], reverse = True)
                    current_outgoing_list[i+1].append([outgoing_temp,prob_outgoing*1/3])
                    outgoing_temp = outgoing.copy()
                    outgoing_temp[1] = max(outgoing_temp[1]-1,0)
                    outgoing_temp[0:4] = sorted(outgoing_temp[0:4], reverse = True)
                    current_outgoing_list[i+1].append([outgoing_temp,prob_outgoing*1/3])
                    outgoing_temp = outgoing.copy()
                    outgoing_temp[0] = max(outgoing_temp[0]-1,0)
                    outgoing_temp[0:4] = sorted(outgoing_temp[0:4], reverse = True)
                    current_outgoing_list[i+1].append([outgoing_temp,prob_outgoing*1/3])
                # prob = 1/2
                elif outgoing[1] != 0:
                    outgoing_temp = outgoing.copy()
                    outgoing_temp[1] = max(outgoing_temp[1]-1,0)
                    outgoing_temp[0:4] = sorted(outgoing_temp[0:4], reverse = True)
                    current_outgoing_list[i+1].append([outgoing_temp,prob_outgoing*1/2])
                    outgoing_temp = outgoing.copy()
                    outgoing_temp[0] = max(outgoing_temp[0]-1,0)
                    outgoing_temp[0:4] = sorted(outgoing_temp[0:4], reverse = True)
                    current_outgoing_list[i+1].append([outgoing_temp,prob_outgoing*1/2])
                # prob =  1
                else:
                    outgoing_temp = outgoing.copy()
                    outgoing_temp[0] = max(outgoing_temp[0]-1,0)
                    outgoing_temp[0:4] = sorted(outgoing_temp[0:4], reverse = True)
                    current_outgoing_list[i+1].append([outgoing_temp,prob_outgoing*1])
                      
        # The list contains the relevant states at the very end
        # With 2 baskets we have 4*4 possible outgoing states (some appear multiple times)
        # Plausbility check: all probas must add up to 1
                
        outgoing_dict = {}
        # Access elements at the end of the list [num_basket]
        for jga in current_outgoing_list[num_basket]:
            outgoing = jga[0].copy()
            outgoing_str = str(outgoing)
            if outgoing_str in outgoing_dict:
                outgoing_dict[outgoing_str] += jga[1]
            else:
                outgoing_dict[outgoing_str] = jga[1]
        
        # Now iterate over the dict
        cumulated_proba = 0
        for outgoing_str in outgoing_dict:
            cumulated_proba += outgoing_dict[outgoing_str]
            P.loc[str(incoming),outgoing_str] += outgoing_dict[outgoing_str]
    # This should never happen
    else:
        outgoing[0] = max(outgoing[0]-1,0)
        print('ERROR!')
        
        
"""
Step 2: Fill absorbing states
""" 
print('Fill absorbing states: ')
for incoming in states_victory:
    P.loc[str(incoming),str(incoming)] = P.loc[str(incoming),str(incoming)] + 6
for incoming in states_defeat:
    P.loc[str(incoming),str(incoming)] = P.loc[str(incoming),str(incoming)] + 6
for incoming in states_impossible:
    P.loc[str(incoming),str(incoming)] = P.loc[str(incoming),str(incoming)] + 6
    
    
"""
Step 3: Finalize transition matrix
""" 
P = P/6
row_sum = P.sum(axis = 1)
problematic_rows = (row_sum.values != 1.0).sum()
#print(problematic_rows)

# Failing plausi-check might be due to rounding errors (because of dividing by 6)!
if (problematic_rows == 0):
    print('plausi-check passed')
else:
    print('plausi-check failed')


# In[8]:


"""
Calculate probability for entering the stationary set
>> It suffices to calculate the winning probability
"""
# The transitive matrix is always the same
P_transitive = P.iloc[index_transitive,index_transitive].copy(deep = True)
P_transitive = P_transitive-np.identity(P_transitive.shape[0])
#P_transitiv.head()

"""
Iterate over all victorial states:
"""
winning_proba = 0
for relevant in states_victory:
    print('Analyze victory state ' + str(relevant) + ' = ', end = '')
    
    # Write relevant column - i.e. the result vector
    relevant_column = P.iloc[index_transitive,states.index(relevant)].copy(deep = True)
    
    """
    Solve linear system of equations
    """
    x = np.linalg.solve(P_transitive.values,-relevant_column.values)
    
    print('{:.2f}'.format(round(100*x[0],2)) + '%')
    winning_proba += x[0]
print('Winning probability with start in state ' + str(states[0]) + ' = ')
print('{:.2f}'.format(round(100*winning_proba,2)) + '%')


# In[9]:


time_end = time.time()
time_overall = time_end - time_start
print('Overall duration of analysis: ' + str(datetime.timedelta(seconds=time_overall)))

