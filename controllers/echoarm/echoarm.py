from controller import Robot

robot = Robot()
timestep = int(robot.getBasicTimeStep())

MAX_SLIDER_POSITION = 0.120
MIN_SLIDER_POSITION = 0.0
velocity_slider = 0.5

MAX_ELBOW_POSITION = 6.28 # 2pi
MIN_ELBOW_POSITION = 0.0
velocity_elbow = 1.0

slider_piston_base = robot.getDevice("slider_piston_base")
slider_piston_base.setPosition(float('inf'))
slider_piston_base.setVelocity(velocity_slider)
ps_slider = robot.getDevice("slider_piston_base_sensor") 
ps_slider.enable(timestep)

piston_elbow_motor = robot.getDevice("piston_elbow_motor")
piston_elbow_motor.setPosition(float('inf'))
piston_elbow_motor.setVelocity(velocity_elbow) 

ps_elbow = robot.getDevice("piston_elbow_sensor") 
ps_elbow.enable(timestep)

print("Avvio controller coordinato...")

while robot.step(timestep) != -1:
    
    current_slider_pos = ps_slider.getValue()
    
    if current_slider_pos > MAX_SLIDER_POSITION:
        slider_piston_base.setVelocity(-velocity_slider)
    elif current_slider_pos < MIN_SLIDER_POSITION:
        slider_piston_base.setVelocity(velocity_slider)

    current_elbow_pos = ps_elbow.getValue() 
    
    if current_elbow_pos > MAX_ELBOW_POSITION:
        piston_elbow_motor.setVelocity(-velocity_elbow)
    elif current_elbow_pos < MIN_ELBOW_POSITION:
        piston_elbow_motor.setVelocity(velocity_elbow)