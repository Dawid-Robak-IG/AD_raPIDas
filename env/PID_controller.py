import numpy as np

class PIDController:
    def __init__(self,kp=0.15, Ti=0.3, Td=0.01,dt=0.001, out_min=-24, out_max=24):
        self.kp, self.Ti,self.Td = kp,Ti,Td
        self.out_min, self.out_max = out_min,out_max
        self.dt = dt
        self.integral = 0
        self.prev_error = 0
    def get_action(self, setpoint, measured_value):
        error = setpoint - measured_value
        self.integral += (error+self.prev_error)*0.5*self.dt # zmiana metody całkowania na trapezy
        derivative = (error-self.prev_error) / self.dt
        
        output = (self.kp * error) + np.clip((self.kp/self.Ti * self.integral), self.out_min, self.out_max) + (self.kp*self.Td*derivative) # clipowanie całki dopiero po mnożeniu

        self.prev_error = error
        return np.clip(output, self.out_min, self.out_max) # clipowanie outputu
    def reset(self):
        self.integral=0
        self.prev_error=0