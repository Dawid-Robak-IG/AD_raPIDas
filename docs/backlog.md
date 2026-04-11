# Backlog of project work
- <span style="color: green;">(DR)</span> - Dawid Robak
- <span style="color: blue;">(KS)</span> - Kacper Sułkowski

## Week: 2026-03-10 to 2026-03-17
- <span style="color: green;">(DR)</span> Created repo on git.
- <span style="color: green;">(DR)</span> Wrote project folders' struct, libs to use while developing project. 
- <span style="color: green;">(DR)</span> Created simple architecture of system.
- <span style="color: green;">(DR)</span> Wrote down task for first week.
- <span style="color: green;">(DR)</span> Added poetry to project
- <span style="color: green;">(DR)</span> Added class for BLDC -> math model
- <span style="color: green;">(DR)</span> Added noise for current and velocity of motor
- <span style="color: green;">(DR)</span> Added PID controller
- <span style="color: green;">(DR)</span> Added Gymnasium enviroment for BLDC motor in order to create enviroment for future agent
- <span style="color: green;">(DR)</span> Added tests for every class yet created
- <span style="color: blue;">(KS)</span> Validated motor model
- <span style="color: blue;">(KS)</span> Added code comments
- <span style="color: blue;">(KS)</span> Added noise of motor voltage to model
- <span style="color: blue;">(KS)</span> Modified reward function
- <span style="color: blue;">(KS)</span> Added all observation channels to agent env
- <span style="color: blue;">(KS)</span> Updated system arch diagram

## Week: 2026-03-18 to 2026-03-24
- <span style="color: green;">(DR)</span> Extracted reward func in gym env
- <span style="color: green;">(DR)</span> Created train file
- <span style="color: green;">(DR)</span> Chosen PPO algorithm for training
- <span style="color: green;">(DR)</span> Created test for model
- <span style="color: green;">(DR)</span> Added CI, changed test files for CI
- <span style="color: blue;">(KS)</span> Changed PID integration method
- <span style="color: blue;">(KS)</span> Added PID anti-windup clipping
- <span style="color: blue;">(KS)</span> Changed PID output limit to object parameter
- <span style="color: blue;">(KS)</span> Changed way of calculating ss description from tf transformation to explicite matrixes 
- <span style="color: blue;">(KS)</span> Replacing calculating current draw with reading it from ss

## Week: 2026-03-25 to 2026-03-31
- <span style="color: blue;">(KS)</span> Added external torque as model input
- <span style="color: blue;">(KS)</span> Changed referential model parameters (2212 drone motor as reference)
- <span style="color: blue;">(KS)</span> Changed PID structure from IND to ISA
- <span style="color: blue;">(KS)</span> Adjusted referential PID settings
- <span style="color: blue;">(KS)</span> Changed basic dt from 0.01s to 0.001s - the resolution was too low and PID bamboozled
- <span style="color: blue;">(KS)</span> Changed obs and action limits, to match -10 to 10 range
- <span style="color: blue;">(KS)</span> Added reward scaling (to avoid big numbers)
- <span style="color: blue;">(KS)</span> Adjusted reward factors (high accuracy reward and error penalty) - after training with previous values result was highly oscilated (constant +-10%)
- <span style="color: green;">(DR)</span> Added colours for backlog
- <span style="color: green;">(DR)</span> Made step depend on dt in env
- <span style="color: green;">(DR)</span> Did some research about rl algorithms
- <span style="color: green;">(DR)</span> Added possibility of choosing algorithm while training or testing

## Week: 2026-04-01 to 2026-04-14
- <span style="color: green;">(DR)</span> Changed aim func to be faster in calc (sum and then calc not calc in for)
- <span style="color: green;">(DR)</span> Changed sim step to be faster in calc (changed from control force resp to discrete)
- <span style="color: green;">(DR)</span> Added way of training with dynamic SP
- <span style="color: green;">(DR)</span> Made way of training on many CPUs
- <span style="color: green;">(DR)</span> Made BOM