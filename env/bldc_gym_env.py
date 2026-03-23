import gymnasium as gym
from gymnasium import spaces
import numpy as np
from env.BLDC_motor import BLDCMotor
from src.PID_controller import PIDController

class BLDCEnv(gym.Env):
    def __init__(self, penalty_factor_error=1, penalty_factor_current=1, penalty_factor_action=0.2, penalty_stall=20,reward_velocity=10):
        super(BLDCEnv, self).__init__()

        self.motor = BLDCMotor()
        self.dt = 0.01
        self.targeted_speed = 4.0

        self.penalty_factor_error=penalty_factor_error
        self.penalty_factor_current=penalty_factor_current
        self.penalty_factor_action = penalty_factor_action
        self.reward_velocity = reward_velocity
        self.penalty_stall=penalty_stall

        self.previous_err=0

        self.PID = PIDController(dt=self.dt)

        self.maxKp = 20.0
        self.maxKi = 10.0
        self.maxKd = 2.0

        #definicja przestrzeni akcji EJAJ
        self.action_space = spaces.Box(
            low = np.array([
                0.0, # Kp
                0.0, # Ki
                0.0  # Kd
                ]).astype(np.float32),
            high = np.array([
                self.maxKp, # Kp
                self.maxKi, # Ki
                self.maxKd  # Kd
            ]).astype(np.float32),
        dtype = np.float32
        )

        #definicja przestrzeni obserwacji 
        self.observation_space = spaces.Box(
            low = np.array([
                -100.0, # error (cel - 0)
                -100.0, # error_dif
                -100.0, # target
                -100.0, # velocity
                -100.0, # current
                0.0,    # Kp
                0.0,    # Ki
                0.0     # Kd
            ]).astype(np.float32),
            high = np.array([
                100.0, # error (cel - 0)
                100.0, # error_dif
                100.0, # target
                100.0, # velocity
                100.0, # current
                self.maxKp, # Kp
                self.maxKi, # Ki
                self.maxKd  # Kd
            ]).astype(np.float32),
            dtype=np.float32
        )

    #resetowanie środowiska
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.motor.reset()
        self.PID.reset()


        observation = np.array([
            self.targeted_speed, # error (cel - 0)
            0.0,                 # error_dif
            self.targeted_speed, # target
            0.0,                 # velocity
            0.0,                 # current
            self.PID.kp,         # aktualne Kp
            self.PID.ki,         # aktualne Ki
            self.PID.kd          # aktualne Kd
        ], dtype=np.float32)
        return observation, {}

    #krok EJAJ
    def step(self,action):
        #zastosowanie akcji EJAJ
        self.last_action=[self.PID.kp,self.PID.ki, self.PID.kd]
        self.PID.kp,self.PID.ki,self.PID.kd = action
        total_reward=0

        total_reward-= self.jitter_penalty(action)

        # 1 krok EJAJ = 10 kroków modelu
        for i in range(10):
            voltage = self.PID.get_action(self.targeted_speed, self.motor.current_speed)

            speed,current = self.motor.sim_step(voltage,self.dt)
            error = self.targeted_speed - speed
            total_reward += self.aim_func(error,current,speed)

        #sprawdzenie czasu eksperymentu        
        terminated = self.motor.t >= 4.0

        #wyliczanie uchybów i różnicy
        error = self.targeted_speed - speed
        err_dif=error-self.previous_err
        self.previous_err = error

        #zwracanie danych do ejaj
        obs = np.array([error, err_dif,self.targeted_speed,speed, current, self.PID.kp, self.PID.ki,self.PID.kd],dtype=np.float32)
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
            total_reward -= 1.5*self.penalty_factor_error*pow(error,2)

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
