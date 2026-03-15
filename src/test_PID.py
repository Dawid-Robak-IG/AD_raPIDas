import matplotlib.pyplot as plt
from env.BLDCmotor import BLDCMotor
from src.PIDController import PIDController

def test_pid_controller():
    dt = 0.01
    motor = BLDCMotor(noise_v=0, noise_current=0)
    pid = PIDController(kp=5.0, ki=4.0, kd=0.1,dt=dt)

    setpoint = 4.0
    seconds = 4.0
    steps = int(seconds/dt)

    history_speed = []
    history_current = []
    history_time = []
    history_setpoint = [setpoint] * steps

    for i in range(steps):
        current_v, current_i = motor.current_speed, motor.current_draw
        voltage = pid.get_action(setpoint, current_v)

        measured_speed, measured_current = motor.sim_step(voltage,dt)

        history_speed.append(measured_speed)
        history_current.append(measured_current)
        history_time.append(i*dt)

    plt.figure(figsize=(12,5))

    plt.subplot(1,2,1)
    plt.plot(history_time, history_speed, label='Motor\'s velocity')
    plt.plot(history_time, history_setpoint, 'r--', label='Setpoint velocity')
    plt.title('PID velocity regulation')
    plt.xlabel('Time[s]')
    plt.ylabel('Velocity[rad/s]')
    plt.legend()
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(history_time, history_current, color='orange', label='Current draw')
    plt.title('Current draw in time')
    plt.xlabel('Time[s]')
    plt.ylabel('Current[A]')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    test_pid_controller()