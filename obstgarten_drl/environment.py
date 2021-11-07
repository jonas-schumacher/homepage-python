import numpy as np


class Obstgarten:

    def __init__(self, hps):

        self.rng = np.random.default_rng()
        self.hps = hps
        if self.hps['agent']['ONE_HOT']:
            self.num_states_one_hot = hps['env']['NUM_TREE'] * (hps['env']['NUM_FRUIT'] + 1) + (
                        hps['env']['NUM_RAVEN'] + 1)
        else:
            self.num_states = hps['env']['NUM_TREE'] + 1
        self.num_actions = hps['env']['NUM_TREE']
        self.state = None
        self.remaining_baskets_to_choose = 0

    def throw_dice(self):
        number = self.rng.integers(1, 7)

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

    def check_for_game_end(self):
        remaining_fruits = self.state['cherry'] + self.state['apple'] + self.state['pear'] + self.state['plum']
        if remaining_fruits == 0:
            game_end = True
            reward = 1
        elif self.state['raven'] == 0:
            game_end = True
            reward = 0
        else:
            game_end = False
            reward = 0
        return game_end, reward

    def initialize_game(self):
        self.state = {'cherry': self.hps['env']['NUM_FRUIT'],
                      'apple': self.hps['env']['NUM_FRUIT'],
                      'pear': self.hps['env']['NUM_FRUIT'],
                      'plum': self.hps['env']['NUM_FRUIT'],
                      'raven': self.hps['env']['NUM_RAVEN']}

        reward = 0
        game_end = False
        symbol = self.throw_dice()

        # Perform all actions in which the agent has no choice
        while not game_end and symbol != "basket":
            self.state[symbol] = max(0, self.state[symbol] - 1)
            game_end, reward = self.check_for_game_end()
            symbol = self.throw_dice()

        if symbol == "basket":
            self.remaining_baskets_to_choose = self.hps['env']['NUM_BASKET']

        return np.fromiter(self.state.values(), dtype=int), reward, game_end

    def continue_game(self, action):
        # Perform action chosen by agent
        symbol = self.hps['env']['TREES'][action]
        self.state[symbol] = max(0, self.state[symbol] - 1)
        self.remaining_baskets_to_choose -= 1

        game_end, reward = self.check_for_game_end()

        # If the agent has not chosen all baskets, ask for another one
        if self.remaining_baskets_to_choose > 0:
            return np.fromiter(self.state.values(), dtype=int), reward, game_end

        # If all baskets have been chosen, continue with regular play
        reward = 0
        game_end = False
        symbol = self.throw_dice()

        while not game_end and symbol != "basket":
            self.state[symbol] = max(0, self.state[symbol] - 1)
            game_end, reward = self.check_for_game_end()
            symbol = self.throw_dice()

        if symbol == "basket":
            self.remaining_baskets_to_choose = self.hps['env']['NUM_BASKET']

        return np.fromiter(self.state.values(), dtype=int), reward, game_end
