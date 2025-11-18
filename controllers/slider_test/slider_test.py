from controller import Robot

robot = Robot()
timestep = int(robot.getBasicTimeStep())

receiver = robot.getDevice('receiver')
receiver.enable(timestep)

slider = robot.getDevice('slider_piston_base')

slider.setVelocity(1.0) 
slider.setPosition(0.0) 

print("Controller slider pronto...")

while robot.step(timestep) != -1:
    if receiver.getQueueLength() > 0:
        message = receiver.getString()
        receiver.nextPacket()
        
        try:
            parts = message.split(',')
            target_name = parts[0]
            x_cam = float(parts[1])
            y_cam = float(parts[2])
            z_cam = float(parts[3])

            raw_target = y_cam 

            clamped_target = max(-1.0, min(1.0, raw_target)) * 1.2

            print(f"Target: {target_name} | Raw Y: {y_cam:.2f} -> Slider: {clamped_target:.2f}")

            slider.setPosition(clamped_target)

        except Exception as e:
            print(f"Errore parsing: {e}")