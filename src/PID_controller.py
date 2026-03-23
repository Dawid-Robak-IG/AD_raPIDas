import numpy as np

class PIDController:
    def __init__(self,kp=1,ki=0,kd=0,dt=0.01, out_min=-24, out_max=24):
        self.kp, self.ki,self.kd = kp,ki,kd
        self.out_min, self.out_max = out_min,out_max
        self.dt = dt
        self.integral = 0
        self.prev_error = 0
    def get_action(self, setpoint, measured_value):
        error = setpoint - measured_value
        self.integral += (error+self.prev_error)*0.5*self.dt # zmiana metody całkowania na trapezy
        self.integral = np.clip(self.integral, self.out_min, self.out_max) # clipowanie odpowiedzi całki
        derivative = (error-self.prev_error) / self.dt
        
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd*derivative)

        self.prev_error = error
        return np.clip(output, self.out_min, self.out_max) # clipowanie outputu
    def reset(self):
        self.integral=0
        self.prev_error=0