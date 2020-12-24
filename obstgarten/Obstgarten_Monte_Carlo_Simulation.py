"""
Program: Obstgarten Monte Carlo Simulation
Author: Jonas Schumacher [jonas-schumacher on Github]
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import datetime

"""
Define possible states
"""
print('definition: [cherry tree, apple tree, pear tree, plum tree, crow]')
print('start: [10, 10, 10, 10, 9]')
print('victory : [0, 0, 0, 0, x_e], where x_e > 0')
print('defeat: [x_a, x_b, x_c, x_d, 0], where at least one x_i > 0')

"""
Set game parameters
"""
num_fruit = 10
num_raven = 9
num_basket = 2
strategy = 'positive'
# strategy = 'negative'
# strategy = 'random'

"""
Set simulation parameters
"""
num_sim = 10**5
seed = 54321
rng = np.random.RandomState(seed=seed)

trees = ['cherry', 'apple', 'pear', 'plum']

"""
Function A: Throw dice based on next pseudo random number
"""


def throwDice():
    # Generate random integer between 1 and 6
    global rng
    number = rng.randint(1, 7)

    result = 'error'
    if number == 1:
        result = 'cherry'
    elif number == 2:
        result = 'apple'
    elif number == 3:
        result = 'pear'
    elif number == 4:
        result = 'plum'
    elif number == 5:
        result = 'raven'
    elif number == 6:
        result = 'basket'
    else:
        result = 'error'
    return result


"""
Function B: One whole game
"""


def game():
    # Initialize state
    state = {'cherry': num_fruit, 'apple': num_fruit, 'pear': num_fruit, 'plum': num_fruit, 'raven': num_raven}
    game_end = False
    victory = False

    global count_num_dice

    # Solange das Spiel nicht vorbei ist, fÃ¼hre weitere Runde durch
    while not game_end:
        symbol = throwDice()
        count_num_dice += 1

        # Special case: basket
        if symbol == 'basket':

            # Harvest "num_baket" fruits
            for i in range(num_basket):
                # Select default fruit
                selection = 'cherry'

                """
                Case distinction as a funtion of chosen strategy
                """
                # Always select "fullest" tree
                if strategy == 'positive':
                    remaining_fruits = 0
                    for t in trees:
                        if state[t] > remaining_fruits:
                            selection = t
                            remaining_fruits = state[t]

                # Always select "emptiest" tree (provided it's not really empty)
                elif strategy == 'negative':
                    remaining_fruits = num_fruit
                    for t in trees:
                        if state[t] <= remaining_fruits and state[t] > 0:
                            selection = t
                            remaining_fruits = state[t]

                # Select any tree
                elif strategy == 'random':
                    tree_options = []

                    # Only include non-empty trees
                    for t in trees:
                        if state[t] > 0:
                            tree_options.append(t)

                    # Select any of the non-empty tree
                    if len(tree_options) > 0:
                        # Generate random integer between 0 and len(tree_options-1)
                        global rng
                        number = rng.randint(0, len(tree_options))
                        selection = tree_options[number]
                    else:
                        selection = 'cherry'

                # Replace basket by the selected fruit
                symbol = selection

                # Reduce number of fruits of selected tree
                state[symbol] = max(0, state[symbol] - 1)

        # Normal case: harvest one fruit OR feed raven
        else:
            state[symbol] = max(0, state[symbol] - 1)

        # Check if raven has won
        if state['raven'] == 0:
            game_end = True
            victory = False
        # Check if players have won
        elif ((state['cherry'] == 0) + (state['apple'] == 0) + (state['pear'] == 0) + (state['plum'] == 0)) == 4:
            game_end = True
            victory = True
        # If no one has won, the game continues
        else:
            game_end = False
    return victory


if __name__ == "__main__":

    # Measure time
    time_start = time.time()

    """
    Simulation
    """
    num_victories = 0
    history = []
    count_num_dice = 0

    for s in range(1, num_sim + 1):
        if s % 1000 == 0:
            prob = num_victories / s
            history.append(prob)
        if s % 100000 == 0:
            print(s)
            prob = num_victories / s
            print('Current winning probability: ' + str(prob) + ' = ' + '{:.2f}'.format(round(100 * prob, 2)) + '%')
        victory = game()
        if victory:
            num_victories += 1

    prob = num_victories / num_sim
    print('Final winning probability: ' + str(prob) + ' = ' + '{:.2f}'.format(round(100 * prob, 2)) + '%')
    print('Average number of dice thrown per round: ' + str(count_num_dice / num_sim))

    skip = 1

    plt.plot(range(1, int(s / 1000 + 1), 1)[skip:], [100 * i for i in history][skip:])
    plt.xlabel('Number of iterations [$\cdot 10^3$]')
    plt.ylabel('Winning probability [%]')
    plt.savefig('MC_Simulation_' + strategy + '_strategy_' + str(num_sim) + '_runs.png')
    plt.show()

    time_end = time.time()
    time_overall = time_end - time_start
    print('Overall duration of simulation: ' + str(datetime.timedelta(seconds=time_overall)))