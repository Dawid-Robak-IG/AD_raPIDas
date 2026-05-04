import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt 
from stable_baselines3 import PPO, SAC, TD3,DDPG
from env.bldc_gym_env import BLDCEnv
import src.control_evaluation
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
        targeted_speed = c.NOMINAL_SP
    
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
        targeted_LOAD = c.NOMINAL_LOAD

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
    # Tworzymy 4 wiersze dla pełnej przejrzystości
    fig, axes = plt.subplots(4, 1, figsize=(10, 12), sharex=True)
    
    # --- WYKRES 1: Prędkość i Cel ---
    ax1 = axes[0]
    ax1.plot(history["t"], history["v"], label="Velocity", color='tab:blue')
    ax1.plot(history["t"], history["target"], 'r--', label="Target")
    ax1.set_ylabel("Velocity [rad/s]")
    ax1.legend(loc='upper left')
    ax1.set_title("System Performance Analysis")

    # --- WYKRES 2: Napięcie i Prąd (Dwie osie Y) ---
    ax_v = axes[1]
    color_volt = 'tab:green'
    ax_v.plot(history["t"], history["volt"], label="Voltage", color=color_volt)
    ax_v.set_ylabel("Voltage [V]", color=color_volt)
    ax_v.tick_params(axis='y', labelcolor=color_volt)
    
    ax_i = ax_v.twinx()
    color_curr = 'tab:orange'
    ax_i.plot(history["t"], history["i"], label="Current", color=color_curr, alpha=0.7)
    ax_i.set_ylabel("Current [A]", color=color_curr)
    ax_i.tick_params(axis='y', labelcolor=color_curr)
    
    # Połączona legenda dla Wykresu 2
    lines_v, labels_v = ax_v.get_legend_handles_labels()
    lines_i, labels_i = ax_i.get_legend_handles_labels()
    ax_v.legend(lines_v + lines_i, labels_v + labels_i, loc='upper left')

    # --- WYKRES 3: Nastawy PID (Skalowanie logarytmiczne jeśli trzeba) ---
    ax3 = axes[2]
    ax3.plot(history["t"], history["kp"], label="kp", color='tab:red')
    ax3.plot(history["t"], history["Ti"], label="Ti", color='tab:purple')
    ax3.plot(history["t"], history["Td"], label="Td", color='tab:brown')
    ax3.set_ylabel("PID Gains")
    ax3.legend(loc='upper left')

    # --- WYKRES 4: Akcje Agenta (% zmian) ---
    ax4 = axes[3]
    ax4.plot(history["t"], history["kp_act"], label="Δkp")
    ax4.plot(history["t"], history["Ti_act"], label="ΔTi")
    ax4.plot(history["t"], history["Td_act"], label="ΔTd")
    ax4.set_ylabel("Action [%]")
    ax4.set_xlabel("Time [s]")
    ax4.legend(loc='upper left')
    ax4.axhline(0, color='black', lw=1, ls='--') # linia zero dla akcji

    plt.tight_layout()
    plt.show()

def get_sp_change_plan(sim_steps, n_sp_changes):
    sp_change_plan = []

    buf_steps=0.1*sim_steps # pierwsze 0,1 i ostatnie 0,1 czasu bez skoków
    chunk_size=(sim_steps-buf_steps*2)/n_sp_changes

    for i in range(n_sp_changes):
        sp_change_plan.append(np.random.uniform(i*chunk_size+buf_steps,(i+1)*chunk_size+buf_steps))
    
    sp_change_plan.append(sim_steps+100)

    return sp_change_plan




