import torch
from Function_on_Function.Simulation.train_functions import train_ffdnn

from ray import train, tune
from ray.tune.schedulers import AsyncHyperBandScheduler
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


MODEL_NAME = 'FFDNN'
beta, g, snr = 2, 2, 0.1
folder_name = 'train_' + MODEL_NAME.lower() + f'_fof_regressionsimulation_beta{beta}_g{g}'
hyperparameters = {'hidden_layers'      : tune.choice([1, 2, 3]),
                   'hidden_nodes'       : tune.choice([8, 16, 32, 64]),
                   'hidden_q'           : tune.choice([10, 20, 50]),
                   'lambda_weight'      : tune.uniform(0.0, 1.0),
                   'lambda_bias'        : tune.uniform(0.0, 1.0),
                   'lr'                 : tune.uniform(0.001, 0.5),
                   'data_directory'     : f'Function_on_Function/Simulation/data/B{beta}_G{g}/',
                   'MODEL_NAME'         : MODEL_NAME,
                   'X_dir'              : f'X/X_beta{beta}_g{g}_snr{snr}.csv',
                   'T_dir'              : f'T/T_beta{beta}_g{g}_snr{snr}.csv',
                   'Y_dir'              : f'Y/Y_beta{beta}_g{g}_snr{snr}.csv'}


if __name__ == "__main__":
    sched = AsyncHyperBandScheduler()
    trainable_with_cpu_gpu = tune.with_resources(train_ffdnn, {"cpu": 12, "gpu": 1})
    tuner = tune.Tuner(
        trainable_with_cpu_gpu,
        tune_config = tune.TuneConfig(
            metric = "mse",
            mode = "min",
            scheduler = sched,
            num_samples = 50
        ),
        run_config = train.RunConfig(
            name = folder_name
        ),
        param_space = hyperparameters,
    )
    results = tuner.fit()
    print("Best config is:", results.get_best_result().config)