from controller import Robot, Keyboard
import cv2
import numpy as np
import mediapipe as mp
import time

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

BODY_PARTS = {
    "TESTA": [mp_pose.PoseLandmark.NOSE, mp_pose.PoseLandmark.LEFT_EYE, mp_pose.PoseLandmark.RIGHT_EYE, mp_pose.PoseLandmark.LEFT_EAR, mp_pose.PoseLandmark.RIGHT_EAR],
    "TORACE": [mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.RIGHT_SHOULDER],
    "ADDOME": [mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.RIGHT_HIP],
    "BRACCIO_SX": [mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST],
    "BRACCIO_DX": [mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST],
    "GAMBE": [mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.LEFT_ANKLE, mp_pose.PoseLandmark.RIGHT_ANKLE]
}

robot = Robot()
timestep = int(robot.getBasicTimeStep())
camera = robot.getDevice('camera')
camera.enable(timestep)
width = camera.getWidth()
height = camera.getHeight()
fov = camera.getFov()
focal_length = (width / 2) / np.tan(fov / 2)

try:
    range_finder = robot.getDevice('range-finder')
    range_finder.enable(timestep)
except:
    print("Errore: Range-finder non trovato.")

emitter = robot.getDevice('emitter') 
emitter.setChannel(1) 
keyboard = robot.getKeyboard()
keyboard.enable(timestep)

SCANNED_COORDS = {} 
scan_complete = False
scan_timer = 0
SCAN_DURATION = 50 

CROP_X_START = int(width * 0.35) 
CROP_X_END = int(width * 0.60) 
CROP_WIDTH = CROP_X_END - CROP_X_START
CROP_Y_START = 0
CROP_HEIGHT = height

cv2.namedWindow("Riconoscimento Corpo", cv2.WINDOW_NORMAL)

print(">>> AVVIO SCANSIONE PAZIENTE... RIMANI FERMO.")

def get_part_center(landmarks, part_name, roi_w, roi_h, offset_x, offset_y):
    if part_name not in BODY_PARTS: return None
    points = [landmarks[lm.value] for lm in BODY_PARTS[part_name]]
    if not all(p.visibility > 0.5 for p in points): return None
    
    u_roi = np.mean([p.x for p in points]) * roi_w
    v_roi = np.mean([p.y for p in points]) * roi_h

    u_global = int(u_roi + offset_x)
    v_global = int(v_roi + offset_y)
    return (u_global, v_global)

def calculate_3d_coords(u, v, depth_image):
    box_size = 10
    y_min = max(0, v - box_size)
    y_max = min(height, v + box_size)
    x_min = max(0, u - box_size)
    x_max = min(width, u + box_size)
    
    depth_roi = depth_image[y_min:y_max, x_min:x_max]
    valid_depths = depth_roi[depth_roi > 0.01]
    
    if valid_depths.size > 0:
        Z = np.median(valid_depths)
        if 0.1 < Z < 5.0:
            X = (u - width / 2) * Z / focal_length
            Y = (v - height / 2) * Z / focal_length
            return X, Y, Z
    return None

while robot.step(timestep) != -1:
    image_data = camera.getImage()
    depth_data = range_finder.getRangeImage()
    if not image_data or not depth_data: continue
    
    image = np.frombuffer(image_data, np.uint8).reshape((height, width, 4))
    frame_bgr = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    depth_image = np.array(depth_data, dtype=np.float32).reshape((height, width))

    frame_rgb_roi = frame_rgb[CROP_Y_START:height, CROP_X_START:CROP_X_END]
    results = pose.process(frame_rgb_roi)

    cv2.rectangle(frame_bgr, (CROP_X_START, 0), (CROP_X_END, height-2), (255, 0, 0), 2)

    if not scan_complete:
        scan_timer += 1
        cv2.putText(frame_bgr, f"SCANSIONE IN CORSO... {int(scan_timer/SCAN_DURATION*100)}%", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            for part in BODY_PARTS:
                center_2d = get_part_center(landmarks, part, CROP_WIDTH, CROP_HEIGHT, CROP_X_START, CROP_Y_START)
                if center_2d:
                    u, v = center_2d
                    coords_3d = calculate_3d_coords(u, v, depth_image)
                    if coords_3d:
                        SCANNED_COORDS[part] = {'xyz': coords_3d, 'uv': (u, v)}
                        cv2.circle(frame_bgr, (u, v), 5, (0, 255, 0), -1)

        if scan_timer > SCAN_DURATION:
            scan_complete = True
            print(">>> SCANSIONE COMPLETATA. DATI SALVATI:")
            for p, data in SCANNED_COORDS.items():
                print(f" - {p}: {data['xyz']}")
            print(">>> Premi 1-6 per inviare i comandi al robot.")

    else:
        key = keyboard.getKey()
        selected_part = None
        
        if key == ord('1'): selected_part = "TESTA"
        elif key == ord('2'): selected_part = "TORACE"
        elif key == ord('3'): selected_part = "ADDOME"
        elif key == ord('4'): selected_part = "BRACCIO_SX"
        elif key == ord('5'): selected_part = "BRACCIO_DX"
        elif key == ord('6'): selected_part = "GAMBE"
        
        for part, data in SCANNED_COORDS.items():
            u, v = data['uv']
            cv2.circle(frame_bgr, (u, v), 5, (255, 0, 0), -1)
            if part == selected_part:
                cv2.circle(frame_bgr, (u, v), 10, (0, 0, 255), -1)
                cv2.putText(frame_bgr, f"SENDING: {part}", (u+15, v), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                X, Y, Z = data['xyz']
                message = f"{part},{X:.3f},{Y:.3f},{Z:.3f}"
                emitter.send(message.encode('utf-8'))
                print(f"Inviato comando memorizzato: {message}")

        cv2.putText(frame_bgr, "MODE: MEMORY (Robot safe)", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("Riconoscimento Corpo", frame_bgr)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
pose.close()