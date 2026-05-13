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
import env.CONSTS as c
from typing import TypedDict, Optional

class RandomnessIterationsStarts(TypedDict):
    SP_init_i_start: int
    SP_change_i_start: int
    LOAD_i_start: int
    PARAMS_i_start: int

def calc_new_SP(i):
    range_width = (c.MAX_SP - c.MIN_SP)/c.ITERATIONS
    new_min = i*range_width + c.MIN_SP
    new_max = (i+1)*range_width + c.MIN_SP
    return int(random.uniform(new_min, new_max))

def calc_new_load(i, i_max):
    range_width = (c.MAX_LOAD - c.MIN_LOAD)/i_max
    new_min = i*range_width + c.MIN_LOAD
    new_max = (i+1)*range_width + c.MIN_LOAD
    return random.uniform(new_min, new_max)

def calc_new_param(i,i_max,nominal_value, max_val, min_val ,variation_scale=0.05):

    max_deviation = nominal_value * (variation_scale * (i /i_max))
    val = random.uniform(nominal_value - max_deviation, nominal_value + max_deviation)
    return max(min(val, max_val), min_val)

def get_dyn_name(is_rand_SP=False, is_rand_PARAMS=False, is_rand_LOAD=False):
    model_name = "with_dynamic"
    if is_rand_SP:
        model_name += "_SP"
    if is_rand_PARAMS:
        model_name += "_PARAMS"
    if is_rand_LOAD:
        model_name +="_LOAD"
    return model_name

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

def make_env(rank, seed=0, sp=c.NOMINAL_SP, load=c.NOMINAL_LOAD, R=c.R_NOMINAL, L=c.L_NOMINAL, b=c.b_NOMINAL, aim_params=None):
    def _init():
        env = BLDCEnv(R=R,L=L,b=b,aim_params=aim_params)
        env.targeted_speed = sp
        env.load = load
        env.reset(seed=int(seed+rank))
        return env
    set_random_seed(seed)
    return _init

def train(name="", algorithm="PPO", sp=c.NOMINAL_SP, load=c.NOMINAL_LOAD, R=c.R_NOMINAL, L=c.L_NOMINAL, b=c.b_NOMINAL,aim_params=None ,model_path="", num_cpu=c.CPU_AMOUNT):
    colorama.init(autoreset=True)
    os.makedirs("models",exist_ok=True)
    if name=="":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        run_name  = f"bldc_pid_tuner_{timestamp}"
    else:
        run_name  = f"bldc_pid_tuner_{name}"

    env = SubprocVecEnv([make_env(sp=sp,load=load,R=R,L=L,b=b,aim_params=aim_params,rank=i) for i in range(num_cpu)])

    model, log_dir = get_model(algorithm, env, model_path)

    print(Fore.GREEN + "Starting training of RL Agent...")
    model.learn(
        total_timesteps=50000,
        tb_log_name=run_name,
        reset_num_timesteps=False,
        progress_bar = True
    )

    model.save(f"models/{run_name}")
    env.close()
    print(Fore.GREEN + f"Model saved: models/{run_name}")




def train_random(is_rand_SP=False, is_rand_PARAMS=False, is_rand_LOAD=False, 
                 i_rand_starts: Optional[RandomnessIterationsStarts] = None, aim_params=None,
                 learning_rate=3e-4, n_steps=512, batch_size=64,
                 save_model=True):
    colorama.init(autoreset=True)
    os.makedirs("models",exist_ok=True)
    if i_rand_starts is None:
        i_rand_starts = {
            "SP_init_i_start": 0,
            "SP_change_i_start":0,
            "LOAD_i_start": 0,
            "PARAMS_i_start": 0
        }
    model_name = get_dyn_name(is_rand_SP=is_rand_SP, is_rand_PARAMS=is_rand_PARAMS, is_rand_LOAD=is_rand_LOAD)

    env = SubprocVecEnv([make_env(rank=i,aim_params=aim_params) for i in range(c.CPU_AMOUNT)])
    log_dir = f"./ppo_bldc_logs/"
    run_name  = f"bldc_pid_tuner" +  model_name
    model = PPO("MlpPolicy",
                env=env,verbose=1, 
                tensorboard_log=log_dir, 
                device="cpu",
                n_steps = n_steps,
                batch_size=batch_size,
                learning_rate=learning_rate)

    for i in range(c.ITERATIONS):
        if is_rand_SP and i_rand_starts.SP_init_i_start <= i:
            new_sp = calc_new_SP(i)
            env.set_attr("targeted_speed",new_sp)
            print(Fore.GREEN + f"Trainig for SP: {new_sp} | i: {i}")

        if is_rand_SP and i_rand_starts.SP_change_i_start <= i:
            env.set_attr("sp_randomization",1)
            print(Fore.GREEN + f"SP randomization during run: ON | i: {i}")

        if is_rand_PARAMS and i_rand_starts.PARAMS_i_start <= i:
            new_R = calc_new_param(i- i_rand_starts.PARAMS_i_start,c.ITERATIONS- i_rand_starts.PARAMS_i_start,c.R_NOMINAL,c.MAX_R,c.MIN_R)
            new_L = calc_new_param(i- i_rand_starts.PARAMS_i_start,c.ITERATIONS- i_rand_starts.PARAMS_i_start,c.L_NOMINAL,c.MAX_L,c.MIN_L)
            new_b = calc_new_param(i- i_rand_starts.PARAMS_i_start,c.ITERATIONS- i_rand_starts.PARAMS_i_start,c.b_NOMINAL,c.MAX_b,c.MIN_b)
            env.set_attr("R", new_R)
            env.set_attr("L", new_L)
            env.set_attr("b", new_b)
            print(Fore.GREEN + f"Trainig for R: {new_R} | L: {new_L} | b: {new_b} |i: {i}")
        if is_rand_LOAD and i_rand_starts.LOAD_i_start <= i:
            new_load = calc_new_load(i-i_rand_starts.LOAD_i_start,c.ITERATIONS-i_rand_starts.LOAD_i_start)
            env.set_attr("load",new_load)
            print(Fore.GREEN + f"Trainig for LOAD: {new_load} | i: {i}")
        env.reset()

        model.learn(
            total_timesteps=c.TIMESTEPS,
            tb_log_name=run_name,
            reset_num_timesteps=False,
            progress_bar=True,
        )
    if save_model:
        current_model_path = f"models/bldc_pid_tuner_{model_name}.zip"
        model.save(current_model_path)
        print(Fore.GREEN + f"Model saved: models/{run_name}")
        
    env.close()
    return model

if __name__ == "__main__":
    if(len(sys.argv)>2):
        train(sys.argv[1],sys.argv[2])
    elif(len(sys.argv)>1):
        train(sys.argv[1])
    else:
        train()