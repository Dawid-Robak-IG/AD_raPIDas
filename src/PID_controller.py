import numpy as np

class PIDController:
    def __init__(self,kp=1,ki=0,kd=0,dt=0.01):
        self.kp, self.ki,self.kd = kp,ki,kd
        self.dt = dt
        self.integral = 0
        self.prev_error = 0
    def get_action(self, setpoint, measured_value):
        error = setpoint - measured_value
        self.integral += error*self.dt
        derivative = (error-self.prev_error) / self.dt
        
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd*derivative)

        self.prev_error = error
        return np.clip(output, -24, 24) # voltage
    def reset(self):
        self.integral=0
        self.prev_error=0