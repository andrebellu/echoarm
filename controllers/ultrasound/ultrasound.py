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
    "upper_arm_split_motor",
    "probe_motor"
]

LIFT_MOTORS_INDICES = [3, 6] 

motors = {}
for name in motor_names:
    m = robot.getDevice(name)
    if m:
        m.setVelocity(1.5)
        motors[name] = m

POSE_LIBRARY = {
    "IDLE":   [0.00, 0.0, 0.0, 1.57, 1.57, 0.0, -1.57, 0.0, 0.0],
    "TORACE": [0.08, -0.8, 0.1, 0.46, 1.0, 4.5, 0.0, 0.0, 0.2],
    "ADDOME": [0.0, 1.57, 0.25, 0.31, 1.57, -0.2, 0.24, -0.7, -0.3]
}

ROBOT_BASE_X = 0.00
ROBOT_BASE_Y = -1.40

movement_timer = 0
pending_target_angles = None
pending_slider_pos = None
SAFE_LIFT_DURATION = 45

print(">>> Ready. Sequenza sicura: ALZA -> ATTENDI -> SPOSTA SLIDER + POSA.")

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
                
                print(f"\n>>> COMANDO: {body_part} (Coords: {raw_cam_x:.2f}, {raw_cam_y:.2f})")

                slider_cmd = max(-LIMIT_SLIDER, min(LIMIT_SLIDER, raw_cam_y))
                pending_slider_pos = slider_cmd
                print(f"    [Stop] Slider in attesa. Target futuro: {slider_cmd:.2f}m")

                if body_part in POSE_LIBRARY:
                    target = POSE_LIBRARY[body_part]
                else:
                    target = POSE_LIBRARY["IDLE"]
                pending_target_angles = target

                print("    [Azione] Fase 1: Sollevamento braccio (Slider fermo).")
                idle_pose = POSE_LIBRARY["IDLE"]
                
                for idx in LIFT_MOTORS_INDICES:
                    name = motor_names[idx]
                    motors[name].setPosition(idle_pose[idx])
                
                movement_timer = SAFE_LIFT_DURATION

        except Exception as e:
            print(f"ERRORE PARSING: {e}")

    if movement_timer > 0:
        movement_timer -= 1
        
        if movement_timer == 0:
            print("    [Azione] Fase 2: Spostamento Slider e Posa finale.")
            
            if slider and pending_slider_pos is not None:
                slider.setPosition(pending_slider_pos)
                pending_slider_pos = None

            if pending_target_angles is not None:
                for i, name in enumerate(motor_names):
                    valore = pending_target_angles[i]
                    motors[name].setPosition(valore)
                pending_target_angles = None