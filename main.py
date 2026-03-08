import math
import threading
import time
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
from state import SwingState
import texttospeech
import calculations
import phases
import os
import subprocess

# These are the lines connecting the body joints
from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarksConnections
POSE_CONNECTIONS = [(c.start, c.end) for c in PoseLandmarksConnections.POSE_LANDMARKS]


####### move all ofo this later ############
def speak_async(text):
    thread = threading.Thread(target=texttospeech.play_audio, args=(text,))
    thread.daemon = True
    thread.start()





def play_sound(text):
    thread = threading.Thread(target=lambda: os.system(f'say -r 250 "{text}"'))
    thread.daemon = True
    thread.start()
   


def set_state(state, left_wrist, left_shoulder, smoothed_cvx, smoothed_cvy):

    prev_phase = state.prev_phase
    angle = math.degrees(math.atan2(-smoothed_cvy, smoothed_cvx))
    # total speed
    speed = math.sqrt(smoothed_cvx**2 + smoothed_cvy**2)

    # direction angle in degrees (0=right, 90=up, -90=down, 180=left)
    if prev_phase == phases.Phase.BW_SWING and smoothed_cvx < 0 and speed > 150:
        phase = phases.Phase.CRUX

    elif speed > 150 and 10 < angle < 60:
        phase = phases.Phase.BW_SWING
        state.contact_fired = False

    elif speed > 150 and (angle > 120 or angle < -90):
        phase = phases.Phase.FOLLOW_THROUGH

    elif speed < 10 and left_wrist.y > left_shoulder.y:
        phase = phases.Phase.REST
        contact_fired = False
        upward_motion_seen = False

    else:
        if prev_phase in (phases.Phase.CONTACT, phases.Phase.CRUX):
            phase = phases.Phase.FOLLOW_THROUGH
        else:
            phase = prev_phase

    # angle = math.degrees(math.atan2(-smoothed_cvy, smoothed_cvx))
    # if prev_phase == phases.Phase.BW_SWING and smoothed_cvx < 0 and speed > 150:
    #     phase = phases.Phase.CRUX

    # elif speed > 100 and 10 < angle < 60:
    #     phase = phases.Phase.BW_SWING
    #     state.contact_fired = False

    # elif speed > 100 and (angle > 120 or angle < -90):
    #     phase = phases.Phase.FOLLOW_THROUGH

    # elif speed < 10 and left_wrist.y > left_shoulder.y:
    #     phase = phases.Phase.REST
    #     state.contact_fired = False


    # else:
    #     if prev_phase in (phases.Phase.CONTACT, phases.Phase.CRUX):
    #         phase = phases.Phase.FOLLOW_THROUGH
    #     else:
    #         phase = prev_phase
    


    # CONTACT: wrist was going up (vy negative), now going down (vy positive) = peak
    if (
        phase == phases.Phase.FOLLOW_THROUGH
        and prev_phase == phases.Phase.FOLLOW_THROUGH
        and not state.contact_fired
        and state.prev_smoothed_cvy < 0
        and smoothed_cvy > 0
    ):
        phase = phases.Phase.CONTACT
        state.contact_fired = True

    return phase


def print_phase(state, elbow_angle, armpit_angle, smoothed_cvx, smoothed_cvy):
    angle = math.degrees(math.atan2(-smoothed_cvy, smoothed_cvx))
    #print(f'angle: {angle}')
    match (state.current_phase):
        case phases.Phase.REST:
            print("rest")
        case phases.Phase.BW_SWING:
            print("back swing")
            
        case phases.Phase.CRUX:
            print(f'elbowangle: {elbow_angle}')
            print(f'armpitangle: {armpit_angle}')
            print("pause")
            #play_sound("pause")
        case phases.Phase.FOLLOW_THROUGH:
            print("swinging")
        case phases.Phase.CONTACT:
            print(f'elbowangle: {elbow_angle}')
            print(f'armpitangle: {armpit_angle}')
            print("contact")
            #play_sound("contact")


def get_feedback(state, move, mode, elbow_angle, armpit_angle):
    feedback = ""
    
    if state.current_phase == phases.Phase.CRUX and move == "pre hit":
        if mode == "elbow":
            if elbow_angle < 120:
                feedback = "too tight"
            elif elbow_angle < 140:
                feedback = "good"
            elif elbow_angle <= 160:
                feedback = "perfect"
            elif elbow_angle <= 172:
                feedback = "good"
            else:
                feedback = "bend arm"

        elif mode == "arm":
            if armpit_angle < 115:
                feedback = "raise arm"
            elif armpit_angle < 130:
                feedback = "good"
            elif armpit_angle <= 155:
                feedback = "perfect"
            elif armpit_angle <= 170:
                feedback = "good"
            else:
                feedback = "lower arm"

    elif state.current_phase == phases.Phase.CONTACT and move == "on hit":
        if mode == "elbow":
            if elbow_angle < 165:
                feedback = "extend arm"
            elif elbow_angle < 172:
                feedback = "good"
            elif elbow_angle <= 178:
                feedback = "perfect"
            elif elbow_angle <= 181:
                feedback = "good"
            else:
                feedback = "bend arm"

        elif mode == "arm":
            if armpit_angle < 40:
                feedback = "lift arm"
            elif armpit_angle < 52:
                feedback = "good"
            elif armpit_angle <= 72:
                feedback = "perfect"
            elif armpit_angle <= 85:
                feedback = "good"
            else:
                feedback = "lower arm"

    return feedback

