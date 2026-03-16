import gymnasium as gym
from gymnasium import spaces
import numpy as np
from env.BLDC_motor import BLDCMotor
from src.PID_controller import PIDController

class BLDCEnv(gym.Env):
    def __init__(self):
        super(BLDCEnv, self).__init__()

        self.motor = BLDCMotor()
        self.dt = 0.01
        self.targeted_speed = 4.0

        self.PID = PIDController(dt=self.dt)

        self.maxKp = 20.0
        self.maxKi = 10.0
        self.maxKd = 2.0

        self.action_space = spaces.Box(
            low = np.array([0.0,0.0,0.0]).astype(np.float32),
            high = np.array([self.maxKp,self.maxKi,self.maxKd]).astype(np.float32),
            dtype = np.float32
        )

        self.observation_space = spaces.Box(
            low = np.array([-100.0,-100.0, -50.0]).astype(np.float32), # error, velocity, current
            high = np.array([100.0,100.0,50.0]).astype(np.float32),
            dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.motor.reset()
        self.PID.reset()

        observation = np.array([self.targeted_speed, 0.0, 0.0],dtype=np.float32), {}
        return observation
    

    def step(self,action):
        self.PID.kp,self.PID.ki,self.PID.kd = action
        total_reward=0

        for i in range(10):
            voltage = self.PID.get_action(self.targeted_speed, self.motor.current_speed)

            speed,current = self.motor.sim_step(voltage,self.dt)
            error = abs(self.targeted_speed - speed)
            total_reward -= (pow(error,2)*self.dt*abs(current))
        
        terminated = self.motor.t >= 4.0

        obs = np.array([self.targeted_speed - speed, speed, current],dtype=np.float32)
        return obs, total_reward, terminated, False, {}