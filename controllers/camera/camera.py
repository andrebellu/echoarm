from controller import Robot
import cv2
import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=2, 
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

BODY_PARTS = {
    "TORACE": [
        mp_pose.PoseLandmark.LEFT_SHOULDER,
        mp_pose.PoseLandmark.RIGHT_SHOULDER,
        mp_pose.PoseLandmark.LEFT_HIP,
        mp_pose.PoseLandmark.RIGHT_HIP
    ],
}

def draw_body_part_box(frame, landmarks, part_name, width, height):
    if part_name not in BODY_PARTS:
        return
    points = [landmarks[lm.value] for lm in BODY_PARTS[part_name]]
    if not all(p.visibility > 0.5 for p in points):
        return
    x_min = int(min(p.x for p in points) * width)
    y_min = int(min(p.y for p in points) * height)
    x_max = int(max(p.x for p in points) * width)
    y_max = int(max(p.y for p in points) * height)
    margin = 10
    cv2.rectangle(frame, (x_min - margin, y_min - margin), (x_max + margin, y_max + margin), (0, 255, 0), 2)
    cv2.putText(frame, part_name, (x_min - margin, y_min - margin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

def get_part_center(landmarks, part_name, width, height):
    if part_name not in BODY_PARTS:
        return None
    points = [landmarks[lm.value] for lm in BODY_PARTS[part_name]]
    if not all(p.visibility > 0.5 for p in points):
        return None
    
    u = int(np.mean([p.x for p in points]) * width)
    v = int(np.mean([p.y for p in points]) * height)
    
    return (u, v)

robot = Robot()
timestep = int(robot.getBasicTimeStep())

camera = robot.getDevice('camera')
camera.enable(timestep)
width = camera.getWidth()
height = camera.getHeight()
fov = camera.getFov()

try:
    range_finder = robot.getDevice('range-finder')
    range_finder.enable(timestep)
    depth_width = range_finder.getWidth()
    depth_height = range_finder.getHeight()
except Exception as e:
    print(f"Errore: Impossibile trovare 'range-finder'. {e}")
    print("Assicurati di aver aggiunto un RangeFinder al robot in Webots.")
    robot.step(-1)

if width != depth_width or height != depth_height:
    print("Errore: Le dimensioni della camera RGB e del RangeFinder non corrispondono!")
    robot.step(-1)

focal_length = (width / 2) / np.tan(fov / 2)
print(f"Camera Info: {width}x{height}, FoV: {fov:.2f} rad, Lunghezza Focale: {focal_length:.2f} px")

cv2.namedWindow("Riconoscimento Corpo", cv2.WINDOW_NORMAL)
print("Controller avviato... Premi 'q' nella finestra per uscire.")

while robot.step(timestep) != -1:
    image_data = camera.getImage()
    depth_data = range_finder.getRangeImage()

    if not image_data or not depth_data:
        continue
    
    image = np.frombuffer(image_data, np.uint8).reshape((height, width, 4))
    frame_bgr = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    
    depth_image = np.array(depth_data, dtype=np.float32).reshape((height, width))

    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame_bgr, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        landmarks = results.pose_landmarks.landmark
        
        draw_body_part_box(frame_bgr, landmarks, "TORACE", width, height)
        
        target_2d = get_part_center(landmarks, "TORACE", width, height)
        
        if target_2d:
            u, v = target_2d
            
            cv2.circle(frame_bgr, (u, v), 10, (0, 0, 255), -1)

            box_size = 7
            half_box = box_size // 2
            
            y_min_roi = max(0, v - half_box)
            y_max_roi = min(height, v + half_box + 1)
            x_min_roi = max(0, u - half_box)
            x_max_roi = min(width, u + half_box + 1)
            
            depth_roi = depth_image[y_min_roi:y_max_roi, x_min_roi:x_max_roi]
            
            valid_depths = depth_roi[depth_roi > 0.01]
            
            if valid_depths.size > 0:
                Z = np.median(valid_depths)
            else:
                Z = 0.0
            
            if Z > 0.01 and Z < 20.0:
               
                X = (u - width / 2) * Z / focal_length
                
                Y = (v - height / 2) * Z / focal_length
                
                print(f"Target 3D Stabile (X,Y,Z): ({X: .2f}m, {Y: .2f}m, {Z: .2f}m)")
                
                coord_text = f"X:{X:.2f} Y:{Y:.2f} Z:{Z:.2f}"
                cv2.putText(frame_bgr, coord_text, (u - 50, v - 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                cv2.putText(frame_bgr, "Distanza non valida", (u - 50, v - 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0)),

    cv2.imshow("Riconoscimento Corpo", frame_bgr)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
pose.close()