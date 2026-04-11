import src.train_rl as train_rl
import sys
import colorama
from colorama import Fore 
import env.CONSTS as c

def train_by_sp():
    colorama.init(autoreset=True)
    model_name = "with_dynamic_SP"
    current_model_path = ""

    for i in range(c.ITERATIONS):
        SP = train_rl.calc_new_SP(i)
        print(Fore.GREEN + f"Trainig for SP: {SP} | i: {i}")
        train_rl.train(name=model_name, sp=SP, model_path=current_model_path)
        current_model_path = f"models/bldc_pid_tuner_{model_name}.zip"

def train_by_model_params():
    colorama.init(autoreset=True)
    model_name = "with_dynamic_PARAMS"
    current_model_path = ""

    for i in range(c.ITERATIONS):
        new_R = train_rl.calc_new_param(i,c.R_NOMINAL,c.MAX_R,c.MIN_R)
        new_L = train_rl.calc_new_param(i,c.L_NOMINAL,c.MAX_L,c.MIN_L)
        new_b = train_rl.calc_new_param(i,c.b_NOMINAL,c.MAX_b,c.MIN_b)
        print(Fore.GREEN + f"Trainig for R: {new_R} | L: {new_L} | b: {new_b} |i: {i}")
        train_rl.train(name=model_name, R=new_R,L=new_L, b=new_b ,model_path=current_model_path)
        current_model_path = f"models/bldc_pid_tuner_{model_name}.zip"

def train_by_load():
    colorama.init(autoreset=True)
    model_name = "with_dynamic_LOAD"
    current_model_path = ""

    for i in range(c.ITERATIONS):
        LOAD = train_rl.calc_new_load(i)
        print(Fore.GREEN + f"Trainig for LOAD: {LOAD} | i: {i}")
        train_rl.train(name=model_name, load=LOAD ,model_path=current_model_path)
        current_model_path = f"models/bldc_pid_tuner_{model_name}.zip"

if __name__ == "__main__":
    if(len(sys.argv)>1):
        if(sys.argv[1] == "1"): train_by_sp()
        if(sys.argv[1] == "2"): train_by_model_params()
        if(sys.argv[1] == "3"): train_by_load()
    else:
        print("Didn't get any param, leaving...")