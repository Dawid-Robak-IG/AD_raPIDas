import numpy as np
from colorama import Fore
import colorama

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

def get_settling_time_steady_sp(v,sp,t, percent_for_correct_val=5):
    if(abs(sp[0])<1e-6): return -1

    band = abs(sp[0]) * (percent_for_correct_val/100)

    for i in range(len(t)):
        if abs(v[i] - sp[0]) <= band:
            return t[i] - t[0]
    return np.nan

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

    new_ise = ise(error, dt)
    new_iae = iae(abs_error,dt)
    new_itae = itae(abs_error,t,dt)
    new_ess = ess(abs_error,10)

    max_diff = np.max(error)

    mean_settling_time_for_all = mean_settling_time(v,sp,t)

    return {
        "ISE": round(new_ise,4),
        "IAE": round(new_iae,4),
        "ITEA": round(new_itae,4),
        "ESS": round(new_ess,4),
        "MAX_DIFF": round(max_diff,4),
        "MEAN_SETTLING_TIME": round(mean_settling_time_for_all,4)
    }

def print_eval(dict):
    print(Fore.LIGHTRED_EX + "Control evaluation:")
    print(Fore.LIGHTRED_EX + f"ISE: {dict["ISE"]:.3f}")
    print(Fore.LIGHTRED_EX + f"IAE: {dict["IAE"]:.3f}")
    print(Fore.LIGHTRED_EX + f"ITEA: {dict["ITEA"]:.3f}")
    print(Fore.LIGHTRED_EX + f"ESS: {dict["ESS"]:.3f}")
    print(Fore.LIGHTRED_EX + f"MAX_OVERSHOOT: {dict["MAX_DIFF"]:.3f}")
    print(Fore.LIGHTRED_EX + f"MEAN_SETTLING_TIME: {dict["MEAN_SETTLING_TIME"]:.4f} [sec]")


