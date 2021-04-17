import pandas as pd
import matplotlib.pyplot as plt
import time
import datetime

# Measure time 
time_start = time.time()

"""
Set game parameters
NUM_DWARVES = number of dwarves who need to have been to the room already
"""
NUM_DWARVES = 100
NUM_DAYS = 1000
CERTAINTY_LEVELS = [0.9, 0.99, 0.999, 0.9999, 0.99999, 0.999999]

"""
Set all possible states (as list) and fill transition matrix:
"""
P = pd.DataFrame(index=range(NUM_DWARVES + 1), columns=range(NUM_DWARVES + 1))
P.iloc[:, :] = 0

# Fill matrix linewise
for i in range(NUM_DWARVES):
    P.iloc[i, i] = i / NUM_DWARVES
    P.iloc[i, i + 1] = 1 - i / NUM_DWARVES
P.iloc[NUM_DWARVES, NUM_DWARVES] = 1

"""
Potentiate the transition matrix in order to calculate the probabilities for any given day in the future
"""
Ptot = P.copy(deep=True)
history = pd.DataFrame(index=range(NUM_DAYS + 1), columns=range(NUM_DWARVES + 1))

# Day Zero: no dwarf has been to the hall
history.iloc[0, :] = 0
history.iloc[0, 0] = 1

# Iterate over the number of days and save the respective probabilities
for i in range(NUM_DAYS):
    history.iloc[i + 1, :] = Ptot.iloc[0, :]
    Ptot = Ptot.dot(P)

"""
Plot probability distribution 
"""
print('Plot probability distribution')
fig, ax = plt.subplots(figsize=(25, 15))
ax = history.plot(ax=ax, legend=False)
ax.set_xlabel('Days spent in prison')
ax.set_ylabel('Probability for a certain number of remaining dwarves')
plt.grid(True)
plt.savefig('riddle_prob_' + str(NUM_DWARVES) + 'dwarves_' + str(NUM_DAYS) + 'days.png')
plt.show()

"""
Plot inverse distribution
"""
print('Plot inverse probability distribution')
fig, ax = plt.subplots(figsize=(25, 15))
ax = history.reset_index().plot(ax=ax, x=NUM_DWARVES, y='index', legend=False)

plt.plot()
ax.set_xlabel('Survival probability')
ax.set_ylabel('Days spent in prison')
plt.grid(True)
plt.savefig('riddle_prob_' + str(NUM_DWARVES) + 'dwarves_' + str(NUM_DAYS) + 'days_inverse.png')
plt.show()

print('Check certainty levels')
for c in CERTAINTY_LEVELS:
    history_extract = history[history.iloc[:, -1] >= c]
    if len(history_extract) > 0:
        print('Certainty level ' + str(c) + ' reached after ' + str(history_extract.index[0]) + ' days.')
    else:
        print('Certainty level ' + str(c) + ' cant be reached within ' + str(NUM_DAYS) + ' days.')

time_end = time.time()
time_overall = time_end - time_start
print('Overall duration of analysis: ' + str(datetime.timedelta(seconds=time_overall)))
