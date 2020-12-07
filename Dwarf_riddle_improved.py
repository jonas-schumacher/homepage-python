#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""
Program: Dwarve riddle - probabilistic approach
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
num_days = 2000
certainty_levels = [0.9,0.99,0.999,0.9999,0.99999,0.999999]


"""
Set all possible states (as list) and fill transition matrix:
""" 

P = pd.DataFrame(index = range(num_dwarves+1), columns = range(num_dwarves+1))
P.iloc[:,:] = 0

# Fill matrix linewise
for i in range(num_dwarves):
    P.iloc[i,i] = i/num_dwarves
    P.iloc[i,i+1] = 1-i/num_dwarves
P.iloc[num_dwarves,num_dwarves] = 1
# Optionally print P
# print(P)


# In[3]:


"""
Potentiate the transition matrix in order to calculate the probabilities for any given day in the future
"""

Ptot = P.copy(deep = True)
history = pd.DataFrame(index = range(num_days+1), columns = range(num_dwarves+1))

# Day Zero: no dwarf has been to the hall
history.iloc[0,:] = 0
history.iloc[0,0] = 1

# Iterate over the number of days and save the respective probabilities
for i in range(num_days):
    history.iloc[i+1,:] = Ptot.iloc[0,:]
    Ptot = Ptot.dot(P)


# In[4]:


"""
Plot probability distribution 
"""
fig, ax = plt.subplots(figsize  = (25,15))
ax = history.plot(ax=ax, legend = False)
ax.set_xlabel('Days spent in prison')
ax.set_ylabel('Probability for a certain number of remaining dwarves')
plt.grid(True)
plt.savefig('Riddle_' + str(num_dwarves) + 'dwarves_' + str(num_days) + 'days.png')


# In[5]:


for c in certainty_levels:
    history_extract = history[history.iloc[:,-1]>=c]
    if len(history_extract) > 0:
        print('Certainty level ' + str(c)  + ' reached after ' + str(history_extract.index[0])  + ' days.')
    else:
        print('Certainty level ' + str(c)  + ' cant be reached within ' + str(num_days)  + ' days.')


# In[6]:


"""
Plot inverse distribution
"""
fig, ax = plt.subplots(figsize  = (25,15))
ax = history[history.iloc[:,-1]>0.9].reset_index().plot(ax = ax, x = 100, y = 'index', legend = False)
plt.plot()
ax.set_xlabel('Survival probability')
ax.set_ylabel('Days spent in prison')
plt.grid(True)
plt.savefig('Riddle_inverse_' + str(num_dwarves) + 'dwarves_' + str(num_days) + 'days.png')


# In[7]:


time_end = time.time()
time_overall = time_end - time_start
print('Overall duration of analysis: ' + str(datetime.timedelta(seconds=time_overall)))

