import gymnasium as gym
from gymnasium import spaces
import numpy as np
from env.BLDC_motor import BLDCMotor
from src.PID_controller import PIDController

class BLDCEnv(gym.Env):
    def __init__(self, penalty_factor_error=100, penalty_factor_current=1, penalty_factor_action=1, penalty_stall=200,reward_velocity=1000000):
        super(BLDCEnv, self).__init__()

        self.motor = BLDCMotor()
        self.dt = 0.001
        self.total_time = 20
        self.targeted_speed = 800.0
        self.load = 0.1

        self.penalty_factor_error=penalty_factor_error
        self.penalty_factor_current=penalty_factor_current
        self.penalty_factor_action = penalty_factor_action
        self.reward_velocity = reward_velocity
        self.penalty_stall=penalty_stall

        self.previous_err=0

        self.PID = PIDController(dt=self.dt)

        self.maxKp = 1.0
        self.maxTi = 100.0
        self.maxTd = 1.0

        #definicja przestrzeni akcji EJAJ
        self.action_space = spaces.Box(
            low = np.array([
                0.0, # Kp
                0.01, # Ti
                0.0  # Td
                ]).astype(np.float32),
            high = np.array([
                self.maxKp, # Kp
                self.maxTi, # Ti
                self.maxTd  # Td
            ]).astype(np.float32),
        dtype = np.float32
        )

        #definicja przestrzeni obserwacji 
        self.observation_space = spaces.Box(
            low = np.array([
                -10, # error (cel - 0)
                -10, # error_dif
                -10, # target
                -10, # velocity
                -10, # current
                0.0,    # kp
                0.01,    # Ti
                0.0     # Td
            ]).astype(np.float32),
            high = np.array([
                10, # error (cel - 0)
                10, # error_dif
                10, # target
                10, # velocity
                10, # current
                self.maxKp, # kp
                self.maxTi, # Ti
                self.maxTd  # Td
            ]).astype(np.float32),
            dtype=np.float32
        )

    #resetowanie środowiska
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.motor.reset()
        self.PID.reset()


        # !!! dzielenie /1000 żeby zapewnić zakres -10 - 10
        observation = np.array([
            self.targeted_speed/1000, # error (cel - 0)
            0.0,                 # error_dif
            self.targeted_speed/1000, # target
            0.0,                 # velocity
            0.0,                 # current
            self.PID.kp,         # aktualne Kp
            self.PID.Ti,         # aktualne Ti
            self.PID.Td          # aktualne Td
        ], dtype=np.float32)
        return observation, {}

    #krok EJAJ
    def step(self,action):
        #zastosowanie akcji EJAJ
        self.last_action=[self.PID.kp,self.PID.Ti, self.PID.Td]
        self.PID.kp,self.PID.Ti,self.PID.Td = action
        total_reward=0

        total_reward-= self.jitter_penalty(action)

        # 1 krok EJAJ = 100 kroków modelu
        for i in range(self.dt * 100000):
            voltage = self.PID.get_action(self.targeted_speed, self.motor.current_speed)

            speed,current = self.motor.sim_step(voltage,self.load,self.dt)
            error = self.targeted_speed - speed
            total_reward += self.aim_func(error,current,speed)

        # uśrednianie żeby uniknąć wielkich liczb 
        total_reward = total_reward/1000000
        #sprawdzenie czasu eksperymentu        
        terminated = self.motor.t >= self.total_time

        #wyliczanie uchybów i różnicy
        error = self.targeted_speed - speed
        err_dif=error-self.previous_err
        self.previous_err = error

        #zwracanie danych do ejaj
        # !!! dzielenie /1000 żeby zapewnić zakres -10 - 10
        obs = np.array([error/1000, err_dif/1000,self.targeted_speed/1000,speed/1000, current/100, self.PID.kp, self.PID.Ti,self.PID.Td],dtype=np.float32)
        return obs, total_reward, terminated, False, {}
    
    def jitter_penalty(self,action):
        # kara za "szarpanie" parametrami
        action_arr=np.array(action)
        last_action_arr=np.array(self.last_action)

        action_delta = np.sum(np.square(action_arr - last_action_arr))
        return self.penalty_factor_action*action_delta
    def aim_func(self, error, current, speed):
        ################ FUNKCJA CELU ####################
        total_reward = 0

        # asymetryczna kara za przekroczenie
        if error > 0:
            total_reward-=self.penalty_factor_error*pow(error,2)
        else:
            total_reward -= 10*self.penalty_factor_error*pow(error,2)

        # kara za nadmierne zużycie prądu (nie generację)
        if current>0:
            total_reward -= self.penalty_factor_current*pow(current,2)

        # kara za stall
        if abs(current) > 5.0 and speed < 0.1:
            total_reward -= self.penalty_stall # Kara za smażenie uzwojeń

        #nagroda za poprawne sterowanie
        if(error<=self.targeted_speed*0.05):
            total_reward+=self.reward_velocity

        return total_reward
