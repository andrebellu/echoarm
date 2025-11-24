from controller import Robot

robot = Robot()
timestep = int(robot.getBasicTimeStep())

receiver = robot.getDevice('receiver')
receiver.enable(timestep)

LIMIT_SLIDER = 0.8
slider_name = "slider_piston_base"
slider = robot.getDevice(slider_name)

CONFIGURAZIONE_LIMITI = {
    "slider_piston_base":        (-0.80, 0.80),
    "piston_motor":              (0.00, 0.10),
    "lower_arm_rotation_motor":  (-6.28, 6.28),
    "lower_arm_vertical_motor":  (0.30, 3.14),
    "elbow_motor":               (-6.28, 6.28)
}


print(">>> Inizializzazione Robot (Solo Slider)...")

if slider:
    slider.setVelocity(1.0)
    slider.setPosition(0.0) 
    print(f" - Motore {slider_name} -> Ready: 0.0")
else:
    print(f"ATTENZIONE: Motore {slider_name} non trovato.")

print(">>> Robot pronto. In attesa di coordinate...")

while robot.step(timestep) != -1:
    
    if receiver.getQueueLength() > 0:
        message = receiver.getString()
        receiver.nextPacket()
        
        try:
            parts = message.split(',')
            if len(parts) >= 4:
                target_name = parts[0]
                x_cam = float(parts[1]) 
                y_cam = float(parts[2])
                z_cam = float(parts[3]) 
 

                raw_target = y_cam 
                scaled_target = raw_target

                final_target = max(-LIMIT_SLIDER, min(LIMIT_SLIDER, scaled_target))

                if slider:
                    slider.setPosition(final_target)
                    print(f"Target: {target_name} | X_Cam: {x_cam:.2f} | Y_Cam: {y_cam:.2f} | Z_Cam: {z_cam:.2f} -> Slider: {final_target:.2f}")
            
        except ValueError:
            pass
        except Exception as e:
            print(f"Errore generico: {e}")