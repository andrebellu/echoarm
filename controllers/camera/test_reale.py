import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, model_complexity=1, min_detection_confidence=0.3)
mp_drawing = mp.solutions.drawing_utils

try:
    frame_bgr = cv2.imread("persona_reale.jpg")
    if frame_bgr is None:
        print("ERRORE: Impossibile caricare 'persona_reale.jpg'. Assicurati che sia nella cartella giusta.")
    else:
        print("Immagine 'persona_reale.jpg' caricata con successo.")
        
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        
        results = pose.process(frame_rgb)
        
        if results.pose_landmarks:
            print(f"SUCCESSO! Trovati {len(results.pose_landmarks.landmark)} landmark!")
            mp_drawing.draw_landmarks(frame_bgr, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            max_width = 1280
            height, width, _ = frame_bgr.shape

            if width > max_width:
                aspect_ratio = height / width
                new_width = max_width
                new_height = int(new_width * aspect_ratio)
                display_frame = cv2.resize(frame_bgr, (new_width, new_height))
            else:
                display_frame = frame_bgr

            cv2.imshow("Test su Immagine Reale", display_frame)
            print("Premi un tasto qualsiasi per chiudere la finestra.")
            cv2.waitKey(0)
        else:
            print("FALLIMENTO: Nessun landmark trovato nell'immagine reale.")
            
        cv2.destroyAllWindows()

except Exception as e:
    print(f"Si è verificato un errore: {e}")