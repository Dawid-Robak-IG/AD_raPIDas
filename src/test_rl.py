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
import argparse

def make_env(is_rand_SP=False, is_rand_PARAMS=False ,is_rand_LOAD=False):
    if (is_rand_SP):
        targeted_speed = np.random.uniform(c.MIN_SP, c.MAX_SP)
    else:
        targeted_speed = c.BEAUTIFUL_SP
    
    if (is_rand_PARAMS):
        targeted_R = np.random.uniform(c.MIN_R, c.MAX_R)
        targeted_L = np.random.uniform(c.MIN_L, c.MAX_L)
        targeted_b = np.random.uniform(c.MIN_b, c.MAX_b)
    else:
        targeted_R = c.R_NOMINAL
        targeted_L = c.L_NOMINAL
        targeted_b = c.b_NOMINAL

    if (is_rand_LOAD):
        targeted_LOAD = np.random.uniform(c.MIN_LOAD,c.MAX_LOAD) 
    else:
        targeted_LOAD = c.BEAUTIFUL_LOAD

    env = BLDCEnv(R=targeted_R,
                  L=targeted_L,
                  b=targeted_b)
    env.targeted_speed = targeted_speed
    env.load = targeted_LOAD
    print(Fore.GREEN + f"Testing with: SP={targeted_speed}, LOAD={targeted_LOAD}")
    print(Fore.GREEN + f"            : R={targeted_R:.3f}, L={targeted_L:3f}, b={targeted_b:3f}")
    return env
     
def get_model(algorithm,model_path):
    if(algorithm=="PPO"):
        model = PPO.load(model_path)
    elif(algorithm=="SAC"):
        model = SAC.load(model_path)
    elif(algorithm=="TD3"):
        model = TD3.load(model_path)
    elif(algorithm=="DDPG"):
        model = DDPG.load(model_path)
    else:
        print(Fore.YELLOW + "Didn't get any right name for algorithm, continuing with PPO...")
        model = PPO.load(model_path)
    return model

def make_plot(history):
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

def get_new_current_SP(max_step_change_percent, min_step_change_percent ,current_sp):
    choosen_pecent = np.random.uniform(min_step_change_percent,max_step_change_percent)
    direction = np.random.choice([-1,1])
    current_sp *= 1+(direction+choosen_pecent/100)

    if(current_sp>c.MAX_SP):
        current_sp = c.MAX_SP
    elif(current_sp<c.MIN_SP):
        current_sp = c.MIN_SP
    current_sp = round(current_sp,3)
    return current_sp

def test_model(model_name, algorithm="PPO", is_rand_SP=False, is_rand_PARAMS=False ,is_rand_LOAD=False, 
               is_SP_floating=False,steps_change_SP=250, max_change_percent_SP=10, min_change_percent_SP=0 ,is_debug=False):
    model_name = model_name
    colorama.init(autoreset=True)
    env = make_env(is_rand_LOAD=is_rand_LOAD,is_rand_SP=is_rand_SP,is_rand_PARAMS=is_rand_PARAMS)

    model_path = f"models/bldc_pid_tuner_{model_name}.zip"
    if not os.path.exists(model_path):
        print(Fore.RED + f"Couldn't find {model_path}")
        return
    model = get_model(algorithm=algorithm,model_path=model_path)

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
    iteration_change=1
    if(is_debug):
        print(Fore.LIGHTMAGENTA_EX + f"DEBUG: is_SP_floating = {is_SP_floating}")
        print(Fore.LIGHTMAGENTA_EX + f"DEBUG: steps_change_SP = {steps_change_SP}")
    for step in range(1000): # 20 sekundy / 0.1s step = 200 kroków
        if(is_SP_floating and iteration_change*steps_change_SP < step):
            env.targeted_speed = get_new_current_SP(max_step_change_percent=max_change_percent_SP,min_step_change_percent=min_change_percent_SP,
                                                    current_sp=env.targeted_speed)
            env.obs_reset()
            print(Fore.CYAN + f"New targeted speed: {env.targeted_speed}")
            iteration_change += 1
            print(f"step: {step}")

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

    make_plot(history=history)

if __name__ == "__main__":
    colorama.init(autoreset=True)
    parser = argparse.ArgumentParser(description="Testing trained model parser")

    parser.add_argument("--name", type=str, default="num1", help="Name of model")    
    parser.add_argument("--rand_sp", action="store_true", help="Turn on rand SetPoint")
    parser.add_argument("--rand_params", action="store_true", help="Turn on rand Parameters (R, L, b)")
    parser.add_argument("--rand_load", action="store_true", help="Turn on rand Load")
    parser.add_argument("--floating_SP", action="store_true", help="Turn on floating sp while testing time")
    parser.add_argument("--max_float_SP_percent", type=int, default=20, help="How much SP can change in percent to current value")
    parser.add_argument("--min_float_SP_percent", type=int, default=10, help="How much SP can change in percent to current value")
    parser.add_argument("--steps_change_SP", type=int, default=250, help="Determines per how many steps it should change SP value")
    parser.add_argument("--algorithm", type=str, default="PPO", help="Choose algorithm")
    parser.add_argument("--debug", action="store_true", help="Turn on debug logs")

    args = parser.parse_args()

    test_model(model_name=args.name,
               algorithm=args.algorithm, 
               is_rand_SP=args.rand_sp, 
               is_rand_LOAD=args.rand_load, 
               is_rand_PARAMS=args.rand_params,
               is_SP_floating=args.floating_SP,
               steps_change_SP=args.steps_change_SP,
               max_change_percent_SP=args.max_float_SP_percent,
               min_change_percent_SP=args.min_float_SP_percent,
               is_debug = args.debug)

    
    