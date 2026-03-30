# Backlog of project work
- DR - Dawid Robak
- KS - Kacper Sułkowski

## Week: 2026-03-10 to 2026-03-17
- (DR) Created repo on git.
- (DR) Wrote project folders' struct, libs to use while developing project. 
- (DR) Created simple architecture of system.
- (DR) Wrote down task for first week.
- (DR) Added poetry to project
- (DR) Added class for BLDC -> math model
- (DR) Added noise for current and velocity of motor
- (DR) Added PID controller
- (DR) Added Gymnasium enviroment for BLDC motor in order to create enviroment for future agent
- (DR) Added tests for every class yet created
- (KS) Validated motor model
- (KS) Added code comments
- (KS) Added noise of motor voltage to model
- (KS) Modified reward function
- (KS) Added all observation channels to agent env
- (KS) Updated system arch diagram

## Week: 2026-03-18 to 2026-03-24
- (DR) Extracted reward func in gym env
- (DR) Created train file
- (DR) Chosen PPO algorithm for training
- (DR) Created test for model
- (DR) Added CI, changed test files for CI
- (KS) Changed PID integration method
- (KS) Added PID anti-windup clipping
- (KS) Changed PID output limit to object parameter
- (KS) Changed way of calculating ss description from tf transformation to explicite matrixes 
- (KS) Replacing calculating current draw with reading it from ss

## Week: 2026-03-25 to 2026-03-31
- (KS) Added external torque as model input
- (KS) Changed referential model parameters (2212 drone motor as reference)
- (KS) Changed PID structure from IND to ISA
- (KS) Adjusted referential PID settings
- (KS) Changed basic dt from 0.01s to 0.001s - the resolution was too low and PID bamboozled
- (KS) Changed obs and action limits, to match -10 to 10 range
- (KS) Added reward scaling (to avoid big numbers)
- (KS) Adjusted reward factors (high accuracy reward and error penalty) - after training with previous values result was highly oscilated (constant +-10%)
