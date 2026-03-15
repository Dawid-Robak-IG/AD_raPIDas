import control as ct
import numpy as np

class BLDCMotor:
    def __init__(self, noise_v = 0.1, noise_current=0.001):
        # V = di + R*i + Ke*w
        # Kt i = J*dw + b*w
        self.R = 1.0
        self.L = 0.02
        self.J = 0.01 # ineria -> kg*m2
        self.b = 0.01 # friction -> N*m*s
        self.Ke = 0.1 # Back-EMF constant -> V/(rad/s) - stała napiecia wstecznego, ile generuje napiecia gdy sie kreci -> V=Ke*w
        self.Kt = 0.1 # torque constant -> N*m/A- stała momentowa, jak silnie zamienia elektryczna w mechaniczna
        self.noise_speed = noise_v
        self.noise_current = noise_current

        self.calc_new_tf()
        self.reset() 

    def sim_step(self, voltage, dt=0.01):
        t_span = np.array([0, dt])
        
        t_out, y_out, x_out = ct.forced_response(
            self.system,
            T=t_span,
            U=voltage,
            X0=self.x_state,
            return_x=True
        )


        self.x_state=x_out[:,-1]
        self.current_speed = y_out[-1]
        self.t += dt
        self.change_current_draw(voltage)

        speed_noise = np.random.normal(0, self.noise_speed)
        current_noise = np.random.normal(0, self.noise_current)

        noisy_speed = self.current_speed + speed_noise
        noisy_current = self.current_draw + current_noise
        
        return noisy_speed, noisy_current

    def calc_den(self):
        self.den = [ (self.L*self.J), (self.R*self.J) + (self.L*self.b), (self.R*self.b)+(self.Ke*self.Kt) ]
    def reset(self):
        self.t = 0
        self.current_speed = 0
        self.current_draw = 0
        self.x_state = np.zeros(self.system.nstates)
    def change_current_draw(self, voltage):
        self.current_draw = (voltage - self.Ke*self.current_speed) / self.R
    def calc_new_tf(self):
        num = [self.Kt]
        self.calc_den()
        tf_sys = ct.tf(num, self.den)
        self.system = ct.tf2ss(tf_sys)
