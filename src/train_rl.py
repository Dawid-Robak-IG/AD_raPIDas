import gymnasium as gym
from stable_baselines3 import PPO
from env.bldc_gym_env import BLDCEnv
import os
from colorama import Fore 
import colorama
from datetime import datetime

def train():
    colorama.init(autoreset=True)
    os.makedirs("models",exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    run_name  = f"bldc_pid_tuner_{timestamp}"
    log_dir = "./ppo_bldc_logs/"

    env = BLDCEnv()

    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=log_dir)
    print(Fore.GREEN + "Starting training pf RL Agent...")
    model.learn(
        total_timesteps=50000,
        tb_log_name=run_name
    )

    model.save(f"models/{run_name}")
    print(Fore.GREEN + f"Model saved: models/{run_name}")

if __name__ == "__main__":
    train()