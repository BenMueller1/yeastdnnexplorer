import sys

import argparse
from argparse import Namespace

from pytorch_lightning import Trainer, seed_everything
from pytorch_lightning.loggers import TensorBoardLogger, CSVLogger
from pytorch_lightning.callbacks import ModelCheckpoint

from yeastdnnexplorer.ml_models.simple_model import SimpleModel
from yeastdnnexplorer.data_loaders.synthetic_data_loader import SyntheticDataLoader

''' Checkpoint callbacks tell the model when to save a checkpoint of the model during training and what to save in the checkpoint.'''
# Callback to save the best model based on validation loss
best_model_checkpoint = ModelCheckpoint(
    monitor='val_loss',
    mode='min',
    filename='best-model-{epoch:02d}-{val_loss:.2f}',
    save_top_k=1
)

# Callback to save checkpoints every 5 epochs, regardless of performance
periodic_checkpoint = ModelCheckpoint(
    filename='periodic-{epoch:02d}',
    every_n_epochs=2,
    save_top_k=-1  # Setting -1 saves all checkpoints
)

''' We also need to configure the loggers that we're going to use '''
tb_logger = TensorBoardLogger("logs/tensorboard_logs")
csv_logger = CSVLogger("logs/csv_logs")

def main() -> None:
    args = parse_args_for_synthetic_data_experiment()

    # use default values if flag not present in command line arguments
    batch_size = args.batch_size or 32
    lr = args.lr or 0.001
    max_epochs = args.max_epochs or 10
    random_seed = args.random_seed or 42
    gpus = args.gpus or 0

    # set random seed for reproducibility
    seed_everything(random_seed)

    # run the experiment
    simple_model_synthetic_data_experiment(
        batch_size = batch_size,
        lr = lr,
        max_epochs = max_epochs,
        using_random_seed = True, # this argument is here in case we want to add functionality in the future to not use a random seed
        accelerator='gpu' if (gpus > 0) else 'cpu'
    )

def simple_model_synthetic_data_experiment(
        batch_size: int, 
        lr: float, 
        max_epochs: int, 
        using_random_seed: bool, 
        accelerator: str
    ) -> None:

    data_module = SyntheticDataLoader(
        batch_size=batch_size, 
        num_genes=1000, 
        signal = [0.1, 0.15, 0.2, 0.25, 0.3],
        n_sample = [1, 1, 2, 2, 4],
        val_size=0.1, 
        test_size=0.1, 
        random_state=42
    )

    num_tfs = sum(data_module.n_sample) # sum of all n_sample is the number of TFs

    model = SimpleModel(input_dim=num_tfs, output_dim=num_tfs, lr=lr)
    trainer = Trainer(
        max_epochs=max_epochs, 
        deterministic=using_random_seed, 
        accelerator=accelerator,
        callbacks=[best_model_checkpoint, periodic_checkpoint],
        logger=[tb_logger, csv_logger]
    )
    trainer.fit(model, data_module)

    test_results = trainer.test(model, datamodule=data_module)
    print(test_results) # this prints all metrics that were logged during the test phase

def parse_args_for_synthetic_data_experiment() -> Namespace:
    parser = argparse.ArgumentParser(description='Simple Model Synthetic Data Experiment')
    parser.add_argument('--batch_size', action='store') # action=store_true gives a boolean value for if flag is present or not, store gives the value of the flag
    parser.add_argument('--lr', action='store')
    parser.add_argument('--max_epochs', action='store')
    parser.add_argument('--random_seed', action='store')
    parser.add_argument('--gpus', action='store')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    main()