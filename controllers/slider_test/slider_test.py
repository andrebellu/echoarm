from controller import Robot

# --- 1. CONFIGURAZIONE SISTEMA ---
robot = Robot()
timestep = int(robot.getBasicTimeStep())

# Setup Ricevitore
receiver = robot.getDevice('receiver')
receiver.enable(timestep)

# --- 2. PARAMETRI DI SICUREZZA E POSIZIONAMENTO ---
LIMIT_SLIDER = 0.8
LIMIT_STD_ROTATION = 3.14159
LIMIT_PROBE_ROTATION = 6.28318

MOTOR_LIMITS = {
    "slider_piston_base": LIMIT_SLIDER,
    "piston_motor": 0.5,
    "rotational_motor_elbow": LIMIT_STD_ROTATION,
    "rotational_motor_box": LIMIT_STD_ROTATION,
    "rotational_motor_arm": LIMIT_STD_ROTATION,
    "rotational_motor_double_gear": LIMIT_STD_ROTATION,
    "rotational_motor_upper_arm": LIMIT_STD_ROTATION,
    "hingejoint": LIMIT_STD_ROTATION,
    "position_rotational_motor_probe": LIMIT_PROBE_ROTATION
}

# Ready Position
READY_POSITIONS = {
    "piston_motor": 0.05,
    "rotational_motor_elbow": 0.0,
    "rotational_motor_box": 0.0,
    "rotational_motor_arm": 0.2, 
    "rotational_motor_double_gear": 1.6,
    "rotational_motor_upper_arm": 0.0,
    "position_rotational_motor_probe": 1.5,
}

# Nomi dei device
motor_names = [
    "slider_piston_base",            
    "piston_motor",                  
    "rotational_motor_elbow",        
    "rotational_motor_box",          
    "rotational_motor_arm",          
    "rotational_motor_double_gear", 
    "rotational_motor_upper_arm",    
    "position_rotational_motor_probe", 
]

motors = {}

# --- 3. INIZIALIZZAZIONE MOTORI ---
print(">>> Inizializzazione Robot...")

for name in motor_names:
    motor = robot.getDevice(name)
    if motor:
        # Imposta controllo in posizione (default Webots)
        motor.setPosition(float('inf')) 
        motor.setVelocity(1.0) 
        
        # Vai alla posizione di Ready definita nel dizionario
        target_pos = READY_POSITIONS.get(name, 0.0)
        motor.setPosition(target_pos)
        
        motors[name] = motor
        print(f" - Motore {name} -> Ready: {target_pos}")
    else:
        print(f"ATTENZIONE: Motore {name} non trovato.")

slider = motors.get("slider_piston_base")

# --- 4. LOOP PRINCIPALE DI CONTROLLO ---
print(">>> Robot pronto. In attesa di coordinate...")

while robot.step(timestep) != -1:
    
    # Controlla se ci sono messaggi dalla Visione
    if receiver.getQueueLength() > 0:
        message = receiver.getString()
        receiver.nextPacket()
        
        try:
            # Parsing del messaggio: "NOME, X, Y, Z"
            parts = message.split(',')
            if len(parts) >= 4:
                target_name = parts[0]
                # x_cam = float(parts[1]) # Non usata per lo slider
                y_cam = float(parts[2])   # Coordinata Longitudinale (Lungo il lettino)
                # z_cam = float(parts[3]) # Non usata per lo slider

                raw_target = y_cam 
                
                scaled_target = raw_target * 1.2 

                limit = MOTOR_LIMITS.get("slider_piston_base", 0.8)
                final_target = max(-limit, min(limit, scaled_target))

                if slider:
                    slider.setPosition(final_target)
                    print(f"Target: {target_name} | Y_Cam: {y_cam:.2f} -> Slider: {final_target:.2f}")
            
        except ValueError:
            pass
        except Exception as e:
            print(f"Errore generico: {e}")