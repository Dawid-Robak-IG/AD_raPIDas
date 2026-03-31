import gymnasium as gym
from stable_baselines3 import PPO, SAC,TD3,DDPG
from env.bldc_gym_env import BLDCEnv
import os
from colorama import Fore 
import colorama
from datetime import datetime
import sys

def train(name="", algorithm="PPO"):
    colorama.init(autoreset=True)
    os.makedirs("models",exist_ok=True)
    if name=="":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        run_name  = f"bldc_pid_tuner_{timestamp}"
    else:
        run_name  = f"bldc_pid_tuner_{name}"

    env = BLDCEnv()

    if(algorithm=="PPO"):
        model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=log_dir)
        log_dir = "./ppo_bldc_logs/"
    elif(algorithm=="SAC"):
        model = SAC("MlpPolicy", env, verbose=1, tensorboard_log=log_dir)
        log_dir = "./sac_bldc_logs/"
    elif(algorithm=="TD3"):
        model = TD3("MlpPolicy", env, verbose=1, tensorboard_log=log_dir)
        log_dir = "./td3_bldc_logs/"
    elif(algorithm=="DDPG"):
        model = DDPG("MlpPolicy", env, verbose=1, tensorboard_log=log_dir)
        log_dir = "./ddpg_bldc_logs/"
    else:
        print(Fore.YELLOW + "Didn't get any right name for algorithm, continuing with PPO...")
        model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=log_dir)

    print(Fore.GREEN + "Starting training pf RL Agent...")
    model.learn(
        total_timesteps=50000,
        tb_log_name=run_name
    )

    model.save(f"models/{run_name}")
    print(Fore.GREEN + f"Model saved: models/{run_name}")

if __name__ == "__main__":
    if(len(sys.argv)>2):
        train(sys.argv[1],sys.argv[2])
    elif(len(sys.argv)>1):
        train(sys.argv[1])
    else:
        train()