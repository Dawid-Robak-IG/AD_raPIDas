import numpy as np
from colorama import Fore
from env.bldc_gym_env import BLDCEnv
import src.test_rl
import env.CONSTS as c

def ise(error,dt): # Integral Squared Error
    return np.sum(error**2) * dt

def iae(abs_error,dt): # Integral Absolute Error
    return np.sum(abs_error) * dt

def itae(abs_error,t,dt): # Integral Time-weighted Absolute Error
    return np.sum(abs_error*t) * dt

def ess(abs_error, last_percent=10): # steady-state error
    last_samples = int(len(abs_error) * last_percent/100)
    ess = np.mean(abs_error[-last_samples:]) if last_samples>0 else abs_error[-1]
    return ess

def get_settling_time_steady_sp(v, sp, t, percent=5):
    band = abs(sp[0]) * (percent / 100)
    outside_band_indices = np.where(np.abs(v - sp[0]) > band)[0]
    if len(outside_band_indices) == 0:
        return 0.0
    last_outside_idx = outside_band_indices[-1]
    if last_outside_idx == len(t) - 1: # Nigdy nie ustalił się
        return np.nan
    return t[last_outside_idx + 1] - t[0]

def mean_settling_time(v,sp,t):
    idx_of_changing_sp = [0]
    
    for i in range(1,len(sp)):
        if sp[i] != sp[i-1]:
            idx_of_changing_sp.append(i)
    idx_of_changing_sp.append(len(sp))

    settling_times = []

    for i in range(len(idx_of_changing_sp) - 1):
        start = idx_of_changing_sp[i]
        end = idx_of_changing_sp[i+1]

        v_seg = v[start:end]
        sp_seg = sp[start:end]
        t_seg = t[start:end]

        ts = get_settling_time_steady_sp(v_seg,sp_seg,t_seg)
        settling_times.append(ts)
        
    return np.mean(settling_times) if settling_times else -1.0

def calculate_evaluations(t, v, sp):
    error = sp - v
    abs_error = np.abs(error)

    dt = t[1] - t[0]
    print(Fore.LIGHTMAGENTA_EX + f"DEBUG: dt for calculating evaluation: {dt}")

    new_ise = ise(abs_error, dt)
    new_iae = iae(abs_error,dt)
    new_itae = itae(abs_error,t,dt)
    new_ess = ess(abs_error,10)

    overshoot_val = np.max(v - sp) # Jeśli v > sp, to będzie > 0
    max_overshoot_pct = (overshoot_val / sp[0]) * 100 if overshoot_val > 0 else 0

    mean_settling_time_for_all = mean_settling_time(v,sp,t)

    return {
        "ISE": round(new_ise,4),
        "IAE": round(new_iae,4),
        "ITAE": round(new_itae,4),
        "ESS": round(new_ess,4),
        "MAX_DIFF": round(max_overshoot_pct,4),
        "MEAN_SETTLING_TIME": round(mean_settling_time_for_all,4)
    }

def print_eval(dict):
    print(Fore.LIGHTRED_EX + "Control evaluation:")
    print(Fore.LIGHTRED_EX + f"ISE: {dict["ISE"]:.3f}")
    print(Fore.LIGHTRED_EX + f"IAE: {dict["IAE"]:.3f}")
    print(Fore.LIGHTRED_EX + f"ITEA: {dict["ITEA"]:.3f}")
    print(Fore.LIGHTRED_EX + f"ESS: {dict["ESS"]:.3f}")
    print(Fore.LIGHTRED_EX + f"MAX_OVERSHOOT: {dict["MAX_DIFF"]:.3f} [%]")
    print(Fore.LIGHTRED_EX + f"MEAN_SETTLING_TIME: {dict["MEAN_SETTLING_TIME"]:.4f} [sec]")


def fixed_eval(trained_model):
    env = src.test_rl.make_env(is_rand_SP=False, is_rand_PARAMS=False, is_rand_LOAD=False)
    obs, _ = env.reset()
    
    # Inicjalizacja PUSTYCH list (zapobiega dt=0)
    history = {"t": [], "v": [], "target": []} 
    sim_steps = c.NOMINAL_SIM_TIME * 10

    # Zdefiniujmy zestaw testowy (np. dwa skoki prędkości dla lepszej oceny)
    test_setpoints = [800, 1500, 500] # Stała sekwencja dla każdego modelu
    steps_per_sp = sim_steps // len(test_setpoints)

    for i, sp in enumerate(test_setpoints):
        env.targeted_speed = sp # Ustawiamy konkretny cel
        env.obs_reset()
        for _ in range(steps_per_sp):
            action, _ = trained_model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            
            # Zbieramy dane
            # Używamy globalnego licznika kroków dla czasu
            current_step = len(history["t"])
            history["t"].append(current_step * c.NOMINAL_TIME_CHANGE)
            history["v"].append(obs[3] * 1000)
            history["target"].append(sp)

            if terminated: break

    # Używamy Twojej dopracowanej funkcji do obliczeń
    # calculate_evaluations zwraca słownik z ISE, IAE, ITAE, ESS, itd.
    results = calculate_evaluations(np.array(history["t"]), 
                                    np.array(history["v"]), 
                                    np.array(history["target"]))
    
    # Zwracamy ITAE do MINIMALIZACJI przez Optunę
    # Jeśli model się nie ustalił (MEAN_SETTLING_TIME == -1), 
    # możemy "ukarać" wynik, dodając dużą karę (Penalty)
    score = results["ITAE"]
    if results["MEAN_SETTLING_TIME"] < 0:
        score += 1000000 # Potężna kara za brak stabilizacji
        
    return score