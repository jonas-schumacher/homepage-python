import numpy as np
import matplotlib.pyplot as plt
import yaml
import time
from datetime import datetime

from agent import Agent
from environment import Obstgarten

if __name__ == '__main__':

    start_time = time.time()

    with open('hps_train.yaml') as file:
        hps = yaml.load(file, Loader=yaml.FullLoader)
    print(hps)

    PLOT_COLORS = ['black', 'tab:red', 'tab:blue', 'tab:green']
    SMOOTHING_WINDOW_LENGTH = 10

    env = Obstgarten(hps)
    agent = Agent(hps, env)

    current_time = datetime.now().strftime('%Y%m%d-%H%M%S')

    """
    TRAIN
    """
    score_outer = np.zeros(hps['agent']['BATCHES'], dtype=float)
    score_inner = np.zeros(hps['agent']['ITERATIONS_PER_BATCH'], dtype=float)
    iter_games = 0
    for batch_index in range(len(score_outer)):
        for iter_index in range(len(score_inner)):
            # Get initial state from the environment
            state, reward, game_end = env.initialize_game()
            is_first = True
            # Continue game until final state is reached
            while not game_end:
                action = agent.choose_fruit(state, reward, is_first)
                is_first = False
                state, reward, game_end = env.continue_game(action)
            # When game is over, inform agent and save last reward
            agent.finish_game(reward)
            score_inner[iter_index] = reward
            iter_games += 1

        score_outer[batch_index] = np.mean(score_inner)

        print("Batch: {} \N{tab} Winning probability: {}%".format(
            batch_index,
            np.round(100*score_outer[batch_index], 1)))

    agent.finish_interaction()
    """
    EVAL
    """
    fig, ax = plt.subplots()
    plt.plot(score_outer, color=PLOT_COLORS[0], alpha=0.3)
    score_smoothed = np.convolve(score_outer,
                                 np.ones(SMOOTHING_WINDOW_LENGTH), 'valid') / SMOOTHING_WINDOW_LENGTH
    score_smoothed = np.concatenate((score_outer[:SMOOTHING_WINDOW_LENGTH - 1], score_smoothed))
    ax.plot(score_smoothed, label="Average reward (= winning probability)", color=PLOT_COLORS[0])

    plt.xlabel("Iterations of {} games".format(
        hps['agent']['ITERATIONS_PER_BATCH']))
    plt.ylabel("Winning probability")
    plt.legend()
    plt.show()
    fig.savefig("obstgarten" + "-" + current_time)

    duration = time.time() - start_time
    print("Overall time: {} minutes".format(np.round(duration / 60.0, decimals=2)))
