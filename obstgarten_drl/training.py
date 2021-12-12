import numpy as np
import matplotlib.pyplot as plt
import torch
import yaml
import time
from datetime import datetime

from agent import Agent, PositiveAgent, NegativeAgent, RandomAgent
from environment import Obstgarten

if __name__ == '__main__':

    start_time = time.time()

    with open('hps_train.yaml') as file:
        hps = yaml.load(file, Loader=yaml.FullLoader)
    print(hps)

    PLOT_COLORS = ['black', 'tab:red', 'tab:blue', 'tab:green']

    env = Obstgarten(hps)
    if hps['agent']['type'] == "positive":
        agent = PositiveAgent(hps, env)
    elif hps['agent']['type'] == "negative":
        agent = NegativeAgent(hps, env)
    elif hps['agent']['type'] == "random":
        agent = RandomAgent(hps, env)
    else:
        agent = Agent(hps, env)
        if hps["agent"]["read_checkpoint"]:
            checkpoint = torch.load("checkpoint.pt")
            agent.actor.load_state_dict(checkpoint["net"])
            agent.target.load_state_dict(checkpoint["net"])
            agent.actor_opt.load_state_dict(checkpoint["opt"])
    current_time = datetime.now().strftime('%Y%m%d-%H%M%S')
    """
    TRAINING
    """
    if hps['agent']['evaluation_mode']:
        agent.evaluation_mode = True
    score_outer = np.zeros(hps['agent']['batches'], dtype=float)
    score_inner = np.zeros(hps['agent']['games_per_batch'], dtype=float)
    iter_games = 0
    for batch_index in range(len(score_outer)):
        if batch_index == len(score_outer)-1:
            agent.evaluation_mode = True
            print("Switch to evaluation mode")
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
    if hps["agent"]["write_checkpoint"]:
        checkpoint = {"net": agent.actor.state_dict(),
                      "opt": agent.actor_opt.state_dict()}
        torch.save(checkpoint, "checkpoint.pt")

    """
    PLOT TRAINING PROGRESS
    """
    fig, ax = plt.subplots()
    plt.plot(score_outer, color=PLOT_COLORS[0], label="Average reward (= winning probability)")
    plt.xlabel(f"Iterations of {hps['agent']['games_per_batch']} games")
    plt.ylabel("Winning probability")
    plt.legend()
    plt.show()
    fig.savefig(f"obstgarten-{current_time}")

    duration = time.time() - start_time
    print(f"Overall time: {np.round(duration / 60.0, decimals=2)} minutes")
