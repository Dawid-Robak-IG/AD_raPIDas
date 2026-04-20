import matplotlib.pyplot as plt
from env.BLDC_motor import BLDCMotor
from env.PID_controller import PIDController
import os

def test_pid_controller():
    dt = 0.001
    #motor = BLDCMotor(noise_w=0, noise_I=0, noise_V=0, noise_Tl=0)
    motor = BLDCMotor()
    pid = PIDController(kp=0.15, Ti=0.3, Td=0.01,dt=dt)

    setpoint = 2000.0
    load_torque = 0.05
    seconds = 10.0
    steps = int(seconds/dt)

    history_speed = []
    history_current = []
    history_time = []
    history_setpoint = [setpoint] * steps
    history_load = [load_torque] * steps
    history_voltage =[]

    for i in range(steps):
        current_v, current_i = motor.current_speed, motor.current_draw
        voltage = pid.get_action(setpoint, current_v)

        measured_speed, measured_current = motor.sim_step(voltage, load_torque)

        history_speed.append(measured_speed)
        history_current.append(measured_current)
        history_time.append(i*dt)
        history_voltage.append(voltage)
    
    if os.environ.get('CI'):
        print("Simulation finished. Skipping visualization.")
        return

    plt.figure(figsize=(12,5))

    plt.subplot(2,2,1)
    plt.plot(history_time, history_speed, label='Motor\'s velocity')
    plt.plot(history_time, history_setpoint, 'r--', label='Setpoint velocity')
    plt.title('PID velocity regulation')
    plt.xlabel('Time[s]')
    plt.ylabel('Velocity[rad/s]')
    plt.legend()
    plt.grid(True)



    plt.subplot(2, 2, 2)
    plt.plot(history_time, history_current, color='orange', label='Current draw')
    plt.title('Current draw in time')
    plt.xlabel('Time[s]')
    plt.ylabel('Current[A]')
    plt.legend()
    plt.grid(True)

    plt.subplot(2,2,3)
    plt.plot(history_time, history_voltage, 'g--', label='PID voltage')
    plt.title('PID output voltage')
    plt.xlabel('Time[s]')
    plt.ylabel('Output [V]')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    test_pid_controller()