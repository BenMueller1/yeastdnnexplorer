import sys
import argparse

from pytorch_lightning import Trainer, seed_everything
from yeastdnnexplorer.ml_models.simple_model import SimpleModel
from yeastdnnexplorer.data_loaders.synthetic_data_loader import MyDataModule

def main():
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

def simple_model_synthetic_data_experiment(batch_size, lr, max_epochs, using_random_seed, accelerator):
    data_module = MyDataModule(batch_size=batch_size)
    model = SimpleModel(input_dim=1000, output_dim=1, lr=lr)
    trainer = Trainer(max_epochs=max_epochs, deterministic=using_random_seed, accelerator=accelerator)
    trainer.fit(model, data_module)

    test_results = trainer.test(model, datamodule=data_module)
    print(test_results) # TODO should implement logging in the future to get more detailed results & info

def parse_args_for_synthetic_data_experiment():
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