import ikpy.chain
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

urdf_file = "robot.urdf"

print(f">>> Caricamento {urdf_file} (Solo Braccio)...")

try:
    # MODIFICA QUI: Cambiamo base_elements
    # Prima era ["base_link"]. 
    # Mettendo "solid", tagliamo via tutto quello che c'è prima (lo slider).
    my_chain = ikpy.chain.Chain.from_urdf_file(
        urdf_file,
        base_elements=["solid"] 
    )
except Exception as e:
    print(f"ERRORE CRITICO: {e}")
    exit()

# === VERIFICA ===
print("-" * 40)
print("Nuova Configurazione (Slider Escluso):")
# Noterai che il giunto 'slider_piston_base' NON comparirà più nella lista
for i, link in enumerate(my_chain.links):
    print(f" {i}: {link.name} ({link.joint_type})")
print("-" * 40)

# === ATTENZIONE: LE COORDINATE ORA SONO LOCALI! ===
# Se il robot è montato sullo slider, IKPy ora ragiona rispetto al carrello, non alla stanza.
# Esempio: Se vuoi toccare un punto davanti al robot, la Y target sarà vicina a 0, 
# perché hai già mosso lo slider per allinearti.

# Target relativo al carrello (Braccio piegato in avanti e in alto)
# X=0.3 (Avanti), Y=0.0 (Allineato col robot), Z=0.4 (Alto)
target_pos_local = [0.4, 0.0, 0.4] 

print(f">>> Calcolo IK Locale: {target_pos_local}")

ik_solution = my_chain.inverse_kinematics(target_pos_local)

print("\nAngoli calcolati per il Braccio:")
# Nota: l'indice degli angoli ora parte dal primo motore DEL BRACCIO
for i, angle in enumerate(ik_solution):
    # Filtriamo i link fissi per pulizia
    if my_chain.links[i].joint_type in ['revolute', 'prismatic']:
        print(f" - {my_chain.links[i].name}: {angle:.3f}")

# === PLOT ===
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
my_chain.plot(ik_solution, ax, target=target_pos_local)
ax.set_xlim(-0.5, 0.5)
ax.set_ylim(-0.5, 0.5)
ax.set_zlim(0.0, 1.0)
plt.show()