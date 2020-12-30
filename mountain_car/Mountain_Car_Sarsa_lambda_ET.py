import numpy as np
import matplotlib.pyplot as plt
import time
from tiles3 import tiles, IHT

limit_x_pos = (-1.2, .5)
limit_x_vel = (-.07, .07)

"""
Create code tilings for state approximation:
"""
maxSize = 2048
iht = IHT(maxSize)
numTilings = 8


def mytiles(x, y):
    scale_factor_x = 10.0 / (limit_x_pos[1] - limit_x_pos[0])
    scale_factor_y = 10.0 / (limit_x_vel[1] - limit_x_vel[0])
    return tiles(iht, numTilings, list((x * scale_factor_x, y * scale_factor_y)))


def plot_current_solution(weights, state_history, num_counter):
    resolution = 50
    x = np.outer(np.linspace(limit_x_pos[0], limit_x_pos[1], resolution), np.ones(resolution))
    y = np.outer(np.linspace(limit_x_vel[0], limit_x_vel[1], resolution), np.ones(resolution)).T
    z = np.zeros_like(x)
    for i in range(resolution):
        for j in range(resolution):
            xy_tiles = mytiles(x[i, j], y[i, j])
            z[i, j] = weights[xy_tiles, :].sum(axis=0).max()
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(x, y, z, cmap='viridis', edgecolor='none', alpha=.7)
    ax.set_title('Value function and sample trajectory')
    plt.xlabel('Position')
    plt.ylabel('Speed')

    x_points = [i[0] for i in state_history]
    y_points = [i[1] for i in state_history]
    z_points = []
    for i in range(len(state_history)):
        xy_tiles = mytiles(x_points[i], y_points[i])
        z_points.append(weights[xy_tiles, :].sum(axis=0).max() + 1)
    ax.scatter(x_points, y_points, z_points, marker='o', s=10, c='black', alpha=1.0)

    fig.savefig('Mountain_value_' + str(num_counter) + '.png')
    plt.tight_layout()
    plt.show()


def plot_current_stats(state_history, action_history, num_counter):
    fig = plt.figure(figsize=(8, 6))

    color = 'tab:blue'
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.set_title('State (Position x Speed) of mountain car during current episode')
    ax1.set_xlabel('Time step')
    ax1.set_ylabel('Position', color=color)
    ax1.grid(True)
    ax1.plot([i[0] for i in state_history], color=color)

    color = 'tab:red'
    ax2 = ax1.twinx()
    ax2.set_ylabel('Speed', color=color)
    ax2.plot([i[1] for i in state_history], color=color)
    fig.savefig('Mountain_state_' + str(num_counter) + '.png')
    plt.show()

    fig = plt.figure()
    plt.scatter(x=np.arange(len(action_history)), y=action_history, s=5.0, c='black', marker='.')
    plt.title('Action taken during current episode')
    plt.xlabel('Time step')
    plt.ylabel('Action')
    fig.savefig('Mountain_action_' + str(num_counter) + '.png')
    plt.show()


class Environment:

    def __init__(self):

        self.reward_per_timestep = -1
        self.reward_on_success = 0
        self.actions = [-1, 0, 1]

    """"
    Central method: 
    1) Convert (state-action) pair to a new state and reward 
    2) Check if a terminal state is reached which ends the episode
    """

    def calculate_next_state_and_reward(self, current_state, current_action):
        episode_ended = False
        reward = self.reward_per_timestep

        current_pos = current_state[0]
        current_vel = current_state[1]
        next_pos = current_pos + current_vel
        next_vel = current_vel + .001 * current_action - .0025 * np.cos(3 * current_pos)

        # Keep velocity bounded
        if next_vel < limit_x_vel[0]:
            next_vel = limit_x_vel[0]
        elif next_vel > limit_x_vel[1]:
            next_vel = limit_x_vel[1]

        # Keep position bounded
        # Left bound reached: set back to bound and vel = 0
        if next_pos < limit_x_pos[0]:
            next_pos = limit_x_pos[0]
            next_vel = 0
        # Right bound reached: end of episode!
        elif next_pos > limit_x_pos[1]:
            reward = self.reward_on_success
            episode_ended = True

        next_state = (next_pos, next_vel)
        return episode_ended, reward, next_state

    def get_admissible_actions(self):
        return self.actions

    @property
    def get_starting_position(self):
        pos = np.random.uniform(low=-.6, high=-.4)
        vel = 0
        return pos, vel


