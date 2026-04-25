import src.train_rl as train_rl
import sys
import colorama
from colorama import Fore 
import env.CONSTS as c

def train_by_sp():
    train_rl.train_random(is_rand_SP=True)

def train_by_model_params():
    train_rl.train_random(is_rand_PARAMS=True)

def train_by_load():
    train_rl.train_random(is_rand_LOAD=True)

if __name__ == "__main__":
    if(len(sys.argv)>1):
        if(sys.argv[1] == "1"): train_by_sp()
        if(sys.argv[1] == "2"): train_by_model_params()
        if(sys.argv[1] == "3"): train_by_load()
    else:
        print("Didn't get any param, leaving...")