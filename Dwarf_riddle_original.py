#!/usr/bin/env python
# coding: utf-8

# In[11]:


"""
Program: Dwarve riddle - original
Author: Jonas Schumacher [jonas-schumacher on Github]
"""

"""
Import libraries
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import datetime

# Measure time 
time_start = time.time()

"""
Set game parameters
num_dwarves = number of dwarves who have been to the central hall already
"""
num_dwarves = 100


# In[12]:


"""
Set all possible states (as list) and fill transition matrix:
States: 0x,1x,2x,3x (master dwarf has been to hall: light is off) + 0,1,2,3 (new dwarf has been to hall: light is on) 
"""

state_names = []
for i in range(num_dwarves):
    state_names.append(str(i))
    state_names.append(str(i)+'x')

P = pd.DataFrame(index = state_names, columns = state_names)
P.iloc[:,:] = 0

"""
Fill matrix linewise
""" 

# Initial state (no one has been to the hall)
P.iloc[0,1] = 1/num_dwarves
P.iloc[0,2] = 1-1/num_dwarves

# Probabilties after master dwarf has been to the hall
for i in range(1, 2*num_dwarves-1, 2):
    # either master dwarf enters room again or one of the dwarves who have been to the hall already
    P.iloc[i,i] = (i+1)/2/num_dwarves
    # new dwarf enters the hall
    P.iloc[i,i+1] = 1-(i+1)/2/num_dwarves
    
# In these states, the master dwarf needs to enter the hall:
for i in range(2, 2*num_dwarves-1, 2):
    P.iloc[i,i] = 1-1/num_dwarves
    P.iloc[i,i+1] = 1/num_dwarves
    
# Stationary state: Master dwarf enters the hall, afer every other dwarf has been to the hall
P.iloc[2*num_dwarves-1,2*num_dwarves-1] = 1

# Optionally print P
#print(P)


# In[13]:


"""
Calculate probability for entering the stationary set (should be 100% as this is the only stationary state!)
"""
# The transitive matrix is always the same
P_transitive = P.iloc[:-1,:-1].copy(deep = True)
P_transitive = P_transitive-np.identity(P_transitive.shape[0])

# Write relevant column - i.e. the result vector
relevant_column = P.iloc[:-1,-1].copy(deep = True)

#Solve linear system of equations
x = np.linalg.solve(P_transitive.values,-relevant_column.values)

print('{:.2f}'.format(round(100*x[0],2)) + '%')


# In[14]:


"""
Calculate average number of days until stationary set ist reached
"""
# The transitive matrix is always the same
P_transitive = P.iloc[:-1,:-1].copy(deep = True)
P_transitive = P_transitive-np.identity(P_transitive.shape[0])

#Solve linear system of equations
x = np.linalg.solve(P_transitive.values,-np.ones(P_transitive.shape[0]))

print(str(x[0]) + ' days')


# In[15]:


"""
OPTIONALLY PLOT THE DISTRIBUTION FOR A CERTAIN NUMBER OF DAYS PASSED
"""
num_days = 10000
certainty_levels = [0.1,0.9,0.99,0.999,0.9999,0.99999,0.999999]


# In[16]:


"""
Potentiate the transition matrix in order to calculate the probabilities for any given day in the future
"""

Ptot = P.copy(deep = True)
history = pd.DataFrame(index = range(num_days+1), columns = state_names)

# Day Zero: no dwarf has been to the hall
history.iloc[0,:] = 0
history.iloc[0,0] = 1

# Iterate over the number of days and save the respective probabilities
for i in range(num_days):
    history.iloc[i+1,:] = Ptot.iloc[0,:]
    Ptot = Ptot.dot(P)


# In[17]:


"""
Plot probability distribution 
"""
fig, ax = plt.subplots(figsize  = (25,15))
ax = history.plot(ax=ax, legend = False)
ax.set_xlabel('Days spent in prison')
ax.set_ylabel('Probability for a certain number of remaining dwarves')
plt.grid(True)
plt.savefig('Riddle_det_' + str(num_dwarves) + 'dwarves_' + str(num_days) + 'days.png')


# In[18]:


"""
Plot inverse distribution
"""
fig, ax = plt.subplots(figsize  = (25,15))
ax = history[history.iloc[:,-1]>0].reset_index().plot(ax = ax, x = str(num_dwarves-1)+'x', y = 'index', legend = False)
plt.plot()
ax.set_xlabel('Survival probability')
ax.set_ylabel('Days spent in prison')
plt.grid(True)
plt.savefig('Riddle_det_inverse_' + str(num_dwarves) + 'dwarves_' + str(num_days) + 'days.png')


# In[19]:


for c in certainty_levels:
    history_extract = history[history.iloc[:,-1]>=c]
    if len(history_extract) > 0:
        print('Certainty level ' + str(c)  + ' reached after ' + str(history_extract.index[0])  + ' days.')
    else:
        print('Certainty level ' + str(c)  + ' cant be reached within ' + str(num_days)  + ' days.')


# In[20]:


time_end = time.time()
time_overall = time_end - time_start
print('Overall duration of analysis: ' + str(datetime.timedelta(seconds=time_overall)))