def train():
    # Set Training parameters
    gamma = 1.0  # discount
    epsilon = 0.05  # exploration rate: not really needed
    alpha = 0.1 / numTilings  # step size
    trace_decay_param = .9  # parameter lambda in eligibility traces
    env = Environment()

    # Get admissible actions from Environment
    actions = env.get_admissible_actions()

    # Initialize weight and trace vector
    weights = np.zeros((maxSize, len(actions)))
    traces = np.zeros((maxSize, len(actions)))

    counter_history = []

    """
    Learning Loop
    """
    num_max = 200
    for num_counter in range(num_max):

        # State: Get random starting position from environment
        current_state = env.get_starting_position
        current_state_indices = mytiles(current_state[0], current_state[1])

        # Action: chose action epsilon-greedily
        if np.random.rand() < epsilon:
            current_action_index = np.random.randint(len(actions))
        else:
            current_action_index = weights[current_state_indices, :].sum(axis=0).argmax()

        # Reset trace vector to zero:
        traces[:, :] = 0.0

        # print("Initial state = %s" % str(current_state))
        # print("Initial action = %s" % actions[current_action_index])
        state_history = []
        action_history = []
        episode_ended = False

        """
        Generate episode
        >> Episode should end in a "winning state"
        >> Time out after 2000 unsuccessful time steps
        """
        counter = 0
        while (not episode_ended) and (counter < 2000):
            counter += 1
            state_history.append(current_state)
            action_history.append(actions[current_action_index])

            # Take action A and observe reward R and next state S'
            episode_ended, reward, next_state = env.calculate_next_state_and_reward(current_state,
                                                                                    actions[current_action_index])

            # Step 1: Calculate MC error
            delta = reward - weights[current_state_indices, current_action_index].sum()
            # Step 2: Update traces:
            traces[current_state_indices, current_action_index] += 1

            # If episode ended, one can use the MC error:
            if episode_ended:
                # update weights using SGD = stochastic gradient descent
                # here the trace vector approximates the gradient
                weights += alpha * delta * traces

            # If episode is still running, one has to use the TD error:
            else:
                next_state_indices = mytiles(next_state[0], next_state[1])

                # Action: chose action epsilon-greedily
                if np.random.rand() < epsilon:
                    next_action_index = np.random.randint(len(actions))
                else:
                    next_action_index = weights[next_state_indices, :].sum(axis=0).argmax()

                # Transform MC to TD error by adding bootstrap value of next state
                delta += gamma * weights[next_state_indices, next_action_index].sum()

                # Update weights using TD error
                weights += alpha * delta * traces

                # Reduce traces by decay factor:
                traces = gamma * trace_decay_param * traces

                # Prepare next iteration
                current_state = next_state
                current_state_indices = next_state_indices
                current_action_index = next_action_index

        # After ech episode, save the time steps needed for completion
        counter_history.append(counter)
        if num_counter in [10, 50, num_max - 1]:
            plot_current_solution(weights, state_history, num_counter)
            plot_current_stats(state_history, action_history, num_counter)

    print("Mean episode length:" + str(np.mean(counter_history)))

    fig = plt.figure()
    skip_first = 5
    plt.plot(np.arange(skip_first, len(counter_history)), counter_history[skip_first:])
    plt.title('Change in performance during training')
    plt.xlabel('Simulation run')
    plt.ylabel('Episode length')
    plt.grid(True)
    fig.savefig('Mountain_performance_' + str(num_max) + '.png')
    plt.show()


if __name__ == '__main__':
    start = time.time()
    train()
    end = time.time()

    print("Overall time needed: %d" % (end - start))
