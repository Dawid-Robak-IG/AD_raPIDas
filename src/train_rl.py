import gymnasium as gym
from stable_baselines3 import PPO, SAC,TD3,DDPG
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.vec_env import SubprocVecEnv
from env.bldc_gym_env import BLDCEnv
import os
from colorama import Fore 
import colorama
from datetime import datetime
import sys
import random


MIN_SP = 1.0
MAX_SP = 1000
ITERATIONS = 20
BEAUTIFUL_SP = 800.0

MIN_LOAD = 0.0
MAX_LOAD = 1.0
BEAUTIFUL_LOAD = 0.1


def calc_new_SP(i=0):
    range_width = (MAX_SP - MIN_SP)/ITERATIONS
    new_min = i*range_width + MIN_SP
    new_max = (i+1)*range_width + MIN_SP
    return int(random.uniform(new_min, new_max))

def calc_new_load(i=0):
    range_width = (MAX_LOAD - MIN_LOAD)/ITERATIONS
    new_min = i*range_width + MIN_LOAD
    new_max = (i+1)*range_width + MIN_LOAD
    return random.uniform(new_min, new_max)

def calc_new_param():
    print("DOOPA")


def get_model(algorithm, env, model_path=None):
    algorithms = {
        "PPO": PPO,
        "SAC": SAC,
        "TD3": TD3,
        "DDPG": DDPG
    }
    alg_name = algorithm.upper()
    if algorithm not in algorithms:
        print(Fore.YELLOW + "Didn't get any right name for algorithm, continuing with PPO...")
        alg_name = "PPO"
    
    log_dir = f"./{alg_name.lower()}_bldc_logs/"
    algo_class = algorithms[alg_name]

    if model_path and os.path.exists(model_path):
        print(Fore.CYAN + f"Loading existing model: {model_path}")
        model = algo_class.load(model_path,env=env)
    else:
        print(Fore.GREEN + f"Creating new model: {model_path}")
        model = algo_class("MlpPolicy", env=env, verbose=1, tensorboard_log=log_dir, device="cpu")
    return model,log_dir

def make_env(rank, seed=0, sp=1.0):
    def _init():
        env = BLDCEnv()
        env.targeted_speed = sp
        env.reset(seed=int(seed+rank))
        return env
    set_random_seed(seed)
    return _init



def train(name="", algorithm="PPO", sp=BEAUTIFUL_SP, load=BEAUTIFUL_LOAD ,model_path="", num_cpu=10):
    colorama.init(autoreset=True)
    os.makedirs("models",exist_ok=True)
    if name=="":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        run_name  = f"bldc_pid_tuner_{timestamp}"
    else:
        run_name  = f"bldc_pid_tuner_{name}"

    env = SubprocVecEnv([make_env(sp=sp,rank=i) for i in range(num_cpu)])

    model, log_dir = get_model(algorithm, env, model_path)

    print(Fore.GREEN + "Starting training of RL Agent...")
    model.learn(
        total_timesteps=35000,
        tb_log_name=run_name,
        reset_num_timesteps=False,
        progress_bar = True
    )

    model.save(f"models/{run_name}")
    env.close()
    print(Fore.GREEN + f"Model saved: models/{run_name}")

if __name__ == "__main__":
    if(len(sys.argv)>2):
        train(sys.argv[1],sys.argv[2])
    elif(len(sys.argv)>1):
        train(sys.argv[1])
    else:
        train()