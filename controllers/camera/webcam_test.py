import cv2
import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

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
    "BRACCIO_DESTRO": [
        mp_pose.PoseLandmark.RIGHT_SHOULDER,
        mp_pose.PoseLandmark.RIGHT_ELBOW,
        mp_pose.PoseLandmark.RIGHT_WRIST
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

# Il numero 0 indica la prima webcam disponibile (di solito quella integrata o la prima USB)
# Se hai più webcam, puoi provare con 1, 2, etc.
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Errore: Impossibile aprire la webcam.")
    exit()

# Impostiamo la finestra come ridimensionabile
cv2.namedWindow("Riconoscimento Corpo", cv2.WINDOW_NORMAL)
print("Webcam avviata... Premi 'q' per uscire.")

while True:
    # Leggi un frame dalla webcam
    ret, frame_bgr = cap.read()
    if not ret:
        print("Errore: Impossibile ricevere il frame dalla webcam.")
        break
    
    # Ottieni le dimensioni del frame
    height, width, _ = frame_bgr.shape
    
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame_bgr, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        landmarks = results.pose_landmarks.landmark
        draw_body_part_box(frame_bgr, landmarks, "TORACE", width, height)
        draw_body_part_box(frame_bgr, landmarks, "GAMBA_SINISTRA", width, height)
        draw_body_part_box(frame_bgr, landmarks, "BRACCIO_DESTRO", width, height)

    cv2.imshow("Riconoscimento Corpo", frame_bgr)

    # Interrompi il ciclo se viene premuto il tasto 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Script terminato.")