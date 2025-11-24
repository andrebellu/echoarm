from controller import Robot
from ikpy.chain import Chain
from ikpy.link import URDFLink
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

# CATENA CINEMATICA COMPLETA - tutti i giunti fino alla probe
arm_chain = Chain(name='echoarm', links=[
    URDFLink(
        name="piston_motor",
        origin_translation=[0, 0.04, 0],
        origin_orientation=[0, 0, 0],
        joint_type='prismatic',
        translation=[0, 1, 0],
        bounds=(0.001, 0.07)
    ),
    URDFLink(
        name="elbow_motor", 
        origin_translation=[0, 0.17, 0],
        origin_orientation=[0, 0, 0],
        joint_type='revolute',
        rotation=[0, 1, 0],
        bounds=(-3.13, 3.13)
    ),
    URDFLink(
        name="lower_arm_rotation_motor",
        origin_translation=[0, 0.075, 0.0736],
        origin_orientation=[0, 0, 0],
        joint_type='revolute',
        rotation=[0, 0, 1],
        bounds=(-3.13, 3.13)
    ),
    URDFLink(
        name="lower_arm_vertical_motor",
        origin_translation=[0, 0.06, 0],
        origin_orientation=[0, 0, 0],
        joint_type='revolute',
        rotation=[1, 0, 0],
        bounds=(0.31, 3.13)
    ),
    URDFLink(
        name="upper_arm_rotation_motor",
        origin_translation=[0.41, 0.035, 0],
        origin_orientation=[0, 0, 0],
        joint_type='revolute',
        rotation=[0, 1, 0],
        bounds=(-3.13, 3.13)
    ),
    URDFLink(
        name="upper_arm_vertical_motor",
        origin_translation=[0, 0.06, 0],
        origin_orientation=[0, 0, 0],
        joint_type='revolute',
        rotation=[1, 0, 0],
        bounds=(-3.13, 3.13)
    ),
    URDFLink(
        name="probe_motor",
        origin_translation=[0.35, 0, 0],
        origin_orientation=[0, 0, 0],
        joint_type='revolute',
        rotation=[0, 1, 0],
        bounds=(-3.13, 3.13)
    ),
    URDFLink(
        name="probe_tip",
        origin_translation=[0.33, -0.0155, -0.0075],
        origin_orientation=[0, 0, 0],
        joint_type='fixed',
        bounds=(0, 0)
    )
])

# Posizione del robot nel mondo
robot_position = np.array([-0.02, -1.55, 0.83])

# Lista di tutti i motori
motor_links = [
    "piston_motor", 
    "elbow_motor", 
    "lower_arm_rotation_motor", 
    "lower_arm_vertical_motor",
    "upper_arm_rotation_motor", 
    "upper_arm_vertical_motor", 
    "probe_motor"
]

motors = {name: robot.getDevice(name) for name in motor_links}

# Posizione iniziale per tutti i 7 giunti + 1 fisso
initial_position = [0.035, 0.5, 0, 1.57, 0, 0, 0, 0]

print(">>> Configurazione catena completa:")
for i, link in enumerate(arm_chain.links):
    print(f"Link {i}: {link.name} - Tipo: {link.joint_type} - Bounds: {link.bounds}")

# Test cinematica diretta iniziale
fk_init = arm_chain.forward_kinematics(initial_position)
print(f"Posizione iniziale end-effector: {fk_init[:3, 3]}")

while robot.step(timestep) != -1:
    if receiver.getQueueLength() > 0:
        message = receiver.getString()
        receiver.nextPacket()
        parts = message.split(',')
        if len(parts) >= 4:
            body_part = parts[0]
            x_target, y_target, z_target = float(parts[1]), float(parts[2]), float(parts[3])
            
            print(f">>> Target ricevuto: {body_part} [{x_target}, {y_target}, {z_target}]")
            
            # CORREZIONE CRUCIALE: Le coordinate dalla telecamera sono nel sistema mondiale
            # ma includono l'altezza della telecamera (3.45m). Dobbiamo:
            # 1. Proiettare sul paziente (altezza ~0.94m)
            # 2. Convertire nel sistema di riferimento del robot
            
            # Altezza del paziente (dal letto)
            patient_height = 0.94
            
            # Target nel mondo: manteniamo X e Y dalla telecamera, ma usiamo l'altezza del paziente
            target_world = np.array([x_target, y_target, patient_height])
            
            # Converti target mondo in target relativo al robot
            target_relative = target_world - robot_position
            
            print(f">>> Target mondo (proiettato): {target_world}")
            print(f">>> Target relativo al robot: {target_relative}")
            
            # Verifica se il target è raggiungibile - portata aumentata per braccio completo
            target_distance = np.linalg.norm(target_relative)
            max_reach = 1.2  # Aumentato per il braccio completo
            if target_distance > max_reach:
                print(f"Target troppo lontano ({target_distance:.3f}m), ridimensiono")
                target_relative = target_relative * (max_reach / target_distance)
                print(f">>> Target ridimensionato: {target_relative}")
            
            try:
                # Calcola cinematica inversa
                joint_angles = arm_chain.inverse_kinematics(
                    target_relative,
                    initial_position=initial_position,
                    max_iter=100
                )
                
                print(f">>> Angoli giunti calcolati: {[f'{angle:.3f}' for angle in joint_angles]}")
                
                # Verifica con cinematica diretta
                fk_result = arm_chain.forward_kinematics(joint_angles)
                fk_position = fk_result[:3, 3]
                error = np.linalg.norm(target_relative - fk_position)
                print(f">>> Posizione raggiunta: {fk_position}")
                print(f">>> Errore: {error:.4f}")
                
                if error < 0.05:  # Se errore < 5cm
                    # Applica solo i primi 7 angoli (l'ultimo è per il link fisso)
                    for i, name in enumerate(motor_links):
                        if motors[name]:
                            motors[name].setPosition(joint_angles[i])
                            print(f"Motor {name}: {joint_angles[i]:.3f}")
                    initial_position = joint_angles
                    print(">>> Movimento applicato con successo")
                else:
                    print(">>> ATTENZIONE: Errore troppo alto, mantengo posizione precedente")
                
            except Exception as e:
                print(f"ERRORE IK: {e}")
                # In caso di errore, reimposta la posizione iniziale
                initial_position = [0.035, 0.5, 0, 1.57, 0, 0, 0, 0]
            
            # Controllo slider - usa la coordinata Y per movimento orizzontale
            raw_slider = float(parts[2])
            final_slider = max(-LIMIT_SLIDER, min(LIMIT_SLIDER, raw_slider))
            if slider:
                slider.setPosition(final_slider)
                print(f"Slider position: {final_slider}")
            
            print("----------------------------------------------------------------")