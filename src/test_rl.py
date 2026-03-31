import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt 
from stable_baselines3 import PPO, SAC, TD3,DDPG
from env.bldc_gym_env import BLDCEnv
import os 
from colorama import Fore
import colorama
import sys

def test_model(argv):
    model_name = argv[1]
    colorama.init(autoreset=True)
    env = BLDCEnv()

    model_path = f"models/bldc_pid_tuner_{model_name}.zip"
    if not os.path.exists(model_path):
        print(Fore.RED + f"Couldn't find {model_path}")
        return
    
    if(len(argv)>2):
        if(argv[2]=="PPO"):
            model = PPO.load(model_path)
        elif(argv[2]=="SAC"):
            model = SAC.load(model_path)
        elif(argv[2]=="TD3"):
            model = TD3.load(model_path)
        elif(argv[2]=="DDPG"):
            model = DDPG.load(model_path)
        else:
            print(Fore.YELLOW + "Didn't get any right name for algorithm, continuing with PPO...")
            model = PPO.load(model_path)
    else:
        model = PPO.load(model_path)
    obs, _ = env.reset()

    history = {"t": [], "v": [], "target": [], "kp": [], "Ti": [], "Td": [], "i": []}

    print(Fore.GREEN + f"Launching model: {model_path}...")
    for step in range(1000): # 20 sekundy / 0.1s step = 200 kroków
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        
        history["t"].append(step * 0.1)
        history["v"].append(obs[3]*1000)
        history["target"].append(obs[2]*1000)
        history["kp"].append(action[0])
        history["Ti"].append(action[1])
        history["Td"].append(action[2])
        
        if terminated: break

    plt.figure(figsize=(10, 8))
    plt.subplot(2, 1, 1)
    plt.plot(history["t"], history["v"], label="Velocity RL")
    plt.plot(history["t"], history["target"], 'r--', label="Target")
    plt.ylabel("Velocity [rad/s]")
    plt.legend()
    
    plt.subplot(2, 1, 2)
    plt.plot(history["t"], history["kp"], label="kp")
    plt.plot(history["t"], history["Ti"], label="Ti")
    plt.plot(history["t"], history["Td"], label="Td")
    plt.ylabel("PID")
    plt.xlabel("Time[s]")
    plt.legend()
    
    plt.show()

if __name__ == "__main__":
    colorama.init(autoreset=True)
    if(len(sys.argv)<2):
        print(Fore.RED + f"No name for model given, returning...")
        exit()
    test_model(sys.argv)
    