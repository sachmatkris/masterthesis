import torch
from Datasets.Scalar_on_Function import Utils
from Datasets.Scalar_on_Function.Real.CanadianWeather.train_functions import train_adafnn

from ray import train, tune
from ray.tune.schedulers import AsyncHyperBandScheduler
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


MODEL_NAME = 'AdaFNN'
folder_name = 'train_' + MODEL_NAME.lower() + '_canadianweather'
save_directory = 'C:/Users/Kristijonas/ray_results/' + folder_name
hyperparameters = {'n_bases1'            : tune.choice([3, 4, 5, 6, 7]),
                   'bases_hidden_nodes1' : tune.choice([8, 16, 32, 64]),
                   'bases_hidden_layers1': tune.choice([1, 2, 3]),
                   'n_bases2'            : tune.choice([3, 4, 5, 6, 7]),
                   'bases_hidden_nodes2' : tune.choice([8, 16, 32, 64]),
                   'bases_hidden_layers2': tune.choice([1, 2, 3]),
                   'sub_hidden_nodes'    : tune.choice([16, 32, 64]),
                   'sub_hidden_layers'   : tune.choice([1, 2, 3]),
                   'lambda1'             : tune.uniform(0.0, 1.0),
                   'lambda2'             : tune.uniform(0.0, 1.0),
                   'lr'                  : tune.uniform(0.001, 0.05),
                   'data_directory'      : 'Scalar_on_Function/Real/CanadianWeather/',
                   'MODEL_NAME'          : MODEL_NAME}


if __name__ == "__main__":
    sched = AsyncHyperBandScheduler()
    trainable_with_cpu_gpu = tune.with_resources(train_adafnn, {"cpu": 12, "gpu": 1})
    tuner = tune.Tuner(
        trainable_with_cpu_gpu,
        tune_config = tune.TuneConfig(
            metric = "accuracy",
            mode = "max",
            scheduler = sched,
            num_samples = 100
        ),
        run_config = train.RunConfig(
            name = folder_name
        ),
        param_space = hyperparameters,
    )
    results = tuner.fit()
    print("Best config is:", results.get_best_result().config)

result_df = Utils.load_best(save_directory, train_adafnn)