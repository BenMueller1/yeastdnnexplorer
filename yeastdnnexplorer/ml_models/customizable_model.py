from typing import Any

import pytorch_lightning as pl
import torch
import torch.nn as nn
from torch.optim import Optimizer


class CustomizableModel(pl.LightningModule):
    """ docstring here """

    def __init__(
        self, 
        input_dim: int, 
        output_dim: int, 
        lr: float = 0.001,
        hidden_layer_num: int = 1,
        hidden_layer_sizes: list = [128],
        activation: str = "ReLU", # can be "ReLU", "Sigmoid", "Tanh", "LeakyRelU"
        optimizer: str = "Adam", # can be "Adam", "SGD", "RMSprop"
        L2_regularization_term: float = 0.0,
        dropout_rate: float = 0.0,
    ) -> None:
        """
        Constructor of CustomizableModel.
        """
        if not isinstance(input_dim, int):
            raise TypeError("input_dim must be an integer")
        if not isinstance(output_dim, int):
            raise TypeError("output_dim must be an integer")
        if not isinstance(lr, float) or lr <= 0:
            raise TypeError("lr must be a positive float")
        if input_dim < 1 or output_dim < 1:
            raise ValueError("input_dim and output_dim must be positive integers")

        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.lr = lr
        self.hidden_layer_num = hidden_layer_num
        self.hidden_layer_sizes = hidden_layer_sizes
        self.optimizer = optimizer
        self.L2_regularization_term = L2_regularization_term
        self.save_hyperparameters()

        match activation:
            case "ReLU":
                self.activation = nn.ReLU()
            case "Sigmoid":
                self.activation = nn.Sigmoid()
            case "Tanh":
                self.activation = nn.Tanh()
            case "LeakyRelU":
                self.activation = nn.LeakyReLU()
            case _:
                raise ValueError("activation must be one of 'ReLU', 'Sigmoid', 'Tanh', 'LeakyRelU'")
        
        self.input_layer = nn.Linear(input_dim, hidden_layer_sizes[0])
        self.hidden_layers = nn.ModuleList([])
        for i in range(hidden_layer_num - 1):
            self.hidden_layers.append(nn.Linear(hidden_layer_sizes[i], hidden_layer_sizes[i+1]))
        self.output_layer = nn.Linear(hidden_layer_sizes[-1], output_dim)

        self.dropout = nn.Dropout(p=dropout_rate)


    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the model (i.e. how predictions are made for a given input)

        :param x: The input data to the model (minus the target y values)
        :type x: torch.Tensor
        :return: The predicted y values for the input x, this is a tensor of shape
            (batch_size, output_dim)
        :rtype: torch.Tensor

        """
        x = self.dropout(self.activation(self.input_layer(x)))
        for hidden_layer in self.hidden_layers:
            x = self.dropout(self.activation(hidden_layer(x)))
        x = self.output_layer(x)
        return x

    def training_step(self, batch: Any, batch_idx: int) -> torch.Tensor:
        """
        Training step for the model, this is called for each batch of data during
        training.

        :param batch: The batch of data to train on
        :type batch: Any
        :param batch_idx: The index of the batch
        :type batch_idx: int
        :return: The loss for the training batch
        :rtype: torch.Tensor

        """
        x, y = batch
        y_pred = self(x)
        loss = nn.functional.mse_loss(y_pred, y)
        self.log("train_loss", loss)
        return loss

    def validation_step(self, batch: Any, batch_idx: int) -> torch.Tensor:
        """
        Validation step for the model, this is called for each batch of data during
        validation.

        :param batch: The batch of data to validate on
        :type batch: Any
        :param batch_idx: The index of the batch
        :type batch_idx: int
        :return: The loss for the validation batch
        :rtype: torch.Tensor

        """
        x, y = batch
        y_pred = self(x)
        loss = nn.functional.mse_loss(y_pred, y)
        self.log("val_loss", loss)
        return loss

    def test_step(self, batch: Any, batch_idx: int) -> torch.Tensor:
        """
        Test step for the model, this is called for each batch of data during testing
        Testing is only performed after training and validation when we have chosen a
        final model We want to test our final model on unseen data (which is why we use
        validation sets to "test" during training)

        :param batch: The batch of data to test on (this will have size (batch_size,
            input_dim)
        :type batch: Any
        :param batch_idx: The index of the batch
        :type batch_idx: int
        :return: The loss for the test batch
        :rtype: torch.Tensor

        """
        x, y = batch
        y_pred = self(x)
        loss = nn.functional.mse_loss(y_pred, y)
        self.log("test_loss", loss)
        return loss

    def configure_optimizers(self) -> Optimizer:
        """
        Configure the optimizer for the model.

        :return: The optimizer for the model
        :rtype: Optimizer

        """
        match self.optimizer:
            case "Adam":
                return torch.optim.Adam(self.parameters(), lr=self.lr, weight_decay=self.L2_regularization_term)
            case "SGD":
                return torch.optim.SGD(self.parameters(), lr=self.lr, weight_decay=self.L2_regularization_term)
            case "RMSprop":
                return torch.optim.RMSprop(self.parameters(), lr=self.lr, weight_decay=self.L2_regularization_term)
            case _:
                raise ValueError("optimizer must be one of 'Adam', 'SGD', 'RMSprop'")
