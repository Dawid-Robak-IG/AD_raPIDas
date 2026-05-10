MIN_SP = 300.0
MAX_SP = 2000
NOMINAL_SP = 1000.0

MIN_LOAD = 0.01
MAX_LOAD = 0.08
NOMINAL_LOAD = 0.02

R_NOMINAL = 0.2
L_NOMINAL = 0.0005
b_NOMINAL = 0.00001

MIN_R = 0.18
MAX_R = 0.22

MIN_b = 0.000009
MAX_b = 0.000011

MIN_L = 0.00044
MAX_L = 0.00055

#CPU_AMOUNT = 10
CPU_AMOUNT = 12


MIN_KP = 0.00001 # !!!, żeby % zmiana zawsze coś dawała
MIN_TI = 0.00001   # tutaj jest na odwrót, więc to jest max waga całki
MIN_TD = 0.00001

MAX_KP = 10.0
MAX_TI = 1000    # tutaj jest na odwrót, więc to jest min waga całki
MAX_TD = 10

# akcje w %
MIN_ACT = -5
MAX_ACT = 5


TIMESTEPS = 30000 # liczba kroków agenta na jedną iterację treningu
ITERATIONS = 10 # liczba iteracji treningu agenta
MAX_TOTAL_TIME = 30 # czas w sekundach w pojedynczym runie w trenowaniu (t[s])

MIN_SP_CHANGE_TIME = 50 #minimalny odstęp między losowymi skokami w trenowaniu w krokach agenta(t[s]*10)
MAX_SP_CHANGE_TIME = MAX_TOTAL_TIME*10/2 #maksymalny odstęp między losowymi skokami w trenowaniu w krokach agenta(t[s]*10)

NOMINAL_SIM_TIME = 30
NOMINAL_TIME_CHANGE = 0.1

OPTUNA_TRIALS = 10