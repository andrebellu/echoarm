import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from ikpy.chain import Chain
from ikpy.link import URDFLink
import numpy as np

print(">>> Definizione catena cinetica manuale echoarm...")

my_chain = Chain(name='echoarm', links=[
    URDFLink(
        name="piston_motor",
        origin_translation=[0,0.04,0],
        origin_orientation=[0,0,0],
        joint_type='prismatic',
        translation=[1, 0, 0],
        bounds=(0, 0.10)
    ),
    URDFLink(
        name="elbow_motor",
        origin_translation=[0,0.17,0],
        origin_orientation=[0,0,0],
        joint_type='revolute',
        rotation=[1, 0, 0],
        bounds=(-6.28,6.28)
    ),
    URDFLink(
        name="lower_arm_rotation_motor",
        origin_translation=[0,0.075,0.0736],
        origin_orientation=[0,0,0],
        joint_type='revolute',
        rotation=[0, 0, 1],
        bounds=(-6.28,6.28)
    ),
    URDFLink(
        name="lower_arm_vertical_motor",
        origin_translation=[0,0.06,0],
        origin_orientation=[0,0,0],
        joint_type='revolute',
        rotation=[1, 0, 0],
        bounds=(0.3,3.14)
    )
])

print(">>> Catena caricata senza warning!")

# Posizione iniziale (tutti a 0 tranne l'ultimo motore verticale)
initial_position = [0] * len(my_chain.links)
initial_position[3] = 1.0 

# Target locale. 
# NOTA: Ho messo un target raggiungibile. Se metti 1.2 metri, il robot (che è lungo 30cm) fallirà.
target_pos_local = [0.1, 0.3, 0.1] 

print(f">>> Calcolo IK verso: {target_pos_local}")

try:
    ik_solution = my_chain.inverse_kinematics(
        target_pos_local,
        initial_position=initial_position
    )

    print("\n>>> SOLUZIONE TROVATA (Angoli Motori):")
    
    # Mappatura indici -> nomi per chiarezza
    # Nota: In IKPy l'indice 0 è la base_link, quindi i motori partono da 1
    motor_map = {
        1: "piston_motor (m)",
        2: "elbow_motor (rad)",
        3: "lower_arm_rotation_motor (rad)",
        4: "lower_arm_vertical_motor (rad)"
    }

    for i, val in enumerate(ik_solution):
        if i in motor_map:
            print(f" - {motor_map[i]}: {val:.4f}")

    # === PLOT ===
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Plotta la catena nella configurazione trovata
    my_chain.plot(ik_solution, ax, target=target_pos_local)
    
    # Imposta limiti assi per vedere bene il robot (scala in metri)
    ax.set_xlim(-0.3, 0.3)
    ax.set_ylim(-0.1, 0.5)
    ax.set_zlim(0.0, 0.5)
    
    plt.show()

except ValueError as ve:
    print(f"\nERRORE LIMITI O CONFIGURAZIONE: {ve}")
except Exception as e:
    print(f"\nERRORE GENERICO: {e}")