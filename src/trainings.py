import src.train_rl as train_rl
import sys
import colorama
from colorama import Fore 

def train_by_sp():
    colorama.init(autoreset=True)
    model_name = "with_dynamic_SP"
    current_model_path = ""

    for i in range(train_rl.ITERATIONS):
        SP = train_rl.calc_new_SP(i)
        print(Fore.GREEN + f"Trainig for SP: {SP} | i: {i}")
        train_rl.train(name=model_name, sp=SP, model_path=current_model_path)
        current_model_path = f"models/bldc_pid_tuner_{model_name}.zip"

def train_by_model_params():
    a = 0

def train_by_load():
    a = 0

if __name__ == "__main__":
    if(len(sys.argv)>1):
        if(sys.argv[1] == "1"): train_by_sp()
        if(sys.argv[1] == "2"): train_by_model_params()
        if(sys.argv[1] == "3"): train_by_load()
    print("Didn't get any param, leaving...")