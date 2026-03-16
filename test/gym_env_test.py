from env.bldc_gym_env import BLDCEnv

env = BLDCEnv()
obs, info = env.reset()
obs, reward, terminated, truncated, info = env.step([5.0,2.0,0.1])
print(f"Observation: {obs}, Reward: {reward}")