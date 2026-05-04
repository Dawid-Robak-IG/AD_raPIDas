import gymnasium as gym
from gymnasium import spaces
import numpy as np
from env.BLDC_motor import BLDCMotor
from env.PID_controller import PIDController
import env.CONSTS as c
from typing import TypedDict, Optional
from dataclasses import dataclass

@dataclass
class AimFuncParams:
    penalty_factor_error: int = 10
    penalty_factor_current: int = 1
    penalty_factor_action: int = 1
    penalty_stall: int = 200
    reward_velocity: int = 100


class BLDCEnv(gym.Env):
    def __init__(self, aim_params: Optional[AimFuncParams] = None, R=c.R_NOMINAL, L=c.L_NOMINAL, b=c.b_NOMINAL):
        super(BLDCEnv, self).__init__()

        if aim_params is None:
            aim_params = AimFuncParams()
            
        self.dt = 0.001
        self.sim_steps_per_agent_step = 100
        self.motor = BLDCMotor(dt = self.dt,R=R,L=L,b=b)
        self.total_time = c.MAX_TOTAL_TIME
        self.targeted_speed = c.NOMINAL_SP
        self.sp_randomization=0
        self.steps_to_sp_change=np.random.uniform(c.MIN_SP_CHANGE_TIME,c.MAX_SP_CHANGE_TIME)
        self.load = c.NOMINAL_LOAD

        self.penalty_factor_error=aim_params.penalty_factor_error
        self.penalty_factor_current=aim_params.penalty_factor_current
        self.penalty_factor_action = aim_params.penalty_factor_action
        self.reward_velocity = aim_params.reward_velocity
        self.penalty_stall= aim_params.penalty_stall

        self.previous_err=0

        self.PID = PIDController(dt=self.dt)


        self.minKp = c.MIN_KP
        self.minTi = c.MIN_TI
        self.minTd = c.MIN_TD
        self.maxKp = c.MAX_KP
        self.maxTi = c.MAX_TI
        self.maxTd = c.MAX_TD

        #definicja przestrzeni akcji EJAJ
        # self.action_space = spaces.Box(
        #     low = np.array([
        #         0.0, # Kp
        #         0.001, # Ti
        #         0.0  # Td
        #         ]).astype(np.float32),
        #     high = np.array([
        #         self.maxKp, # Kp
        #         self.maxTi, # Ti
        #         self.maxTd  # Td
        #     ]).astype(np.float32),
        # dtype = np.float32
        # )

        # akcja %
        self.action_space = spaces.Box(
            low = np.array([
                c.MIN_ACT, # Kp
                c.MIN_ACT, # Ti
                c.MIN_ACT  # Td
                ]).astype(np.float32),
            high = np.array([
                c.MAX_ACT, # Kp
                c.MAX_ACT, # Ti
                c.MAX_ACT  # Td
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
                self.minKp,    # kp
                self.minTi,    # Ti
                self.minTd     # Td
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
    
    def obs_reset(self):
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
        
        total_reward=0
        self.last_coeffs=np.array([self.PID.kp,self.PID.Ti, self.PID.Td])


        #zastosowanie akcji EJAJ
        # self.PID.kp,self.PID.Ti,self.PID.Td = action
        self.PID.kp,self.PID.Ti,self.PID.Td = np.clip(self.last_coeffs * (np.array(action) + 1.0),
                                                       [self.minKp, self.minTi, self.minTd],
                                                       [self.maxKp, self.maxTi, self.maxTd])
        
        self.current_coeffs = np.array([self.PID.kp,self.PID.Ti,self.PID.Td])

        total_reward-= self.jitter_penalty()

        sum_sq_error_pos = 0   # dla błędu > 0
        sum_sq_error_neg = 0   # dla błędu <= 0 (overshoot)
        sum_sq_current = 0
        stall_steps = 0
        in_zone_steps = 0
        
        # 1 krok RL = 100 kroków modelu

        if(self.sp_randomization):
            if(self.steps_to_sp_change<=0):
                self.steps_to_sp_change=np.random.uniform(c.MIN_SP_CHANGE_TIME,c.MAX_SP_CHANGE_TIME)
                self.targeted_speed=np.random.uniform(c.MIN_SP,c.MAX_SP)
            self.steps_to_sp_change -=1

        for _ in range(self.sim_steps_per_agent_step):
            voltage = self.PID.get_action(self.targeted_speed, self.motor.current_speed)
            speed, current = self.motor.sim_step(voltage, self.load)
            
            error = self.targeted_speed - speed
            
            total_reward += self.aim_func(error,current,speed)


        # uśrednianie żeby uniknąć wielkich liczb 
        total_reward = total_reward/1000000000

        #print("Reward:",total_reward)

        terminated = self.motor.t >= self.total_time

        #wyliczanie uchybów i różnicy
        error = self.targeted_speed - speed
        err_dif=error-self.previous_err
        self.previous_err = error

        #zwracanie danych do ejaj
        # !!! dzielenie /1000 żeby zapewnić zakres -10 - 10
        obs = np.array([error/1000, err_dif/1000,self.targeted_speed/1000,speed/1000, current/100, self.PID.kp, self.PID.Ti,self.PID.Td],dtype=np.float32)
        return obs, total_reward, terminated, False, {}
    
    # kara za "szarpanie" parametrami
    def jitter_penalty(self):

        action_delta = np.sum(np.square(self.current_coeffs - self.last_coeffs))
        return self.penalty_factor_action*action_delta
    
    def aim_func(self, error, current, speed):
        ################ FUNKCJA CELU ####################
        total_reward = 0

        # asymetryczna kara za przekroczenie
        abs_error = abs(error)
        if error > 0:
            total_reward -= self.penalty_factor_error * abs_error*abs_error
        else:
            total_reward -= 10 * self.penalty_factor_error * abs_error*abs_error # 10x większa kara za overshoot

        # kara za nadmierne zużycie prądu (nie generację)
        if current>0:
            total_reward -= self.penalty_factor_current*current*current

        # kara za stall
        if abs(current) > 5.0 and speed < 0.1:
            total_reward -= self.penalty_stall # Kara za smażenie uzwojeń

        #nagroda za poprawne sterowanie
        if(error<=self.targeted_speed*0.05):
            total_reward+=self.reward_velocity

        return total_reward
