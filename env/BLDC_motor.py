import control as ct
import numpy as np

class BLDCMotor:
    def __init__(self, noise_v = 0.1, noise_current=0.001, noise_voltage=0.001):
        # V = L*di + R*i + Ke*w - równanie spadku napięcia II prawo Kirchhoffa
        # T = Kt*i = J*dw + b*w - równanie momentu II prawo Newtona
        self.R = 1.0 # rezystancja uzwojenia [Ohm]
        self.L = 0.02 # induktancja uzwojenia [Henr]
        self.J = 0.01 # moment bezwładności [kg*m2]
        self.b = 0.01 # wsp. moemntu tarcia [N*m*s]
        self.Ke = 0.1 # stała wstecznej siły EM -> V/(rad/s) - stała napiecia wstecznego, ile generuje napiecia gdy sie kreci -> V=Ke*w
        self.Kt = 0.1 # stała momentowa -> N*m/A- jak silnie zamienia elektryczna w mechaniczna
        self.noise_speed = noise_v
        self.noise_current = noise_current
        self.noise_voltage = noise_voltage

        self.calc_new_ss()
        self.reset() 

    #symulacja kroku o czasie dt
    def sim_step(self, voltage, dt=0.01):
        t_span = np.array([0, dt])

        #dodane zaszumienie sterowania
        voltage_noise = np.random.normal(0, self.noise_voltage) 
        noisy_voltage= voltage + voltage_noise

        #symulacja
        t_out, y_out, x_out = ct.forced_response(
            self.system,
            T=t_span,
            U=noisy_voltage,
            X0=self.x_state,
            return_x=True
        )

        #aktualizacja stanu obiektu (pythona, nie dynamicznego :D)
        self.x_state=x_out[:,-1]
        self.current_speed = y_out[1,-1] # bezpośrednio z wyjścia obiektu (patrz macierz C)
        self.current_draw = y_out[0,-1] # bezpośrednio z wyjścia obiektu
        self.t += dt

        #zaszumianie wyjść
        speed_noise = np.random.normal(0, self.noise_speed)
        current_noise = np.random.normal(0, self.noise_current)

        noisy_speed = self.current_speed + speed_noise
        noisy_current = self.current_draw + current_noise
        
        return noisy_speed, noisy_current
    
    #resetowanie stanu silnika
    def reset(self):
        self.t = 0
        self.current_speed = 0
        self.current_draw = 0
        self.x_state = np.zeros(self.system.nstates)

    # wyznaczanie opisu w przestrzeni stanu
    def calc_new_ss(self):
        # alternatywna wersja wyznaczenia macierzy równania stanu
        # mamy jawnie prąd w wektorze stanu
        # x = [i , w]
        # di/dt = -R/L * i - Ke/L * w + 1/L * V
        # dw/dt =  Kt/J * i - b/J  * w
        A = [
            [-self.R/self.L, -self.Ke/self.L],
            [ self.Kt/self.J, -self.b/self.L ]
        ]

        B = [
            [1/self.L],
            [0]
        ]
        
        C = [
            [1, 0], # Stan 0 (prąd)
            [0, 1]  # Stan 1 (prędkość)
        ]
        
        D = [[0], [0]] # Brak bezpośredniego przejścia V na wyjście

        self.system = ct.ss(A, B, C, D)
