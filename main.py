import threading
import time
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import texttospeech
import calculations

# These are the lines connecting the body joints
from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarksConnections
POSE_CONNECTIONS = [(c.start, c.end) for c in PoseLandmarksConnections.POSE_LANDMARKS]

def speak_async(text):
    thread = threading.Thread(target=texttospeech.play_audio, args=(text,))
    thread.daemon = True
    thread.start()



last_spoken = 0
def draw_landmarks_on_image(rgb_image, detection_result, current_time):
    global last_spoken
    annotated_image = np.copy(rgb_image)
    h, w = annotated_image.shape[:2]

    for pose_landmarks in detection_result.pose_landmarks:
        # Draw lines between joints
        for start_idx, end_idx in POSE_CONNECTIONS:
            start = pose_landmarks[start_idx]
            end = pose_landmarks[end_idx]
            left_elbow = pose_landmarks[13]
            left_shoulder = pose_landmarks[11]
            left_wrist = pose_landmarks[15]
            
            if (calculations.calculate_angle(left_shoulder, left_elbow, left_wrist) > 90): 
                if (current_time - last_spoken > 5):
                    speak_async("your arm is too wide")
                    last_spoken = current_time
      
                cv2.circle(annotated_image,
                    (int(left_elbow.x * w), int(left_elbow.y * h)),
                    20, (255, 0, 0), -1)
                cv2.line(annotated_image,
                    (int(left_elbow.x * w), int(left_elbow.y * h)),
                    (int(left_shoulder.x * w), int(left_shoulder.y * h)),
                    (255, 0, 0), 2)
                cv2.line(annotated_image,
                    (int(left_elbow.x * w), int(left_elbow.y * h)),
                    (int(left_wrist.x * w), int(left_wrist.y * h)),
                    (255, 0, 0), 2)
            
            cv2.line(annotated_image,
                (int(start.x * w), int(start.y * h)),
                (int(end.x * w), int(end.y * h)),
                (0, 255, 0), 2)
        # Draw dots on each joint
        for landmark in pose_landmarks:
            cv2.circle(annotated_image,
                (int(landmark.x * w), int(landmark.y * h)),
                4, (0, 0, 255), -1)
    return annotated_image

# Load the model
base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
options = vision.PoseLandmarkerOptions(base_options=base_options, num_poses=5, running_mode=vision.RunningMode.VIDEO)
detector = vision.PoseLandmarker.create_from_options(options)

# Load image and detect
cap = cv2.VideoCapture(0)  # 0 = default webcam
start_time = time.time()

# initialize prev wrist
prev_wrist = None
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    
    # Convert frame to mediapipe format
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # timestamp to make the video continuous
    timestamp = int((time.time() - start_time) * 1000)

    # Detect and draw
    detection_result = detector.detect_for_video(mp_image, timestamp)
    
    # get current wrist
    current_wrist = detection_result.pose_landmarks[15]

    annotated_frame = draw_landmarks_on_image(rgb_frame, detection_result, time.time())

    # Show
    cv2.imshow("Pose", cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR))

    # update prev wrist to current wrist
    prev_wrist = current_wrist

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


