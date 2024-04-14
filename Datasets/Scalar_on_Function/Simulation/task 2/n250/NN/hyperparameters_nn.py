import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
from Datasets.Scalar_on_Function import Utils
from Datasets.Scalar_on_Function.Simulation.train_functions import train_nn

from ray import train, tune
from ray.tune.schedulers import AsyncHyperBandScheduler


MODEL_NAME = 'NN'
N_SAMPLES = 250
beta, g, snr = 2, 1, 0.5       # chosen and fixed for the whole task 2
folder_name = 'train_' + MODEL_NAME.lower() + f'_regressionsimulation_{N_SAMPLES}'
save_directory = 'C:/Users/Kristijonas/ray_results/' + folder_name
hyperparameters = {'hidden_layers'      : tune.choice([1, 2, 3]),
                   'hidden_nodes'       : tune.choice([16, 32, 64, 128]),
                   'lr'                 : tune.uniform(0.001, 0.1),
                   'data_directory'     : f'C:/Users/Kristijonas/Desktop/ETH/Master thesis/Datasets/Scalar_on_Function/Simulation/data/task 2/B{beta}_G{g}/n{N_SAMPLES}/',
                   'MODEL_NAME'         : MODEL_NAME,
                   'X_dir'              : f'X/X_beta{beta}_g{g}_snr{snr}.csv',
                   'T_dir'              : f'T/T_beta{beta}_g{g}_snr{snr}.csv',
                   'Y_dir'              : f'Y/Y_beta{beta}_g{g}_snr{snr}.csv'}

if __name__ == "__main__":
    sched = AsyncHyperBandScheduler()
    trainable_with_cpu_gpu = tune.with_resources(train_nn, {"cpu": 12, "gpu": 1})
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
    assert not results.errors

result_df = Utils.load_best(save_directory, train_nn)