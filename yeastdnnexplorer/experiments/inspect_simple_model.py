import sys
import argparse

import pytorch_lightning as pl
from pytorch_lightning import seed_everything
from yeastdnnexplorer.ml_models.simple_model import SimpleModel
from yeastdnnexplorer.data_loaders.synthetic_data_loader import SyntheticDataLoader

def main():
    args = parse_args_for_inspect_model_experiment()

    # use default values if flag not present in command line arguments
    checkpoint_file_path = args.checkpoint_file

    inspect_model_experiment(checkpoint_file_path)

def inspect_model_experiment(checkpoint_file_path):
    
    # load the model from the checkpoint
    model = SimpleModel.load_from_checkpoint(checkpoint_path = checkpoint_file_path)

    print("Model Hyperparameters===========================================")
    print(model.hparams)

    print("Model Parameters================================================")
    for name, param in model.named_parameters():
        print(f"{name}: {param.size()}")
        print(f"\t{param.data}")


def parse_args_for_inspect_model_experiment():
    parser = argparse.ArgumentParser(description='Inspcting Model Parameters')
    parser.add_argument('--checkpoint_file', type=str, action='store', required=True) # this will be the checkpoint file that we want to inspect
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    main()