from controller import Robot
import cv2
import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(static_image_mode=True, model_complexity=2, min_detection_confidence=0.5)

BODY_PARTS = {
    "TORACE": [
        mp_pose.PoseLandmark.LEFT_SHOULDER,
        mp_pose.PoseLandmark.RIGHT_SHOULDER,
        mp_pose.PoseLandmark.LEFT_HIP,
        mp_pose.PoseLandmark.RIGHT_HIP
    ],
    "GAMBA_SINISTRA": [
        mp_pose.PoseLandmark.LEFT_HIP,
        mp_pose.PoseLandmark.LEFT_KNEE,
        mp_pose.PoseLandmark.LEFT_ANKLE
    ],
    "GAMBA_DESTRA": [
        mp_pose.PoseLandmark.RIGHT_HIP,
        mp_pose.PoseLandmark.RIGHT_KNEE,
        mp_pose.PoseLandmark.RIGHT_ANKLE
    ]
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

robot = Robot()
timestep = int(robot.getBasicTimeStep())
camera = robot.getDevice('camera')
camera.enable(timestep)
width = camera.getWidth()
height = camera.getHeight()

cv2.namedWindow("Riconoscimento Corpo", cv2.WINDOW_NORMAL)
print("Controller avviato...")

while robot.step(timestep) != -1:
    image_data = camera.getImage()
    if not image_data:
        continue
    
    image = np.frombuffer(image_data, np.uint8).reshape((height, width, 4))
    frame_bgr = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame_bgr, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        landmarks = results.pose_landmarks.landmark
        draw_body_part_box(frame_bgr, landmarks, "TORACE", width, height)
        draw_body_part_box(frame_bgr, landmarks, "GAMBA_SINISTRA", width, height)
        draw_body_part_box(frame_bgr, landmarks, "GAMBA_DESTRA", width, height)


    cv2.imshow("Riconoscimento Corpo", frame_bgr)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()