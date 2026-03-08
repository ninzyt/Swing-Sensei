
import streamlit as st
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
import main
import gemini_api


st.title("temp title")

move = st.selectbox("Feedback timing", ["on hit", "pre hit"])
mode = st.selectbox("Metric", ["elbow", "arm"])

if "state" not in st.session_state:
    st.session_state.state = SwingState()
if "detector" not in st.session_state:
    base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
    options = vision.PoseLandmarkerOptions(base_options=base_options, num_poses=1, running_mode=vision.RunningMode.VIDEO)
    st.session_state.detector = vision.PoseLandmarker.create_from_options(options)
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
    st.session_state.last_timestamp = 0

start_time = st.session_state.start_time

state = st.session_state.state
detector = st.session_state.detector




# Load image and detect
cap = cv2.VideoCapture(0)  # 0 = default webcam

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

if "video_holder" not in st.session_state:
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    st.session_state.video_holder = cv2.VideoWriter("session.mp4", fourcc, 30, (w, h))

video_holder = st.session_state.video_holder

frame_holder = st.empty()
stop = st.button("Stop")


while not stop:
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


    annotated_frame = main.handle_frame_landmarks(rgb_frame, detection_result, state, move, mode, current_velocity)
    # add frame to the video 
    video_holder.write(cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)) 
    
    # Show
    frame_holder.image(annotated_frame, channels="RGB", width='stretch')




    


    

    # update prev values
    state.prev_wrist = current_wrist
    state.prev_time = current_time
    state.prev_velocity = current_velocity
    
cap.release()
video_holder.release()
del st.session_state.video_holder
# gemini feedback
st.write(gemini_api.get_gemini())