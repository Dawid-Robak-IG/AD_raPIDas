import BLDCmotor
import matplotlib.pyplot as plt

motor = BLDCmotor.BLDCMotor()
time_steps = 200
dt = 0.01

speeds = []
currents = []
time = []

voltage_input = 12.0

for i in range(time_steps):
    speed,curr = motor.sim_step(voltage_input,dt)
    speeds.append(speed)
    currents.append(curr)
    time.append(motor.t)


plt.figure(figsize=(12,5))

plt.subplot(1,2,1)
plt.plot(time,speeds,color='blue', label="Velocity [rad/s]")
plt.title("Response of motor for 12V")
plt.xlabel("Time[s]")
plt.ylabel("Velocity[rad/s]")
plt.grid(True)
plt.legend()

plt.subplot(1,2,2)
plt.plot(time,currents,color='red',label="Current[A]")
plt.title("Currents of motor for 12V")
plt.grid(True)
plt.xlabel("Time[s]")
plt.ylabel("Current[A]")
plt.legend()

plt.tight_layout()
plt.show()