def test_model(model_name, algorithm="PPO", is_rand_SP=False, is_rand_PARAMS=False ,is_rand_LOAD=False, 
               is_SP_floating=False,n_sp_changes=1, sim_time=30 ,is_debug=False):
    
    model_name = model_name
    colorama.init(autoreset=True)
    sim_steps=sim_time*10

    env = make_env(is_rand_LOAD=is_rand_LOAD,is_rand_SP=is_rand_SP,is_rand_PARAMS=is_rand_PARAMS)

    model_path = f"models/bldc_pid_tuner_{model_name}.zip"

    if not os.path.exists(model_path):
        print(Fore.RED + f"Couldn't find {model_path}")
        return
    
    model = get_model(algorithm=algorithm,model_path=model_path)

    obs, _ = env.reset()

    history = {
        "t": [0], "v": [obs[3]*1000],"volt": [env.PID.prev_output],'i':[obs[4]*100], "target": [obs[2]*1000],
        "kp": [env.PID.kp], "Ti": [env.PID.Ti], "Td": [env.PID.Td],
        "kp_act": [0], "Ti_act": [0], "Td_act": [0]
    }   

    print(Fore.GREEN + f"Launching model: {model_path}...")

    if(is_debug):
        print(Fore.LIGHTMAGENTA_EX + f"DEBUG: is_SP_floating = {is_SP_floating}")
        print(Fore.LIGHTMAGENTA_EX + f"DEBUG: n_sp_changes = {n_sp_changes}")

    sp_change_plan = get_sp_change_plan(sim_steps,n_sp_changes)
    sp_change_counter=0

    for step in range(sim_steps): # 20 sekundy / 0.1s step = 200 kroków

        if(is_SP_floating and sp_change_plan[sp_change_counter] <= step):
            sp_change_counter +=1

            env.targeted_speed = np.random.uniform(c.MIN_SP, c.MAX_SP)

            env.obs_reset()

            print(Fore.CYAN + f"New targeted speed: {env.targeted_speed}")
            print(f"step: {step}")

        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        
        history["t"].append(step * 0.1)
        history["v"].append(obs[3]*1000)
        history['volt'].append(env.PID.prev_output)
        history['i'].append(obs[4]*100)
        history["target"].append(obs[2]*1000)
        history["kp"].append(env.PID.kp)
        history["Ti"].append(env.PID.Ti)
        history["Td"].append(env.PID.Td)
        history["kp_act"].append(action[0])
        history["Ti_act"].append(action[1])
        history["Td_act"].append(action[2])
        
        if terminated: break

    src.control_evaluation.print_eval(src.control_evaluation.calculate_evaluations(np.array(history["t"]),
                                                       np.array(history["v"]),
                                                       np.array(history["target"])))
    make_plot(history=history)


if __name__ == "__main__":
    colorama.init(autoreset=True)
    parser = argparse.ArgumentParser(description="Testing trained model parser")

    parser.add_argument("--name", type=str, default="num1", help="Name of model")    
    parser.add_argument("--rand_sp", action="store_true", help="Turn on rand SetPoint")
    parser.add_argument("--rand_params", action="store_true", help="Turn on rand Parameters (R, L, b)")
    parser.add_argument("--rand_load", action="store_true", help="Turn on rand Load")
    parser.add_argument("--floating_SP", action="store_true", help="Turn on floating sp while testing time")
    parser.add_argument("--sp_changes", type=int, default=4, help="Number of SP random changes")
    parser.add_argument("-r","--random_full", action="store_true", help="Turn on full randomization")
    parser.add_argument("--algorithm", type=str, default="PPO", help="Choose algorithm")
    parser.add_argument("--debug", action="store_true", help="Turn on debug logs")
    parser.add_argument("-t","--time", type=int, default=30, help="Duration of simulation")

    args = parser.parse_args()

    test_model(model_name=args.name,
               algorithm=args.algorithm, 
               is_rand_SP=args.rand_sp or args.random_full, 
               is_rand_LOAD=args.rand_load or args.random_full, 
               is_rand_PARAMS=args.rand_params or args.random_full,
               is_SP_floating=args.floating_SP or args.random_full,
               n_sp_changes=args.sp_changes,
               is_debug = args.debug)

    
    