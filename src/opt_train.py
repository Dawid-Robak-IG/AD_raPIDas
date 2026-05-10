import optuna
import optuna.visualization as vis
from optuna.samplers import RandomSampler, TPESampler
import src.control_evaluation
import src.train_rl
import env.CONSTS as c
import colorama
from colorama import Fore
import argparse
import plotly
import os

def objective(trial):
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

def run_optimization(sampler_type, study_name):
    print(Fore.CYAN + f"Running optimalization: {study_name} ({sampler_type.__class__.__name__})")
    
    # SQLite pozwala na przerwanie i wznowienie optymalizacji bez utraty danych
    study = optuna.create_study(
        direction="minimize",
        study_name=study_name,
        sampler=sampler_type,
        storage=f"sqlite:///optuna_study_{study_name}.db",
        load_if_exists=True
    )
    
    study.optimize(objective, n_trials=c.OPTUNA_TRIALS) # Możesz zmienić liczbę prób

    print(Fore.GREEN + "="*10)
    print(Fore.GREEN + f"Best parameters: {study.best_params}")
    print(Fore.GREEN + f"Best score: {study.best_value}")
    print(Fore.GREEN + "="*10)

    save_study_plots(study=study_name)

def save_study_plots(study):
    import os
    os.makedirs("opt_plots", exist_ok=True)
    
    # Zapisujemy do HTML, bo są interaktywne (można najechać myszką na punkt)
    vis.plot_optimization_history(study).write_html(f"opt_plots/{study}_history.html")
    vis.plot_parallel_coordinate(study).write_html(f"opt_plots/{study}_correlations.html")
    vis.plot_param_importances(study).write_html(f"opt_plots/{study}_importance.html")
    vis.plot_slice(study).write_html(f"opt_plots/{study}_slices.html")
    
    print(Fore.GREEN + "Correlations save in /opt_plots")

def make_random_search():
    run_optimization(RandomSampler(), "random_search_ppo")
    
def make_bayes_search():
    # TPESampler to domyślny algorytm Bayesowski w Optuna
    run_optimization(TPESampler(), "bayes_search_ppo")

def opt_show(arg_study_name):
    colorama.init(autoreset=True)

    # 1. Połączenie z istniejącą bazą danych
    storage_url = "sqlite:///optuna_study.db"
    if arg_study_name == "random":
        study_name = "random_search_ppo" # Upewnij się, że nazwa jest identyczna jak w opt_train.py
    elif arg_study_name == "bayes":
        study_name = "bayes_search_ppo"

    try:
        study = optuna.load_study(study_name=study_name, storage=storage_url)
        
        print(Fore.CYAN + f"Wczytano badanie: {study_name}")
        print(Fore.GREEN + f"Najlepszy wynik (ITAE): {study.best_value}")
        print(Fore.GREEN + f"Najlepsze parametry: {study.best_params}")

        # 2. Generowanie wykresów
        os.makedirs("opt_plots", exist_ok=True)
        
        print("Generuję wykresy...")
        vis.plot_optimization_history(study).write_html("opt_plots/history.html")
        vis.plot_parallel_coordinate(study).write_html("opt_plots/correlations.html")
        vis.plot_param_importances(study).write_html("opt_plots/importance.html")
        vis.plot_slice(study).write_html("opt_plots/slices.html")
        
        print(Fore.YELLOW + "Gotowe! Wykresy znajdziesz w folderze /opt_plots")

    except Exception as e:
        print(Fore.RED + f"Błąd: {e}")

if __name__ == "__main__":
    colorama.init(autoreset=True)
    parser = argparse.ArgumentParser(description="Optimalization training model parser")

    parser.add_argument("--search",type=str,default="random",help="Name for search")
    parser.add_argument("--show_result",action="store_true", help="just show result")

    args = parser.parse_args()

    if(args.show_result==True):
        opt_show(args.search)
    elif(args.search=="random"):
        make_random_search()
    elif(args.search=="bayes"):
        make_bayes_search()