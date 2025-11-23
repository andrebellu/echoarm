from controller import Robot, Keyboard
import cv2
import numpy as np
import mediapipe as mp

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

def draw_body_part_box(frame, landmarks, part_name, roi_w, roi_h, offset_x, offset_y, is_selected=False):
    if part_name not in BODY_PARTS: return
    points = [landmarks[lm.value] for lm in BODY_PARTS[part_name]]
    if not all(p.visibility > 0.5 for p in points): return

    x_vals_roi = [p.x * roi_w for p in points]
    y_vals_roi = [p.y * roi_h for p in points]
    
    x_min = int(min(x_vals_roi) + offset_x)
    x_max = int(max(x_vals_roi) + offset_x)
    y_min = int(min(y_vals_roi) + offset_y)
    y_max = int(max(y_vals_roi) + offset_y)
    
    margin = 10
    color = (0, 0, 255) if is_selected else (0, 255, 0)
    thickness = 3 if is_selected else 2

    cv2.rectangle(frame, (x_min - margin, y_min - margin), (x_max + margin, y_max + margin), color, thickness)
    cv2.putText(frame, part_name, (x_min - margin, y_min - margin - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

def get_part_center(landmarks, part_name, roi_w, roi_h, offset_x, offset_y):
    if part_name not in BODY_PARTS: return None
    points = [landmarks[lm.value] for lm in BODY_PARTS[part_name]]
    if not all(p.visibility > 0.5 for p in points): return None
    
    u_roi = np.mean([p.x for p in points]) * roi_w
    v_roi = np.mean([p.y for p in points]) * roi_h

    u_global = int(u_roi + offset_x)
    v_global = int(v_roi + offset_y)

    return (u_global, v_global)

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

current_selection = None 
cv2.namedWindow("Riconoscimento Corpo", cv2.WINDOW_NORMAL)

CROP_X_START = int(width * 0.35) 

CROP_X_END = int(width * 0.60) 

CROP_WIDTH = CROP_X_END - CROP_X_START
CROP_Y_START = 0
CROP_HEIGHT = height

print(f"ROI Attiva: Da pixel {CROP_X_START} a {CROP_X_END} (Totale width: {width})")

while robot.step(timestep) != -1:
    key = keyboard.getKey()
    if key == ord('1'): current_selection = "TESTA"
    elif key == ord('2'): current_selection = "TORACE"
    elif key == ord('3'): current_selection = "ADDOME"
    elif key == ord('4'): current_selection = "BRACCIO_SX"
    elif key == ord('5'): current_selection = "BRACCIO_DX"
    elif key == ord('6'): current_selection = "GAMBE"
    elif key == ord('0'): current_selection = None

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
    cv2.putText(frame_bgr, "AREA ANALISI", (CROP_X_START+10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        for part in BODY_PARTS:
            is_selected = (part == current_selection)
            draw_body_part_box(frame_bgr, landmarks, part, CROP_WIDTH, CROP_HEIGHT, CROP_X_START, CROP_Y_START, is_selected)

        if current_selection:
            target_2d = get_part_center(landmarks, current_selection, CROP_WIDTH, CROP_HEIGHT, CROP_X_START, CROP_Y_START)
            
            if target_2d:
                u, v = target_2d
                
                box_size = 10
                y_min_roi = max(0, v - box_size)
                y_max_roi = min(height, v + box_size)
                x_min_roi = max(0, u - box_size)
                x_max_roi = min(width, u + box_size)
                
                depth_roi = depth_image[y_min_roi:y_max_roi, x_min_roi:x_max_roi]
                valid_depths = depth_roi[depth_roi > 0.01]
                
                if valid_depths.size > 0:
                    Z = np.median(valid_depths)
                    
                    if 0.1 < Z < 5.0:
                        X = (u - width / 2) * Z / focal_length
                        Y = (v - height / 2) * Z / focal_length

                        message = f"{current_selection},{X:.3f},{Y:.3f},{Z:.3f}"
                        emitter.send(message.encode('utf-8'))
                        
                        cv2.circle(frame_bgr, (u, v), 8, (0, 0, 255), -1)
                        cv2.putText(frame_bgr, f"SEND: {current_selection}", (u, v-30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.imshow("Riconoscimento Corpo", frame_bgr)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
pose.close()