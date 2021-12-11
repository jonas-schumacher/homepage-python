import numpy as np
import torch

from network import DQNNetwork
from buffer import ExperienceBuffer, Experience


def epsilon_decay_schedule(decay_type, total_steps, init_epsilon, min_epsilon, decay_share):
    decay_steps = int(decay_share * total_steps)

    epsilons = np.full(shape=total_steps, fill_value=min_epsilon)
    if decay_type == "linear":
        epsilons = 1 - np.arange(total_steps) / decay_steps
        epsilons = min_epsilon + (init_epsilon - min_epsilon) * epsilons
        epsilons = np.clip(epsilons, min_epsilon, init_epsilon)
    if decay_type == "exponential":
        decay = 0.01 / np.logspace(-2, 0, decay_steps, endpoint=False) - 0.01
        decay = min_epsilon + (init_epsilon - min_epsilon) * decay
        epsilons[:decay_steps] = decay

    return epsilons


class Agent:

    def __init__(self, hps, env):

        self.hps = hps
        self.env = env
        torch.manual_seed(hps['env']['seed'])

        self.game_count = 0
        self.train_count = 0
        self.decision_count = 0
        self.rng = np.random.default_rng(hps['env']['seed'])
        self.evaluation_mode = False

        self.actor = DQNNetwork(num_inputs=self.env.num_states,
                                num_actions=self.env.num_actions,
                                hidden=self.hps['dqn']['hidden_size'],
                                hps=self.hps)
        self.target = DQNNetwork(num_inputs=self.env.num_states,
                                 num_actions=self.env.num_actions,
                                 hidden=self.hps['dqn']['hidden_size'],
                                 hps=self.hps)

        self.actor_opt = torch.optim.Adam(self.actor.parameters(), lr=self.hps['dqn']['lr'])

        self.buffer = ExperienceBuffer(capacity=self.hps['dqn']['replay_size'], hps=hps)
        self.state = None
        self.action = None

        self.epsilon_schedule = epsilon_decay_schedule(
            decay_type=self.hps['dqn']['eps']['strategy'],
            total_steps=self.hps['agent']['batches'] * self.hps['agent']['games_per_batch'],
            init_epsilon=self.hps['dqn']['eps']['start'],
            min_epsilon=self.hps['dqn']['eps']['final'],
            decay_share=self.hps['dqn']['eps']['share'])

        self.epsilon = self.epsilon_schedule[0]

    def choose_fruit(self, state, reward, is_first):

        self.decision_count += 1

        if self.hps['agent']['one_hot_state']:
            state_input = np.array([], dtype=int)
            for s in state[:-1]:
                fruit = np.zeros(shape=self.hps['env']['num_fruit'] + 1, dtype=int)
                fruit[s] = 1
                state_input = np.concatenate((state_input, fruit))
            raven = np.zeros(shape=self.hps['env']['num_raven'] + 1, dtype=int)
            raven[state[-1]] = 1
            state_input = np.concatenate((state_input, raven))
        else:
            state_input = state
            if self.hps['agent']['additional_input']:
                fullest_tree = np.argmax(state[:-1])
                state_input = np.concatenate((state_input, np.array([fullest_tree])))

        # In evaluation mode, always go for the greedy action
        if self.evaluation_mode:
            action = self.actor.sample_action(state_input)
            return action

        if self.rng.random() < self.epsilon:
            action = self.rng.choice(a=self.env.num_actions, replace=False)
        else:
            action = self.actor.sample_action(state_input)

        if not is_first:
            exp = Experience(state=self.state,
                             action=self.action,
                             reward=reward,
                             next_state=state_input,
                             done=False)
            self.buffer.append(exp)

        self.state = state_input
        self.action = action

        return action

    def finish_game(self, reward):
        # In evaluation mode, skip training
        if self.evaluation_mode:
            return None

        exp = Experience(state=self.state,
                         action=self.action,
                         reward=reward,
                         next_state=np.ones_like(a=self.state),
                         done=True)
        self.buffer.append(exp)
        if len(self.buffer) >= self.hps['dqn']['replay_start_size']:
            # Reduce exploring parameter
            self.epsilon = self.epsilon_schedule[self.game_count]

            # Train network
            if self.game_count % self.hps['dqn']['skip_train'] == 0:
                self.train_network()
                self.train_count += 1

            # Copy weights from trained to target net
            if self.game_count % self.hps['dqn']['skip_copy'] == 0:
                self.target.load_state_dict(self.actor.state_dict())
        self.game_count += 1

    def train_network(self):
        self.actor_opt.zero_grad()

        # Sample a mini-batch from the replay buffer
        obs_batch, action_batch, reward_batch, next_obs_batch, done_batch = \
            self.buffer.sample(self.hps['dqn']['batch_size'])
        obs_batch = torch.tensor(obs_batch, dtype=torch.float32)
        action_batch = torch.tensor(action_batch, dtype=torch.int64)
        reward_batch = torch.tensor(reward_batch, dtype=torch.float32)
        next_obs_batch = torch.tensor(next_obs_batch, dtype=torch.float32)
        done_batch = torch.BoolTensor(done_batch)

        # A: Evaluate training net
        raw_values = self.actor(obs_batch)
        q_values = raw_values.gather(1, action_batch.unsqueeze(1)).squeeze(1)

        # B: Evaluate target net (without gradients) in order to bootstrap training net
        with torch.no_grad():
            target_q_values = self.target.get_max_value(next_obs_batch)
            target_q_values[done_batch] = 0.0
            target_q_values = reward_batch + self.hps['agent']['gamma'] * target_q_values.detach()

        loss = torch.nn.MSELoss()(q_values, target_q_values)

        loss.backward()
        self.actor_opt.step()

    def finish_interaction(self):
        print("Number of training steps: {}".format(self.train_count))
        print("Number of games played: {}".format(self.game_count))
        print("Number of decision: {}".format(self.decision_count))


class RandomAgent(Agent):
    def __init__(self, hps, env):
        super().__init__(hps, env)

    def choose_fruit(self, state, reward, is_first):
        action = self.rng.choice(self.hps['env']['num_tree'])
        return action

    def finish_game(self, reward):
        pass

    def finish_interaction(self):
        pass


class PositiveAgent(RandomAgent):
    def __init__(self, hps, env):
        super().__init__(hps, env)

    def choose_fruit(self, state, reward, is_first):
        action = np.argmax(state[:-1])
        return action


class NegativeAgent(RandomAgent):
    def __init__(self, hps, env):
        super().__init__(hps, env)

    def choose_fruit(self, state, reward, is_first):
        action = np.argmin(state[:-1])
        return action
