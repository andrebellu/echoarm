"""my_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

motor = robot.getDevice("motor")
sensor = robot.getDevice("sensor")
motor.setVelocity(1.0)
motor.setPosition(float('inf'))
sensor.enable(timestep)


# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    position = sensor.getValue()
    if position > 0.75:
        motor.setPosition(-10.0)
    elif position < -0.75:
        motor.setPosition(10.0)


# Enter here exit cleanup code.
