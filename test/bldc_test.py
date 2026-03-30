import env.BLDC_motor as BLDC_motor
import matplotlib.pyplot as plt
import os

def bldc_test():
    motor = BLDC_motor.BLDCMotor()
    time_steps = 600
    dt = 0.001

    speeds = []
    currents = []
    time = []

    voltage_input = 12.0
    load_torque = 0.1

    for i in range(time_steps):
        speed,curr = motor.sim_step(voltage_input,load_torque,dt)
        speeds.append(speed)
        currents.append(curr)
        time.append(motor.t)

    if os.environ.get('CI'):
        print("Simulation finished. Skipping visualization.")
        return

    plt.figure(figsize=(12,5))

    plt.subplot(1,2,1)
    plt.plot(time,speeds,color='blue', label="Velocity [rad/s]")
    plt.title("Response of motor for 12V & 0.1 Nm")
    plt.xlabel("Time[s]")
    plt.ylabel("Velocity[rad/s]")
    plt.grid(True)
    plt.legend()

    plt.subplot(1,2,2)
    plt.plot(time,currents,color='red',label="Current[A]")
    plt.title("Currents of motor for 12V & 0.1 Nm")
    plt.grid(True)
    plt.xlabel("Time[s]")
    plt.ylabel("Current[A]")
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    bldc_test()
