import collections
import numpy as np

Experience = collections.namedtuple('Experience', field_names=['state', 'action', 'reward', 'next_state', 'done'])


class ExperienceBuffer:
    def __init__(self, capacity):
        self.buffer = collections.deque(maxlen=capacity)
        self.rng = np.random.default_rng()

    def __len__(self):
        return len(self.buffer)

    def append(self, experience):
        self.buffer.append(experience)

    def sample(self, batch_size):
        indices = self.rng.choice(len(self.buffer), batch_size, replace=False)
        state_batch, action_batch, reward_batch, next_state_batch, done_batch = zip(*[self.buffer[idx] for idx in indices])
        return np.array(state_batch), np.array(action_batch), np.array(reward_batch), np.array(next_state_batch), np.array(done_batch),