def draw_angle(annotated_image, point_a, point_b, point_c, elbow_angle, w, h):

    Ax = int(point_a.x * w)
    Ay = int(point_a.y * h)

    Bx = int(point_b.x * w)
    By = int(point_b.y * h)

    Cx = int(point_c.x * w)
    Cy = int(point_c.y * h)

    angle1 = math.degrees(math.atan2(Ay - By, Ax - Bx))
    angle2 = math.degrees(math.atan2(Cy - By, Cx - Bx))

    #smaller interior arc
    diff = (angle2 - angle1) % 360
    if diff > 180:
        angle1, angle2 = angle2, angle1
        diff = (angle2 - angle1) % 360

    radius = 100

    cv2.ellipse(
        annotated_image,
        (Bx, By),               # center at elbow
        (radius, radius),       # arc size
        0,
        angle1,
        angle1 + diff,
        (255, 0, 0),         
        2
    )

    cv2.putText(
        annotated_image,
        f"{int(elbow_angle)}°",
        (Bx + 10, By - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 0, 0),
        2
    )


def handle_frame_landmarks(rgb_image, detection_result, state, move, mode, curr_velocity):

    annotated_image = np.copy(rgb_image)
    h, w = annotated_image.shape[:2]

    

    for pose_landmarks in detection_result.pose_landmarks:
        # Draw lines between joints
        for start_idx, end_idx in POSE_CONNECTIONS:
            start = pose_landmarks[start_idx]
            end = pose_landmarks[end_idx]
            
            cv2.line(annotated_image,
                (int(start.x * w), int(start.y * h)),
                (int(end.x * w), int(end.y * h)),
                (0, 255, 0), 2)
            

        # Draw dots on each joint
        for landmark in pose_landmarks:
            cv2.circle(annotated_image,
                (int(landmark.x * w), int(landmark.y * h)),
                4, (0, 0, 255), -1)

        left_elbow = pose_landmarks[13]
        left_shoulder = pose_landmarks[11]
        left_wrist = pose_landmarks[15] 
        left_hip = pose_landmarks[23] 

        elbow_angle = calculations.calculate_angle(left_shoulder, left_elbow, left_wrist)
        armpit_angle = calculations.calculate_angle(left_hip, left_shoulder, left_elbow)

        draw_angle(annotated_image, left_shoulder, left_elbow, left_wrist, elbow_angle, w, h)
        draw_angle(annotated_image, left_hip, left_shoulder, left_elbow, armpit_angle, w, h)

        
        cv2.line(annotated_image,
            (int(left_elbow.x * w), int(left_elbow.y * h)),
            (int(left_shoulder.x * w), int(left_shoulder.y * h)),
            (255, 0, 0), 2)
        cv2.line(annotated_image,
            (int(left_elbow.x * w), int(left_elbow.y * h)),
            (int(left_wrist.x * w), int(left_wrist.y * h)),
            (255, 0, 0), 2)

        # arm moving down  = positive y
        # arm moving right  = positive x
        state.velocity_history.append(curr_velocity)
        state.prev_velocity_history.append(state.prev_velocity)
        smoothed_cvx = sum(v[0] for v in state.velocity_history) / len(state.velocity_history) # it gets the vx from each tuple
        smoothed_cvy = sum(v[1] for v in state.velocity_history) / len(state.velocity_history) # it gets the vy from each tuple
        smoothed_pvx = sum(v[0] for v in state.prev_velocity_history) / len(state.prev_velocity_history) # it gets the vx from each tuple
        smoothed_pvy = sum(v[1] for v in state.prev_velocity_history) / len(state.prev_velocity_history) # it gets the vy from each tuple

       

        state.current_phase = set_state(state, left_wrist, left_shoulder, smoothed_cvx, smoothed_cvy)
        
        #print(f"speed: {speed:.2f}, prev_speed: {prev_speed:.2f}, angle: {angle:.2f}")
        print_phase(state, elbow_angle, armpit_angle, smoothed_cvx, smoothed_cvy)

        feedback = get_feedback(state, move, mode, elbow_angle, armpit_angle)

                
    

        if (state.current_phase == phases.Phase.CONTACT or state.current_phase == phases.Phase.CRUX):
            play_sound(feedback)
        
        #update current phase
        state.prev_phase = state.current_phase
        state.prev_smoothed_cvy = smoothed_cvy
                            
    return annotated_image



def main():
    state = SwingState()

    move = "on hit"
    mode = "arm"

    # Load the model
    base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
    options = vision.PoseLandmarkerOptions(base_options=base_options, num_poses=1, running_mode=vision.RunningMode.VIDEO) # curently 1 person
    detector = vision.PoseLandmarker.create_from_options(options)

    # Load image and detect
    cap = cv2.VideoCapture(0)  # 0 = default webcam
    start_time = time.time()

 
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Convert frame to mediapipe format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # timestamp to make the video continuous
        timestamp = int((time.time() - start_time) * 1000)

        # Detect and draw
        detection_result = detector.detect_for_video(mp_image, timestamp)
        
        # get current values
        if len(detection_result.pose_landmarks) > 0:
            current_wrist = detection_result.pose_landmarks[0][15]
        else:
            current_wrist = None

        current_time = time.time()

        # get prev values
        if (state.prev_wrist is None):
            state.prev_wrist = current_wrist


        # calculate velocity
        if state.prev_wrist is not None and current_wrist is not None:
            current_velocity = calculations.calculate_wrist_velocity(state.prev_wrist, current_wrist, current_time-state.prev_time, w, h)
        else:
            current_velocity = (0, 0)
        if (state.prev_velocity is None):
            state.prev_velocity = current_velocity


        annotated_frame = handle_frame_landmarks(rgb_frame, detection_result, state, move, mode, current_velocity)

        # Show
        cv2.imshow("Pose", cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR))

        

        # update prev values
        state.prev_wrist = current_wrist
        state.prev_time = current_time
        state.prev_velocity = current_velocity
        
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    main()
