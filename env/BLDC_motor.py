import control as ct
import numpy as np

class BLDCMotor:
    def __init__(self, noise_w = 0.1, noise_I = 0.001, noise_V = 0.001, noise_Tl = 0.001, dt=0.001):
        # V = L*di + R*i + Ke*w - równanie spadku napięcia II prawo Kirchhoffa
        # T = Kt*i = J*dw + b*w - równanie momentu II prawo Newtona
        self.R = 0.2 # rezystancja uzwojenia [Ohm]
        self.L = 0.0005 # induktancja uzwojenia [Henr]
        self.J = 0.00002 # moment bezwładności [kg*m2]
        self.b = 0.00001 # wsp. moemntu tarcia [N*m*s]
        self.Ke = 0.01 # stała wstecznej siły EM -> V/(rad/s) - stała napiecia wstecznego, ile generuje napiecia gdy sie kreci -> V=Ke*w
        self.Kt = 0.01 # stała momentowa -> N*m/A- jak silnie zamienia elektryczna w mechaniczna
        self.noise_w = noise_w
        self.noise_I = noise_I
        self.noise_V = noise_V
        self.noise_Tl = noise_Tl
        self.dt = dt

        self.calc_new_ss()
        self.reset() 

    def sim_step(self, voltage, load_torque=0.0):
        # Szum wejść
        v_n = np.random.normal(0, self.noise_V)
        l_n = np.random.normal(0, self.noise_Tl)
        
        # Wektor wejść: u = [napięcie, obciążenie]
        u = np.array([voltage + v_n, load_torque + l_n])

        # OBLICZENIA (To jest 100x szybsze niż forced_response!)
        # x(k+1) = Ad * x(k) + Bd * u(k)
        self.x_state = self.Ad @ self.x_state + self.Bd @ u
        
        # y(k) = Cd * x(k) + Dd * u(k)
        y = self.Cd @ self.x_state + self.Dd @ u
        
        self.current_draw = y[0]
        self.current_speed = y[1]
        self.t += self.dt

        # Szum wyjść
        noisy_speed = self.current_speed + np.random.normal(0, self.noise_w)
        noisy_current = self.current_draw + np.random.normal(0, self.noise_I)
        
        return noisy_speed, noisy_current
    #symulacja kroku o czasie dt
    # def sim_step(self, voltage, load_torque = 0.0, dt = 0.01):
    #     t_span = np.array([0, dt])

    #     #dodane zaszumienie sterowania
    #     voltage_noise = np.random.normal(0, self.noise_V) 
    #     noisy_voltage = voltage + voltage_noise

    #     load_noise = np.random.normal(0, self.noise_Tl)
    #     noisy_load = load_torque + load_noise

    #     #wektor wejść
    #     u_input= np.array([[noisy_voltage, noisy_voltage],[noisy_load, noisy_load]])

    #     #symulacja
    #     t_out, y_out, x_out = ct.forced_response(
    #         self.system,
    #         T=t_span,
    #         U=u_input,
    #         X0=self.x_state,
    #         return_x=True
    #     )

    #     #aktualizacja stanu obiektu (pythona, nie dynamicznego :D)
    #     self.x_state=x_out[:,-1]
    #     self.current_speed = y_out[1,-1] # bezpośrednio z wyjścia obiektu (patrz macierz C)
    #     self.current_draw = y_out[0,-1] # bezpośrednio z wyjścia obiektu
    #     self.t += dt

    #     #zaszumianie wyjść
    #     speed_noise = np.random.normal(0, self.noise_w)
    #     current_noise = np.random.normal(0, self.noise_I)

    #     noisy_speed = self.current_speed + speed_noise
    #     noisy_current = self.current_draw + current_noise
        
    #     return noisy_speed, noisy_current
    
    #resetowanie stanu silnika
    def reset(self):
        self.t = 0
        self.current_speed = 0
        self.current_draw = 0
        self.x_state = np.zeros(self.system.nstates)

    # wyznaczanie opisu w przestrzeni stanu
    def calc_new_ss(self):
        # mamy jawnie prąd w wektorze stanu
        # x = [i , w]
        # u = [V, Tl]
        # di/dt = -R/L * i - Ke/L * w + 1/L * V
        # dw/dt =  Kt/J * i - b/J * w - 1/J * Tl
        A = [
            [-self.R/self.L, -self.Ke/self.L],
            [ self.Kt/self.J, -self.b/self.J ]
        ]

        B = [
            [1/self.L, 0],
            [0, -1/self.J]
        ]
        
        C = [
            [1, 0], # Stan 0 (prąd)
            [0, 1]  # Stan 1 (prędkość)
        ]
        
        D = [[0, 0], [0, 0]] # Brak bezpośredniego przejścia V i Lt na wyjście

        self.system = ct.ss(A, B, C, D)
        # Dyskretyzacja układu ciągłego na dyskretny
        sys_discrete = self.system.sample(self.dt, method='zoh') # Zero-Order Hold
        self.Ad = sys_discrete.A
        self.Bd = sys_discrete.B
        self.Cd = sys_discrete.C
        self.Dd = sys_discrete.D
