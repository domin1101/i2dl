from random import shuffle
import numpy as np

import torch
from torch.autograd import Variable


class SolverKeyPoint(object):
    default_adam_args = {"lr": 1e-4,
                         "betas": (0.9, 0.999),
                         "eps": 1e-8,
                         "weight_decay": 0.0}

    def __init__(self, optim=torch.optim.Adam, optim_args={},
                 loss_func=torch.nn.CrossEntropyLoss()):
        optim_args_merged = self.default_adam_args.copy()
        optim_args_merged.update(optim_args)
        self.optim_args = optim_args_merged
        self.optimF = optim
        self.loss_func = loss_func

        self._reset_histories()

    def _reset_histories(self):
        """
        Resets train and val histories for the accuracy and the loss.
        """
        self.train_loss_history = []
        self.train_acc_history = []
        self.val_acc_history = []
        self.val_loss_history = []

    def set_model(self, model):
        self.optim = self.optimF(model.parameters(), **self.optim_args)

    def validate(self, model, val_loader):
        model.eval()
        loss_val = 0
        counter = 0
        for batch in val_loader:
            images = batch['image']
            key_pts = batch['keypoints']
            key_pts = key_pts.view(key_pts.size(0), -1)
            key_pts = key_pts.type(torch.FloatTensor)
            images = images.type(torch.FloatTensor)

            output = model(images)
            loss_val += self.loss_func(output, key_pts).item()
            counter += 1

        return loss_val / counter, 1.0 / (2 * (loss_val/len(val_loader)))

    def step(self, model, train_iterator):
        batch = next(train_iterator)
        model.train()

        self.optim.zero_grad()

        images = batch['image']
        key_pts = batch['keypoints']
        key_pts = key_pts.view(key_pts.size(0), -1)
        key_pts = key_pts.type(torch.FloatTensor)
        images = images.type(torch.FloatTensor)

        output = model(images)

        loss = self.loss_func(output, key_pts)
        loss.backward()

        self.optim.step()

        return loss.item(), 1.0 / (2 * (loss.item()))