from controller import Robot
import math

# --- SETUP ROBOT ---
robot = Robot()
timestep = int(robot.getBasicTimeStep())

# --- SETUP RECEIVER ---
receiver = robot.getDevice('receiver')
receiver.enable(timestep)

# --- DEFINIZIONE LIMITI MOTORI ---
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

# --- FUNZIONE DI ATTESA ---
def wait(seconds):
    start_time = robot.getTime()
    while robot.step(timestep) != -1:
        if robot.getTime() - start_time > seconds:
            break

# --- INIZIALIZZAZIONE MOTORI ---
motors = {}
motor_names = [
    "slider_piston_base",            
    "piston_motor",                  
    "rotational_motor_elbow",        
    "rotational_motor_box",          
    "rotational_motor_arm",          
    "rotational_motor_double_gear", 
    "rotational_motor_upper_arm",    
    "position_rotational_motor_probe", 
    "hingejoint"                     
]

print("--- Inizializzazione Motori ---")
for name in motor_names:
    motor = robot.getDevice(name)
    if motor:
        motor.setPosition(float('inf')) 
        motor.setVelocity(1.0) 
        motor.setPosition(0.0)
        motors[name] = motor
    else:
        print(f"ATTENZIONE: Motore {name} non trovato.")

slider = motors.get("slider_piston_base")

# --- SEQUENZA DI TEST DIAGNOSTICO ---
def run_startup_test():
    print("\n>>> AVVIO TEST DIAGNOSTICO CON LIMITI DEFINITI <<<")
    
    if "slider_piston_base" in motors:
        print(f"Test: Slider Base (Limit: +/- {LIMIT_SLIDER})")
        test_val = LIMIT_SLIDER * 0.5 
        motors["slider_piston_base"].setPosition(test_val)
        wait(2.0)
        motors["slider_piston_base"].setPosition(-test_val)
        wait(2.0)
        motors["slider_piston_base"].setPosition(0.0)
        wait(1.0)

    if "piston_motor" in motors:
        print("Test: Pistone Verticale (Target: 0.05)")
        motors["piston_motor"].setPosition(0.05)
        wait(2.0)
        motors["piston_motor"].setPosition(0.0)
        wait(1.0)

    print(f"Test: Rotazione Standard (Target: PI = {LIMIT_STD_ROTATION:.2f})")
    
    # 1. Test Gomito (Singolo)
    if "rotational_motor_elbow" in motors:
        print(f" -> Muovo rotational_motor_elbow a PI")
        motors["rotational_motor_elbow"].setPosition(LIMIT_STD_ROTATION)
        wait(3.0)
        motors["rotational_motor_elbow"].setPosition(0.0)
        wait(2.0)

    # 2. Test Braccio + Gruppo Superiore (Sincronizzati)
    # Qui muoviamo arm, box, gear e upper_arm tutti insieme
    print(f" -> Muovo rotational_motor_arm a PI (Movimento Gruppo Completo)")
    
    group_arm = [
        "rotational_motor_arm", 
        "rotational_motor_box", 
        "rotational_motor_double_gear", 
        "rotational_motor_upper_arm"
    ]

    # Andata
    for name in group_arm:
        if name in motors:
            motors[name].setPosition(LIMIT_STD_ROTATION)
    wait(3.0)

    # Ritorno
    for name in group_arm:
        if name in motors:
            motors[name].setPosition(0.0)
    wait(2.0)

    if "position_rotational_motor_probe" in motors:
        print(f"Test: Probe Rotazione Completa (Target: 2PI = {LIMIT_PROBE_ROTATION:.2f})")
        motors["position_rotational_motor_probe"].setPosition(LIMIT_PROBE_ROTATION)
        wait(4.0)
        motors["position_rotational_motor_probe"].setPosition(0.0)
        wait(2.0)

    print(">>> Reset posizione Home <<<")
    for name, motor in motors.items():
        motor.setPosition(0.0)
    wait(1.0)
    print(">>> Test completato. Attivazione Receiver. <<<\n")

# --- ESECUZIONE TEST ---
run_startup_test()

# --- MAIN LOOP (RECEIVER) ---
print("Controller in ascolto (Modalità Receiver)...")

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
                
                calculated_pos = max(-1.0, min(1.0, raw_target)) * 1.2
                
                # APPLICAZIONE LIMITE DI SICUREZZA
                limit = MOTOR_LIMITS.get("slider_piston_base", 0.8)
                
                final_target = max(-limit, min(limit, calculated_pos))

                if slider:
                    slider.setPosition(final_target)
                    print(f"RX: {target_name} | Y: {y_cam:.2f} -> Slider: {final_target:.2f} (Max: {limit})")
            
            else:
                print(f"Msg invalido: {message}")

        except Exception as e:
            print(f"Errore: {e}")