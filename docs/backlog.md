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

<table style="width: 100%; border: none;">
  <tr>
    <td align="center" style="border: none;">
      <img src="figs/first_sp_800.png" width="600px"><br>
      <b>Dynamic SP 1</b>
    </td>
  </tr>
</table>



## Week: 2026-04-01 to 2026-04-14
- <span style="color: green;">(DR)</span> Changed sim step to be faster in calc (changed from control force resp to discrete)
- <span style="color: green;">(DR)</span> Added way of training with dynamic SP
- <span style="color: green;">(DR)</span> Added way of training with dynamic LOAD
- <span style="color: green;">(DR)</span> Added way of training with dynamic PARAMS (RLb)
- <span style="color: green;">(DR)</span> Made way of training on many CPUs
- <span style="color: green;">(DR)</span> Made BOM
- <span style="color: green;">(DR)</span> Added way of training many sessions on one model
- <span style="color: green;">(DR)</span> Added program for deleting dynamic models

<table style="width: 100%; border: none;">
  <tr>
    <td align="center" style="border: none;">
      <img src="figs/with_dynamic_SP_1.png" width="600px"><br>
      <b>Dynamic SP 1</b>
    </td>
    <td align="center" style="border: none;">
      <img src="figs/with_dnyamic_LOAD_1.png" width="600px"><br>
      <b>Dynamic LOAD 1</b>
    </td>
  </tr>
  <tr>
    <td align="center" style="border: none;">
      <img src="figs/with_dynamic_PARAMS_1.png" width="600px"><br>
      <b>Dynamic PARAMS 1</b>
    </td>
    <td style="border: none;"></td>
  </tr>
</table>


## Week 2026-04-15 to 2026-04-21
- <span style="color: green;">(DR)</span> Added figs for first dynamic tests
- <span style="color: green;">(DR)</span> Train and test with different max Kp Ti Td (changed them) MAX: kp=10.o, ti = 0.5, td = 0.01
<table style="width: 100%; border: none;">
  <tr>
    <td align="center" style="border: none;">
      <img src="figs/with_dynamic_SP_2.png" width="600px"><br>
      <b>Dynamic SP 2</b>
    </td>
    <td align="center" style="border: none;">
      <img src="figs/with_dnyamic_LOAD_2.png" width="600px"><br>
      <b>Dynamic LOAD 2</b>
    </td>
  </tr>
  <tr>
    <td align="center" style="border: none;">
      <img src="figs/with_dynamic_PARAMS_2.png" width="600px"><br>
      <b>Dynamic PARAMS 2</b>
    </td>
    <td style="border: none;"></td>
  </tr>
</table>

- <span style="color: blue;">(KS)</span> Changed agent action from direct values to % change
- <span style="color: blue;">(KS)</span> Changed CONST values
- <span style="color: blue;">(KS)</span> Fixed scripts to pass tests
- <span style="color: blue;">(KS)</span> Moved PID script from src to env
- <span style="color: blue;">(KS)</span> Fixed test_rl plots
- <span style="color: blue;">(KS)</span> Added randomization to test_rl call

<table style="width: 100%; border: none;">
  <tr>
    <td align="center" style="border: none;">
      <img src="figs/KS_v3_SP.png" width="600px"><br>
      <b>Trained: dynamic SP, Run witch random SP & params</b>
    </td>
  </tr>
</table>

<table style="width: 100%; border: none;">
  <tr>
    <td align="center" style="border: none;">
      <img src="figs/KS_v3_PARAMS.png" width="600px"><br>
      <b>Trained: dynamic PARAMS, Run witch random SP & params</b>
    </td>
  </tr>
</table>

## Week 2026-04-22 to 2026-04-28
- <span style="color: green;">(DR)</span> Optimised way of training (now it doesnt save and load model constantly, it creates model,env one time, one time save)
- <span style="color: green;">(DR)</span> Added normal flags for testing (easy to choose rand sp,load,params etc.)
- <span style="color: green;">(DR)</span> Added possibility of floating SP in testing
- <span style="color: green;">(DR)</span> Added possibility of training with changing SP, PARAMS, LOAD in one time. After 1/3rd of all iteration it starts to change another thing. From start SP, then PARAMS, then LOAD
- <span style="color: green;">(DR)</span> Added function to evaluate agent controlling in changing sp environment
- <span style="color: green;">(DR)</span> Hotfix way of changing floating SP values

## Week 2026-04-29 to 2026-05-05

- <span style="color: blue;">(KS)</span> Changed test_rl call arguments (n sp changes).
- <span style="color: blue;">(KS)</span> Added randomization of sp change timestemps in test_rl.
- <span style="color: blue;">(KS)</span> Chenged test_rl plots.
- <span style="color: blue;">(KS)</span> Changed training plan - 30s runs from reset to reset
- <span style="color: blue;">(KS)</span> Fixed malfuctioning training random ranges calculation (ctr+c ctrl+v typo).
- <span style="color: blue;">(KS)</span> Changed PID gains limits.
- <span style="color: blue;">(KS)</span> Added randomized SP changes during train run. 
- <span style="color: blue;">(KS)</span> Packed env aim params into object.
- <span style="color: blue;">(KS)</span> Fixed some errors in control eval function.

## Week 2026-05-06 to 2026-05-12

- <span style="color: green;">(DR)</span> Addd optimalization for learning rate, batch size, n_steps
- <span style="color: green;">(DR)</span> Add fixed evaluation based on ITAE and stabilization