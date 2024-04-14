import torch
from Datasets.Scalar_on_Function import Utils
from Datasets.Scalar_on_Function.Simulation.train_functions import train_cnn

from ray import train, tune
from ray.tune.schedulers import AsyncHyperBandScheduler
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


MODEL_NAME = 'CNN'
task = 1
beta, g, snr = 2, 3, 0.5
folder_name = 'train_' + MODEL_NAME.lower() + f'_regressionsimulation_beta{beta}_g{g}_snr{snr}_task{task}'
save_directory = 'C:/Users/Kristijonas/ray_results/' + folder_name
hyperparameters = {'conv_hidden_layers'     : tune.choice([1, 2, 3]),
                   'conv_hidden_channels'   : tune.choice([4, 8, 16]),
                   'fc_hidden_layers'       : tune.choice([1, 2, 3]),
                   'fc_hidden_nodes'        : tune.choice([16, 32, 64]),
                   'kernel_convolution'     : tune.choice([4, 8]),
                   'kernel_pool'            : tune.choice([2, 4]),
                   'convolution_stride'     : tune.choice([1, 2]),
                   'pool_stride'            : tune.choice([1, 2]),
                   'lr'                     : tune.uniform(0.001, 0.1),
                   'data_directory'         : f'C:/Users/Kristijonas/Desktop/ETH/Master thesis/Datasets/Scalar_on_Function/Simulation/data/task {task}/B{beta}_G{g}/snr{snr}/',
                   'MODEL_NAME'             : MODEL_NAME,
                   'Y_dir'                  : f'Y/Y_beta{beta}_g{g}_snr{snr}.csv'
                   }



if __name__ == "__main__":
    sched = AsyncHyperBandScheduler()
    trainable_with_cpu_gpu = tune.with_resources(train_cnn, {"cpu": 12, "gpu": 1})
    tuner = tune.Tuner(
        trainable_with_cpu_gpu,
        tune_config = tune.TuneConfig(
            metric = "mse",
            mode = "min",
            scheduler = sched,
            num_samples = 50,
        ),
        run_config = train.RunConfig(
            name = folder_name
        ),
        param_space = hyperparameters,
    )
    results = tuner.fit()
    print("Best config is:", results.get_best_result().config)

result_df = Utils.load_best(save_directory, train_cnn)