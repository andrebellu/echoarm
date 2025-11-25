from controller import Robot
import numpy as np

timestep = 32
robot = Robot()
receiver = robot.getDevice('receiver')
receiver.enable(timestep)

LIMIT_SLIDER = 0.8 
slider = robot.getDevice("slider_piston_base")
if slider:
    slider.setVelocity(1.0)
    slider.setPosition(0.0)
    if hasattr(slider, 'getMaxForce'):
        slider.setAvailableForce(slider.getMaxForce())

motor_names = [
    "piston_motor",
    "elbow_motor",
    "lower_arm_rotation_motor",
    "lower_arm_vertical_motor",
    "lower_upper_arm_rotation_motor",
    "upper_arm_rotation_motor",
    "upper_arm_vertical_motor",
    "probe_motor"
]

motors = {}
for name in motor_names:
    m = robot.getDevice(name)
    if m:
        m.setVelocity(1.5)
        motors[name] = m

POSE_LIBRARY = {
    "IDLE":   [0.00, 0.0, 0.0, 1.57, 1.57, 0.0, -1.57, 0.0],
    "TORACE": [0.05, -0.6, 0.0, 0.50, 1.00, 4.5, 0.00, 0.2],
}

ROBOT_BASE_X = 0.00
ROBOT_BASE_Y = -1.40

print(">>> Ready. Default fallback: IDLE")

while robot.step(timestep) != -1:
    last_message = None
    while receiver.getQueueLength() > 0:
        last_message = receiver.getString()
        receiver.nextPacket()
    
    if last_message:
        try:
            parts = last_message.split(',')
            if len(parts) >= 4:
                body_part = parts[0]
                
                raw_cam_x, raw_cam_y = float(parts[1]), float(parts[2])
                
                print(f"\n>>> COMANDO RICEVUTO: {body_part}")


                slider_cmd = max(-LIMIT_SLIDER, min(LIMIT_SLIDER, raw_cam_y))
                
                if slider:
                    slider.setPosition(slider_cmd)
                    print(f"    Slider va a: {slider_cmd:.2f}m")

                if body_part in POSE_LIBRARY:
                    target_angles = POSE_LIBRARY[body_part]
                    print(f"    -> Posa '{body_part}' trovata. Eseguo.")
                else:
                    target_angles = POSE_LIBRARY["IDLE"]
                    print(f"    !!! Posa '{body_part}' non trovata. Vado in IDLE.")

                for i, name in enumerate(motor_names):
                    valore = target_angles[i]
                    motors[name].setPosition(valore)

        except Exception as e:
            print(f"ERRORE: {e}")