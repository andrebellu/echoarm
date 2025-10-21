from controller import Robot

robot = Robot()

timestep = int(robot.getBasicTimeStep())

base_motor = robot.getDevice("base_arm_joint")
base_sensor = robot.getDevice("base_arm_joint_sensor")
arm_motor = robot.getDevice("arm_joint")
arm_sensor = robot.getDevice("arm_joint_sensor")

base_sensor.enable(timestep)
arm_sensor.enable(timestep)

base_motor.setPosition(float('inf'))
base_motor.setVelocity(0.0)
arm_motor.setPosition(float('inf'))
arm_motor.setVelocity(0.0)

base_velocity = 1.0    # rad/s
arm_velocity = 1.0     # rad/s

base_motor.setVelocity(base_velocity)
arm_motor.setVelocity(arm_velocity)

print("Avvio controller per rotazione continua...")

while robot.step(timestep) != -1:
    base_pos = base_sensor.getValue()
    arm_pos = arm_sensor.getValue()
    
    print(f"Base joint: {base_pos:.3f} rad | Arm joint: {arm_pos:.3f} rad")