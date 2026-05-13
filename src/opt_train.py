import optuna
import optuna.visualization as vis
from optuna.samplers import RandomSampler, TPESampler
import src.control_evaluation
import src.train_rl
import env.CONSTS as c
from env.bldc_gym_env import AimFuncParams
import colorama
from colorama import Fore
import argparse
import plotly
import os

def objective_model(trial):
    lr = trial.suggest_float("learning_rate", 1e-5, 1e-2, log=True)
    n_steps = trial.suggest_categorical("n_steps", [256, 512, 1024, 2048])
    batch_size = trial.suggest_categorical("batch_size", [32, 64, 128])

    i_rand_starts = src.train_rl.RandomnessIterationsStarts
    i_rand_starts.SP_init_i_start = 0
    i_rand_starts.SP_change_i_start = 1
    i_rand_starts.PARAMS_i_start = c.ITERATIONS // 3
    i_rand_starts.LOAD_i_start = (2 * c.ITERATIONS) // 3

    trained_model = src.train_rl.train_random(
        is_rand_SP=True, 
        is_rand_PARAMS=True, 
        is_rand_LOAD=True,
        i_rand_starts=i_rand_starts,
        learning_rate=lr,
        n_steps=n_steps,
        batch_size=batch_size,
        save_model=False
    )

    score = src.control_evaluation.fixed_eval(trained_model)
    
    return score

def objective_aim(trial):

    i_rand_starts = src.train_rl.RandomnessIterationsStarts
    i_rand_starts.SP_init_i_start = 0
    i_rand_starts.SP_change_i_start = 1
    i_rand_starts.PARAMS_i_start = c.ITERATIONS // 3
    i_rand_starts.LOAD_i_start = (2 * c.ITERATIONS) // 3


    penalty_factor_error=trial.suggest_float("p_factor_error", 0.1,1000, log=True)
    penalty_factor_current=trial.suggest_float("p_factor_current", 0.1, 1000, log=True)
    penalty_factor_action=trial.suggest_float("p_factor_action", 0.1, 1000, log=True)
    penalty_stall=trial.suggest_float("p_factor_stall", 10, 1000, log=True)
    reward_velocity=trial.suggest_float("r_velocity", 10, 1000, log=True)

    aim_params=AimFuncParams(penalty_factor_error=penalty_factor_error,
                             penalty_factor_current=penalty_factor_current,
                             penalty_factor_action=penalty_factor_action,
                             penalty_stall=penalty_stall,
                             reward_velocity=reward_velocity)

    trained_model = src.train_rl.train_random(
        is_rand_SP=True, 
        is_rand_PARAMS=True, 
        is_rand_LOAD=True,
        i_rand_starts=i_rand_starts,
        save_model=False,
        aim_params=aim_params)

    score = src.control_evaluation.fixed_eval(trained_model)
    
    return score

def run_optimization(sampler_type,policy,type,study_name):
    print(Fore.CYAN + f"Running optimalization: {study_name} ({sampler_type.__class__.__name__})")
    
    os.makedirs("db", exist_ok=True)

    study = optuna.create_study(
            direction="minimize",
            study_name=study_name,
            sampler=sampler_type,
            storage=f"sqlite:///db/optuna_study_{study_name}.db",
            load_if_exists=True)
    

    # SQLite pozwala na przerwanie i wznowienie optymalizacji bez utraty danych
    if type=="aim":
        study.optimize(objective_aim, n_trials=c.OPTUNA_TRIALS) # Możesz zmienić liczbę prób
    else:
        study.optimize(objective_model, n_trials=c.OPTUNA_TRIALS) # Możesz zmienić liczbę prób
    

    print(Fore.GREEN + "="*10)
    print(Fore.GREEN + f"Best parameters: {study.best_params}")
    print(Fore.GREEN + f"Best score: {study.best_value}")
    print(Fore.GREEN + "="*10)

    save_study_plots(study=study,arg_type=type,arg_policy=policy)

def save_study_plots(study,arg_policy,arg_type):
    import os
    dir_name=f"opt_plots/{arg_type}/{arg_policy}"
    os.makedirs(f"{dir_name}", exist_ok=True)
    
    # Zapisujemy do HTML, bo są interaktywne (można najechać myszką na punkt)
    vis.plot_optimization_history(study).write_html(f"{dir_name}/history.html")
    vis.plot_parallel_coordinate(study).write_html(f"{dir_name}/correlations.html")
    vis.plot_param_importances(study).write_html(f"{dir_name}/importance.html")
    vis.plot_slice(study).write_html(f"{dir_name}/slices.html")
    
    print(Fore.GREEN + f"Correlations save in /{dir_name}")

# def make_random_search():
#     run_optimization(RandomSampler(), "random_search_ppo")
    
# def make_bayes_search():
#     # TPESampler to domyślny algorytm Bayesowski w Optuna
#     run_optimization(TPESampler(), "bayes_search_ppo")

def make_search(arg_policy,arg_type):
    policy=None
    name=f"{arg_policy}_search_{arg_type}"
    if arg_policy == "bayes":
        policy=TPESampler()
    else:
        policy=RandomSampler()

    run_optimization(policy,arg_policy,arg_type,name)

def opt_show(arg_policy, arg_type):
    colorama.init(autoreset=True)

    # 1. Połączenie z istniejącą bazą danych
    study_name = f"{arg_policy}_search_{arg_type}"
    storage_url = f"sqlite:///db/optuna_study_{study_name}.db"

    print(f"{study_name}")
    print(f"optuna_study_{study_name}.db")

    try:
        study = optuna.load_study(study_name=study_name, storage=storage_url)
        
        print(Fore.CYAN + f"Wczytano badanie: {study_name}")
        print(Fore.GREEN + f"Najlepszy wynik (ITAE): {study.best_value}")
        print(Fore.GREEN + f"Najlepsze parametry: {study.best_params}")

        # 2. Generowanie wykresów
        dir_name=f"opt_plots/{arg_type}/{arg_policy}"
        os.makedirs(f"{dir_name}", exist_ok=True)
        
        print("Generuję wykresy...")
        vis.plot_optimization_history(study).write_html(f"{dir_name}/history.html")
        vis.plot_parallel_coordinate(study).write_html(f"{dir_name}/correlations.html")
        vis.plot_param_importances(study).write_html(f"{dir_name}/importance.html")
        vis.plot_slice(study).write_html(f"{dir_name}/slices.html")
        
        print(Fore.YELLOW + f"Gotowe! Wykresy znajdziesz w folderze /{dir_name}")

    except Exception as e:
        print(Fore.RED + f"Błąd: {e}")

if __name__ == "__main__":
    colorama.init(autoreset=True)
    parser = argparse.ArgumentParser(description="Optimalization training model parser")

    parser.add_argument("-p","--policy",type=str,default="random",choices=["random","bayes"],help="Name of search policy.")
    parser.add_argument("-t","--type", type=str,default="model",choices=["model","aim"],help="Type of parameters to optimize.")
    parser.add_argument("-r","--show_result",action="store_true", help="Show results and generate plots without training.")
    

    args = parser.parse_args()

    if(args.show_result==True):
        opt_show(arg_policy=args.policy,arg_type=args.type)
    else:
        make_search(arg_policy=args.policy,arg_type=args.type)