from controller import Robot

robot = Robot()
timestep = int(robot.getBasicTimeStep())

# --- SLIDER CONSTANT ---
MAX_SLIDER_POSITION = 0.120 # m
MIN_SLIDER_POSITION = 0.0
velocity_slider = 0.5

# --- ELBOW ROT CONSTANT ---
MAX_ELBOW_POSITION = 6.28 # 2pi
MIN_ELBOW_POSITION = 0.0
velocity_piston_elbow = 1.0
velocity_elbow = 1.0 

# --- LOWER ARM ROT ---
MAX_LOWER_ARM_POSITION = 1.57 # pi/2
MIN_LOWER_ARM_POSITION = -1.57
velocity_lower_arm = 1.0

# --- UPPER ARM BOX ROT ---
MAX_UPPER_ARM_BOX_POSITION = 1.57 # pi/2
MIN_UPPER_ARM_BOX_POSITION = -1.57
velocity_upper_arm_box = 1.0

# --- UPPER ARM ROT ---
MAX_UPPER_ARM_POSITION = 1.57 # pi/2
MIN_UPPER_ARM_POSITION = -1.57
velocity_upper_arm = 1.0

# --- PISTON BASE SLIDER ---
slider_piston_base = robot.getDevice("slider_piston_base")
slider_piston_base.setVelocity(velocity_slider)
ps_slider = robot.getDevice("slider_piston_base_sensor") 
ps_slider.enable(timestep)

# --- PISTON ELBOW ROT ---
piston_elbow_motor = robot.getDevice("piston_elbow_motor")
piston_elbow_motor.setVelocity(velocity_piston_elbow) 
ps_piston_elbow = robot.getDevice("piston_elbow_sensor") 
ps_piston_elbow.enable(timestep)

# --- ELBOW MOTOR ROT ---
elbow_motor = robot.getDevice("elbow_motor")
elbow_motor.setVelocity(velocity_elbow)
ps_elbow = robot.getDevice("elbow_sensor")
ps_elbow.enable(timestep)

# --- LOWER ARM MOTOR ROT ---
lower_arm_motor = robot.getDevice("lower_arm_motor")
lower_arm_motor.setVelocity(velocity_lower_arm)
ps_lower_arm = robot.getDevice("lower_arm_sensor")
ps_lower_arm.enable(timestep)

# --- UPPER ARM BOX MOTOR ROT ---
upper_arm_box_motor = robot.getDevice("upper_arm_box_motor")
upper_arm_box_motor.setVelocity(velocity_upper_arm_box)
ps_upper_arm_box = robot.getDevice("upper_arm_box_sensor")
ps_upper_arm_box.enable(timestep)

# --- UPPER ARM MOTOR ROT ---
upper_arm_motor = robot.getDevice("upper_arm_motor")
upper_arm_motor.setVelocity(velocity_upper_arm)
ps_upper_arm = robot.getDevice("upper_arm_sensor")
ps_upper_arm.enable(timestep)

# --- FUNZIONE DI ATTESA ---
def wait(duration_ms):
    start_time = robot.getTime()
    while robot.step(timestep) != -1:
        if (robot.getTime() - start_time) * 1000.0 > duration_ms:
            break

# --- SEQUENZA DI TEST ---
print("Avvio test sequenziale di mobilità completa...")

print("Testo slider...")
slider_piston_base.setPosition(MAX_SLIDER_POSITION)
wait(3000)
slider_piston_base.setPosition(MIN_SLIDER_POSITION)
wait(3000)

print("Testo pistone gomito (giro completo)...")
piston_elbow_motor.setPosition(MAX_ELBOW_POSITION) # Modificato
wait(4000) # Aumentato tempo di attesa
piston_elbow_motor.setPosition(MIN_ELBOW_POSITION)
wait(4000) # Aumentato tempo di attesa

print("Testo motore gomito (giro completo)...")
elbow_motor.setPosition(MAX_ELBOW_POSITION) # Modificato
wait(4000) # Aumentato tempo di attesa
elbow_motor.setPosition(MIN_ELBOW_POSITION)
wait(4000) # Aumentato tempo di attesa

print("Testo braccio inferiore...")
lower_arm_motor.setPosition(MAX_LOWER_ARM_POSITION)
wait(2000)
lower_arm_motor.setPosition(MIN_LOWER_ARM_POSITION)
wait(2000)
lower_arm_motor.setPosition(0.0)
wait(2000)

print("Testo scatola braccio superiore...")
upper_arm_box_motor.setPosition(MAX_UPPER_ARM_BOX_POSITION)
wait(2000)
upper_arm_box_motor.setPosition(MIN_UPPER_ARM_BOX_POSITION)
wait(2000)
upper_arm_box_motor.setPosition(0.0)
wait(2000)

print("Testo braccio superiore...")
upper_arm_motor.setPosition(MAX_UPPER_ARM_POSITION)
wait(2000)
upper_arm_motor.setPosition(MIN_UPPER_ARM_POSITION)
wait(2000)
upper_arm_motor.setPosition(0.0)
wait(2000)

print("Test completato.")

while robot.step(timestep) != -1:
    pass