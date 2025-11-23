from controller import Robot

# --- CONFIGURAZIONE ---
robot = Robot()
timestep = int(robot.getBasicTimeStep())

print(">>> Controller TV (Python) avviato.")

# 1. Ottieni i device
display = robot.getDevice("display")
led = robot.getDevice("led")

# 2. Accendi il LED (simula TV accesa)
if led:
    led.set(1)

# 3. CARICA L'IMMAGINE STATICA
# L'immagine deve essere nella stessa cartella di questo script python!
image_name = "body.png"
ir = None

if display:
    # Carica l'immagine in memoria
    ir = display.imageLoad(image_name)
    
    if ir:
        print(f" [OK] Immagine '{image_name}' caricata.")
        
        # Incolla l'immagine sul display alle coordinate (0,0)
        # False = non usare blending (sovrascrivi tutto)
        display.imagePaste(ir, 0, 0, False)
    else:
        print(f" [ERR] Impossibile caricare '{image_name}'. Controlla il percorso!")

# --- LOOP PRINCIPALE ---
# Anche se l'immagine è statica, il controller deve rimanere vivo
while robot.step(timestep) != -1:
    pass

# (Opzionale) Pulizia all'uscita - Python lo fa in automatico solitamente
# if display and ir:
#    display.imageDelete(ir)