# RL Algorithms
File which describe how ceratin algorithms work or on which they relay. This documentation is for future analysis of the motor adaptive control with RL.

## Comparison of Deep Reinforcement Learning Algorithms for PID Tuning

| Feature | **PPO** (Proximal Policy Optimization) | **SAC** (Soft Actor-Critic) | **TD3** (Twin Delayed DDPG) | **DDPG** (Deep Deterministic Policy Gradient) |
|:---|:---|:---|:---|:---|
| **Policy Type** | **On-policy** | **Off-policy** | **Off-policy** | **Off-policy** |
| **Action Space** | Discrete & Continuous | Continuous | Continuous | Continuous |
| **Key Mechanism** | **Clipped Objective Function** | **Maximum Entropy RL** | **Clipped Double-Q Learning** | Deterministic Policy Gradient |
| **Stability** | **Very High** | High | High | Low (Prone to divergence) |
| **Sample Efficiency** | Moderate | **Very High** | High | High |
| **Exploration** | Stochastic (Action noise) | Entropy-based (Stochastic) | Deterministic + Added Noise | Deterministic + Added Noise |
| **Tuning Complexity** | Low (Robust to hyperparams) | Moderate | High (Many components) | Moderate |
| **Best For...** | General purpose, safety-critical systems | High-performance robotics, energy efficiency | High-precision industrial control | Historical baseline, simple continuous tasks |

## PPO (Proximal Policy Optimization) - https://spinningup.openai.com/en/latest/algorithms/ppo.html
Tries to make the biggest improvement possible without any collase. 

New policies close to old. When it sees that sth works greate it doesn't let huge change. Although its based on gradient no going to huge numbers.

For dicrete or continuous action.

There is policy and value func. Policy set for which observation what to do. Value func is a reward func.

ON-policy -> Works only on recent data. No memories.

It checks if improvement is better than what it expected. Works on advantage. When advantage is less than zero, even if val func went up it doesn't let it go. It looks for savings.

On gradient

## SAC (Soft Actor-Critic) - https://spinningup.openai.com/en/latest/algorithms/sac.html

Works on entrophy (it tries to max it). Tries not to be too predictable. Works on huge space of possible outcomes.

Off-policy -> works on errors from the past. Needs less steps to learn.

Has 2 val func (Q-functions). Always gets from less positive reward.

On gradient

## TD3 (Twin Delayed DDPG) - https://spinningup.openai.com/en/latest/algorithms/td3.html

Created for continuous work. Engineered to eliminate overdrive

Works with 2 val func. Always gets from less positive reward.

Assumes that similar actions give similar results.

Deterministic -> It add on its own noise to actions. No weird sharp edges of rewards (for perfect condition). Promotes safe and smooth actions.

Off-policy -> works on errors from the past.

delayed policy -> less frequent updates.

Extremely stable. Gives smooth results. Less twitching

On gradient

## DDPG (Deep Deterministic Policy Gradient) - https://spinningup.openai.com/en/latest/algorithms/ddpg.html

First, not very stable.

Even small changes to parameters may cause it to stop working correctly.

Deterministic

Learn to predict reward

Off Policy

Target networks -> set of its own network that update very slowly

exploration noise -> it needs noise because of deterministic behaviour. 

On gradient
