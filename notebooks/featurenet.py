import math
import numpy as np
import torch
import torch.nn

from .nnutils import Network
from .phinet import PhiNet
from .invnet import InvNet
from .fwdnet import FwdNet

class FeatureNet(Network):
    def __init__(self, n_actions, input_shape=2, n_latent_dims=4, n_hidden_layers=1, n_units_per_layer=32, lr=0.001, inv_steps_per_fwd=5):
        super().__init__()
        self.n_actions = n_actions
        self.lr = lr
        self.inv_steps_per_fwd = inv_steps_per_fwd

        self.phi = PhiNet(input_shape=input_shape, n_latent_dims=n_latent_dims, n_units_per_layer=n_units_per_layer, n_hidden_layers=n_hidden_layers, lr=lr)

        self.fwd_model = FwdNet(n_actions=n_actions, n_latent_dims=n_latent_dims, n_hidden_layers=n_hidden_layers, n_units_per_layer=n_units_per_layer, lr=lr)

        self.inv_model = InvNet(n_actions=n_actions, n_latent_dims=n_latent_dims, n_units_per_layer=n_units_per_layer, n_hidden_layers=n_hidden_layers, lr=lr)

        self.cross_entropy = torch.nn.CrossEntropyLoss()
        self.mse = torch.nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.parameters(), lr=self.lr)

    def compute_inv_loss(self, a_logits, a):
        return self.cross_entropy(input=a_logits, target=a)

    def compute_fwd_loss(self, z0, z1, z1_hat):
        eps = 1e-6
        error = torch.sqrt(torch.sum(torch.pow(z1_hat - z1, 2), dim=-1))
        dz = torch.sqrt(torch.sum(torch.pow(z1 - z0, 2), dim=-1))
        return torch.mean(error / (dz + eps))
        # return self.mse(z1,z1_hat)

    def compute_diversity_loss(self, z0, z1):
        # Encourage the largest difference to be non-zero
        return 0.1*torch.mean(torch.exp(-100 * torch.max(torch.pow(z0-z1,2),dim=-1)[0]))

    def forward(self, *args, **kwargs):
        raise NotImplementedError

    def predict_a(self, z0, z1, ):
        a_logits = self.inv_model(z0, z1)
        return torch.argmax(a_logits, dim=-1)

    def train_batch(self, x0, x1, a, model='inv'):
        self.train()
        self.optimizer.zero_grad()
        z0 = self.phi(x0)
        z1 = self.phi(x1)
        loss = 0
        if model in ['inv', 'both']:
            a_hat = self.inv_model(z0, z1)
            loss += self.compute_inv_loss(a_logits=a_hat, a=a)
        if model in ['fwd', 'both']:
            z1_hat = self.fwd_model(z0, a)
            loss += 0.05 * self.compute_fwd_loss(z0, z1, z1_hat)
        loss.backward()
        self.optimizer.step()
        return loss
