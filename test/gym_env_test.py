import os
import matplotlib.pyplot as plt
from env.bldc_gym_env import BLDCEnv

def test_bldc_environment_integration():
    """
    Test if the BLDC Gym environment initializes and performs a step correctly.
    """
    # 1. Initialization (Sanity Check)
    env = BLDCEnv()
    obs, info = env.reset()
    
    # Assertions for reset state
    assert obs is not None, "Observation should not be None after reset"
    assert isinstance(info, dict), "Info should be a dictionary"

    # 2. Execution (Step Function)
    # Action format: [voltage, load_torque, dt]
    action = [5.0, 2.0, 0.1]
    obs, reward, terminated, truncated, info = env.step(action)
    
    # 3. Validation (Assertions)
    # Check if reward is a valid numerical value
    assert isinstance(reward, (int, float)), f"Expected numerical reward, got {type(reward)}"
    
    # Check if the environment returns the expected observation shape
    # Assuming obs has a specific length (e.g., 2 for speed and current)
    assert len(obs) >= 2, f"Observation vector too short: {len(obs)}"

    # Logical check: Motor should not have negative velocity for positive voltage
    # Replace index 0 with your actual velocity index in the obs vector
    assert obs[0] >= 0, f"Physical inconsistency: Negative velocity {obs[0]} for positive input"

    print(f"Integration Test Passed: Observation: {obs}, Reward: {reward}")

if __name__ == "__main__":
    test_bldc_environment_integration()