import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt 
from stable_baselines3 import PPO 
from env.bldc_gym_env import BLDCEnv
import os 
from colorama import Fore
import colorama
import sys

def test_model(model_name):
    colorama.init(autoreset=True)
    env = BLDCEnv()

    model_path = f"models/bldc_pid_tuner_{model_name}.zip"
    if not os.path.exists(model_path):
        print(Fore.RED + f"Couldn't find {model_path}")
        return
    
    model = PPO.load(model_path)
    obs, _ = env.reset()

    history = {"t": [], "v": [], "target": [], "kp": [], "ki": [], "kd": [], "i": []}

    print(Fore.GREEN + f"Launching model: {model_path}...")
    for step in range(40): # 4 sekundy / 0.1s step = 40 kroków
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        
        history["t"].append(step * 0.1)
        history["v"].append(obs[3])
        history["target"].append(obs[2])
        history["kp"].append(action[0])
        history["ki"].append(action[1])
        history["kd"].append(action[2])
        
        if terminated: break

    plt.figure(figsize=(10, 8))
    plt.subplot(2, 1, 1)
    plt.plot(history["t"], history["v"], label="Velocity RL")
    plt.plot(history["t"], history["target"], 'r--', label="Target")
    plt.ylabel("Velocity [rad/s]")
    plt.legend()
    
    plt.subplot(2, 1, 2)
    plt.plot(history["t"], history["kp"], label="Kp")
    plt.plot(history["t"], history["ki"], label="Ki")
    plt.plot(history["t"], history["kd"], label="Kd")
    plt.ylabel("PID")
    plt.xlabel("Time[s]")
    plt.legend()
    
    plt.show()

if __name__ == "__main__":
    colorama.init(autoreset=True)
    if(len(sys.argv)<2):
        print(Fore.RED + f"No name for model given, returning...")
        exit()
    test_model(sys.argv[1])
    