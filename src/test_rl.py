import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt 
from stable_baselines3 import PPO, SAC, TD3,DDPG
from env.bldc_gym_env import BLDCEnv
import os 
from colorama import Fore
import colorama
import sys
import env.CONSTS as c

def test_model(argv, rand):
    model_name = argv[1]
    colorama.init(autoreset=True)


    if (rand):

        env = BLDCEnv(R=np.random.uniform(c.MIN_R, c.MAX_R),
                    L=np.random.uniform(c.MIN_L, c.MAX_L), 
                    b=np.random.uniform(c.MIN_b, c.MAX_b))
        env.targeted_speed = np.random.uniform(c.MIN_SP, c.MAX_SP)
    
    else:
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

    history = {"t": [0], 
               "v": [env.motor.current_draw], 
               "target": [env.targeted_speed], 
               "kp": [env.PID.kp], 
               "Ti": [env.PID.Ti], 
               "Td": [env.PID.Td], 
               "kp_act": [0], 
               "Ti_act": [0], 
               "Td_act": [0]}    

    print(Fore.GREEN + f"Launching model: {model_path}...")
    for step in range(1000): # 20 sekundy / 0.1s step = 200 kroków
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        
        history["t"].append(step * 0.1)
        history["v"].append(obs[3]*1000)
        history["target"].append(obs[2]*1000)
        history["kp"].append(env.PID.kp)
        history["Ti"].append(env.PID.Ti)
        history["Td"].append(env.PID.Td)
        history["kp_act"].append(action[0])
        history["Ti_act"].append(action[1])
        history["Td_act"].append(action[2])
        
        if terminated: break

    plt.figure(figsize=(10, 8))
    plt.subplot(3, 1, 1)
    plt.plot(history["t"], history["v"], label="Velocity RL")
    plt.plot(history["t"], history["target"], 'r--', label="Target")
    plt.ylabel("Velocity [rad/s]")
    plt.legend()
    
    plt.subplot(3, 1, 2)
    plt.plot(history["t"], history["kp"], label="kp")
    plt.plot(history["t"], history["Ti"], label="Ti")
    plt.plot(history["t"], history["Td"], label="Td")
    plt.ylabel("PID")
    plt.xlabel("Time[s]")
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(history["t"], history["kp_act"], label="kp_action")
    plt.plot(history["t"], history["Ti_act"], label="Ti_action")
    plt.plot(history["t"], history["Td_act"], label="Td_action")
    plt.ylabel("% changes")
    plt.xlabel("Time[s]")
    plt.legend()
    
    plt.show()

if __name__ == "__main__":
    colorama.init(autoreset=True)
    if(len(sys.argv)<2):
        print(Fore.RED + f"No name for model given, returning...")
        exit()
    if(len(sys.argv)==3):
        test_model(sys.argv, 1)
    else: 
        test_model(sys.argv, 0)
    