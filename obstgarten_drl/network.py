import torch
import torch.nn as nn


class DQNNetwork(nn.Module):

    def __init__(self, num_inputs, num_actions, hidden, hps):

        super(DQNNetwork, self).__init__()
        torch.manual_seed(hps['env']['seed'])
        self.hps = hps

        self.fc = nn.Sequential(
            nn.Linear(num_inputs, hidden[0]),
            nn.ReLU(),
            nn.Linear(hidden[0], hidden[1]),
            nn.ReLU(),
            nn.Linear(hidden[1], num_actions)
        )

    def forward(self, x):
        return self.fc(x)

    @torch.no_grad()
    def sample_action(self, obs):
        obs = torch.from_numpy(obs).float()
        obs = obs.unsqueeze(0)
        q_values = self(obs)
        q_values = q_values.squeeze(0)
        action = torch.argmax(q_values).item()

        return action

    @torch.no_grad()
    def get_max_value(self, obs_batch):
        q_values = self(obs_batch)
        q_max, _ = torch.max(q_values, dim=1)

        return q_max
